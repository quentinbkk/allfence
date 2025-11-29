"""
Tournament Management Module

This module provides functions for creating, managing, and recording results
for fencing tournaments. It includes validation, point calculation, and CSV import.
"""

from .database import get_session_context
from .models import Tournament, TournamentResult, Fencer, Ranking
from .tournament_points import calculate_points
from .ranking import calculate_age, eligible_brackets
from typing import Dict, List, Tuple, Optional
import pandas as pd


def create_tournament(tournament_name: str, date, weapon: str, bracket: str,
                     competition_type: str = "Regional", gender: str = None,
                     location: str = None, max_participants: int = None,
                     description: str = None, status: str = "Upcoming",
                     session=None) -> Tournament:
    """
    Create a new tournament and save it to the database.
    
    Args:
        tournament_name: Name of the tournament
        date: Date when tournament takes place (date object or string)
        weapon: Weapon discipline ("Sabre", "Foil", or "Epee")
        bracket: Age bracket ("U11", "U13", "U15", "Cadet", "Junior", "Senior")
        competition_type: Type affecting point weighting
                         ("Local", "Regional", "National", "Championship", "International")
        gender: Gender category ("M", "F", or None)
        location: Location of tournament (optional)
        max_participants: Maximum number of participants (optional)
        description: Additional notes (optional)
        status: Current status (default: "Upcoming")
        session: Optional database session (creates new if None)
    
    Returns:
        Created Tournament object
    
    Raises:
        ValueError: If any validation fails
    """
    # Validate inputs
    if weapon not in ["Sabre", "Foil", "Epee"]:
        raise ValueError(f"Invalid weapon: {weapon}. Must be Sabre, Foil, or Epee")
    
    if bracket not in ["U11", "U13", "U15", "Cadet", "Junior", "Senior"]:
        raise ValueError(f"Invalid bracket: {bracket}")
    
    if competition_type not in ["Local", "Regional", "National", "Championship", "International"]:
        raise ValueError(f"Invalid competition_type: {competition_type}")
    
    if gender and gender not in ["M", "F"]:
        raise ValueError(f"Invalid gender: {gender}. Must be M, F, or None")
    
    # Create tournament
    tournament = Tournament(
        tournament_name=tournament_name,
        date=date,
        weapon=weapon,
        bracket=bracket,
        competition_type=competition_type,
        gender=gender,
        location=location,
        max_participants=max_participants,
        description=description,
        status=status
    )
    
    # Save to database
    if session is None:
        with get_session_context() as session:
            session.add(tournament)
            session.commit()
            session.refresh(tournament)
            return tournament
    else:
        session.add(tournament)
        session.flush()  # Get the ID without committing
        return tournament


def register_fencer_for_tournament(fencer_id: int, tournament_id: int,
                                   session=None) -> Tuple[bool, str]:
    """
    Register a fencer for a tournament.
    
    Validates eligibility before registering:
    - Weapon match
    - Bracket match
    - Gender match (if specified)
    - Tournament not full
    - Tournament accepts registrations
    
    Args:
        fencer_id: ID of the fencer to register
        tournament_id: ID of the tournament
        session: Optional database session
    
    Returns:
        Tuple (success: bool, message: str)
    """
    if session is None:
        with get_session_context() as session:
            return _register_fencer_impl(fencer_id, tournament_id, session)
    else:
        return _register_fencer_impl(fencer_id, tournament_id, session)


def _register_fencer_impl(fencer_id: int, tournament_id: int, session) -> Tuple[bool, str]:
    """Internal implementation of fencer registration."""
    # Get tournament
    tournament = session.query(Tournament).filter_by(tournament_id=tournament_id).first()
    if not tournament:
        return False, f"Tournament {tournament_id} not found"
    
    # Get fencer
    fencer = session.query(Fencer).filter_by(fencer_id=fencer_id).first()
    if not fencer:
        return False, f"Fencer {fencer_id} not found"
    
    # Check if already registered
    existing_result = session.query(TournamentResult).filter_by(
        tournament_id=tournament_id,
        fencer_id=fencer_id
    ).first()
    
    if existing_result:
        return False, f"Fencer {fencer_id} is already registered for this tournament"
    
    # Check eligibility
    is_eligible, reason = tournament.is_eligible_fencer(fencer)
    if not is_eligible:
        return False, reason
    
    # Register fencer (create result with placement 0 as placeholder)
    result = TournamentResult(
        tournament_id=tournament_id,
        fencer_id=fencer_id,
        placement=0,  # Will be updated when results are recorded
        points_awarded=0
    )
    session.add(result)
    session.commit()
    
    return True, f"Fencer {fencer_id} successfully registered"


def record_tournament_results(tournament_id: int, results_dict: Dict[int, int],
                              session=None) -> Tuple[bool, str]:
    """
    Record tournament results and automatically update fencer rankings.
    
    Args:
        tournament_id: ID of the tournament
        results_dict: Dictionary mapping fencer_id to placement
                     Format: {fencer_id: placement, ...}
                     Example: {101: 1, 102: 2, 103: 3}
        session: Optional database session
    
    Returns:
        Tuple (success: bool, message: str)
    """
    if session is None:
        with get_session_context() as session:
            return _record_results_impl(tournament_id, results_dict, session)
    else:
        return _record_results_impl(tournament_id, results_dict, session)


def _record_results_impl(tournament_id: int, results_dict: Dict[int, int], session) -> Tuple[bool, str]:
    """Internal implementation of recording results."""
    # Get tournament
    tournament = session.query(Tournament).filter_by(tournament_id=tournament_id).first()
    if not tournament:
        return False, f"Tournament {tournament_id} not found"
    
    # Validate tournament status
    if tournament.status not in ["In Progress", "Completed"]:
        return False, f"Tournament status is {tournament.status}. Cannot record results."
    
    # Get all registered participants
    registered_results = session.query(TournamentResult).filter_by(
        tournament_id=tournament_id
    ).all()
    
    registered_fencer_ids = {r.fencer_id for r in registered_results}
    provided_fencer_ids = set(results_dict.keys())
    
    # Validate all registered fencers have results
    if registered_fencer_ids != provided_fencer_ids:
        missing = registered_fencer_ids - provided_fencer_ids
        extra = provided_fencer_ids - registered_fencer_ids
        msg = ""
        if missing:
            msg += f"Missing results for fencers: {missing}. "
        if extra:
            msg += f"Extra fencers not registered: {extra}."
        return False, msg
    
    # Validate placements are unique
    placements = list(results_dict.values())
    if len(placements) != len(set(placements)):
        return False, "Duplicate placements found. Each fencer must have a unique placement."
    
    # Update results and calculate points
    for fencer_id, placement in results_dict.items():
        # Find the result record
        result = next((r for r in registered_results if r.fencer_id == fencer_id), None)
        if not result:
            continue
        
        # Calculate points based on placement and competition type
        points = calculate_points(placement, tournament.competition_type)
        
        # Update result
        result.placement = placement
        result.points_awarded = points
        
        # Update fencer's ranking
        fencer = session.query(Fencer).filter_by(fencer_id=fencer_id).first()
        if fencer and fencer.rankings:
            ranking = fencer.rankings[0]  # Each fencer has one ranking
            ranking.update_ranking(points)
    
    # Mark tournament as completed
    tournament.status = "Completed"
    
    # Commit all changes
    session.commit()
    
    return True, f"Results recorded successfully. {len(results_dict)} fencers updated."


def import_tournament_results_from_csv(csv_file: str, tournament_id: int = None,
                                      session=None) -> Tuple[bool, str, int]:
    """
    Import tournament results from a CSV file.
    
    CSV file format:
        fencer_id,placement
        70196,1
        54354,2
        20871,3
        ...
    
    OR with additional columns:
        fencer_id,placement,pool_record,seeding
        70196,1,5-0,1
        54354,2,4-1,2
        ...
    
    Args:
        csv_file: Path to CSV file containing results
        tournament_id: ID of existing tournament (if None, tournament will be created from CSV metadata)
        session: Optional database session
    
    Returns:
        Tuple (success: bool, message: str, tournament_id: int)
    """
    if session is None:
        with get_session_context() as session:
            return _import_results_impl(csv_file, tournament_id, session)
    else:
        return _import_results_impl(csv_file, tournament_id, session)


def _import_results_impl(csv_file: str, tournament_id: int = None, session=None) -> Tuple[bool, str, int]:
    """Internal implementation of CSV import."""
    try:
        # Read CSV file
        df = pd.read_csv(csv_file)
        
        # Validate required columns
        if 'fencer_id' not in df.columns or 'placement' not in df.columns:
            return False, "CSV must contain 'fencer_id' and 'placement' columns", 0
        
        # If tournament_id not provided, check if CSV has tournament metadata
        if tournament_id is None:
            # Try to get tournament info from CSV columns or create default
            tournament_name = df.get('tournament_name', ['Imported Tournament']).iloc[0] if 'tournament_name' in df.columns else "Imported Tournament"
            date_str = df.get('date', [pd.Timestamp.today()]).iloc[0] if 'date' in df.columns else pd.Timestamp.today()
            weapon = df.get('weapon', ['Foil']).iloc[0] if 'weapon' in df.columns else "Foil"
            bracket = df.get('bracket', ['Senior']).iloc[0] if 'bracket' in df.columns else "Senior"
            competition_type = df.get('competition_type', ['Regional']).iloc[0] if 'competition_type' in df.columns else "Regional"
            
            tournament = create_tournament(
                tournament_name=tournament_name,
                date=date_str,
                weapon=weapon,
                bracket=bracket,
                competition_type=competition_type,
                status="Completed",  # Assume completed if importing results
                session=session
            )
            tournament_id = tournament.tournament_id
        else:
            # Verify tournament exists
            tournament = session.query(Tournament).filter_by(tournament_id=tournament_id).first()
            if not tournament:
                return False, f"Tournament {tournament_id} not found", 0
        
        # Build results dictionary
        results_dict = {}
        for _, row in df.iterrows():
            fencer_id = int(row['fencer_id'])
            placement = int(row['placement'])
            results_dict[fencer_id] = placement
        
        # First, register all fencers (if not already registered)
        for fencer_id in results_dict.keys():
            existing_result = session.query(TournamentResult).filter_by(
                tournament_id=tournament_id,
                fencer_id=fencer_id
            ).first()
            
            if not existing_result:
                # Register fencer (will validate eligibility)
                success, msg = _register_fencer_impl(fencer_id, tournament_id, session)
                if not success:
                    # If registration fails, log warning but continue
                    print(f"Warning: Could not register fencer {fencer_id}: {msg}")
        
        # Set tournament status to "In Progress" so we can record results
        tournament.status = "In Progress"
        session.commit()
        
        # Record results (this will also update rankings)
        success, message = _record_results_impl(tournament_id, results_dict, session)
        
        if success:
            return True, f"Successfully imported {len(results_dict)} results from CSV", tournament_id
        else:
            return False, f"Error recording results: {message}", tournament_id
            
    except FileNotFoundError:
        return False, f"CSV file not found: {csv_file}", 0
    except Exception as e:
        return False, f"Error importing CSV: {str(e)}", 0


def get_tournament_participants(tournament_id: int, session=None) -> List[Fencer]:
    """
    Get list of fencers registered for a tournament.
    
    Args:
        tournament_id: ID of the tournament
        session: Optional database session
    
    Returns:
        List of Fencer objects
    """
    if session is None:
        with get_session_context() as session:
            return _get_participants_impl(tournament_id, session)
    else:
        return _get_participants_impl(tournament_id, session)


def _get_participants_impl(tournament_id: int, session) -> List[Fencer]:
    """Internal implementation of getting participants."""
    results = session.query(TournamentResult).filter_by(tournament_id=tournament_id).all()
    fencer_ids = [r.fencer_id for r in results]
    fencers = session.query(Fencer).filter(Fencer.fencer_id.in_(fencer_ids)).all()
    return fencers


def get_tournament_results(tournament_id: int, session=None) -> List[TournamentResult]:
    """
    Get tournament results sorted by placement.
    
    Args:
        tournament_id: ID of the tournament
        session: Optional database session
    
    Returns:
        List of TournamentResult objects sorted by placement (1st, 2nd, 3rd, etc.)
    """
    if session is None:
        with get_session_context() as session:
            return _get_results_impl(tournament_id, session)
    else:
        return _get_results_impl(tournament_id, session)


def _get_results_impl(tournament_id: int, session) -> List[TournamentResult]:
    """Internal implementation of getting results."""
    results = session.query(TournamentResult).filter_by(
        tournament_id=tournament_id
    ).order_by(TournamentResult.placement.asc()).all()
    return results
