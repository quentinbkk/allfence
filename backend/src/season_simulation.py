"""
Season Simulation Module

This module provides functionality to simulate a full fencing season with:
- Creating multiple tournaments across different dates
- Registering fencers based on eligibility
- Generating realistic results (placements and points)
- Updating fencer rankings automatically
"""

import random
from datetime import datetime, timedelta, date
from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from .models import Season, Tournament, Fencer, TournamentResult, Ranking
from .enums import WeaponType, AgeBracket, CompetitionType, Gender
from .tournament_points import calculate_points
from .ranking import eligible_brackets, calculate_age

# Tournament configurations
COMPETITION_TYPES = [
    ('Local', 0.3),        # 30% local
    ('Regional', 0.4),     # 40% regional
    ('National', 0.2),     # 20% national
    ('Championship', 0.07), # 7% championship
    ('International', 0.03) # 3% international
]

WEAPONS = ['Sabre', 'Foil', 'Epee']
BRACKETS = ['U11', 'U13', 'U15', 'Cadet', 'Junior', 'Senior']
GENDERS = ['M', 'F', None]  # None = mixed/open


def create_season(session: Session, name: str, start_date: date, end_date: date) -> Season:
    """
    Create a new season.
    
    Args:
        session: Database session
        name: Season name (e.g., "2024-2025")
        start_date: Season start date
        end_date: Season end date
    
    Returns:
        Created Season object
    """
    season = Season(
        name=name,
        start_date=start_date,
        end_date=end_date,
        status="Active",
        description=f"Competitive season {name}"
    )
    session.add(season)
    session.commit()
    return season


def count_eligible_fencers(session: Session, weapon: str, bracket: str, gender: Optional[str], 
                          tournament_date: date) -> int:
    """Count fencers eligible for a tournament configuration."""
    all_fencers = session.query(Fencer).filter_by(weapon=weapon).all()
    count = 0
    for fencer in all_fencers:
        fencer_age = calculate_age(fencer.dob, tournament_date)
        fencer_brackets = eligible_brackets(fencer_age)
        if bracket in fencer_brackets:
            if gender is None or fencer.gender == gender:
                count += 1
    return count


def generate_random_tournaments(
    session: Session,
    season: Season,
    num_tournaments: int = 100,
    min_eligible_fencers: int = 8
) -> List[Tournament]:
    """
    Generate random tournaments throughout the season.
    Only creates tournaments with sufficient eligible fencer pool.
    
    Args:
        session: Database session
        season: Season object
        num_tournaments: Number of tournaments to generate
        min_eligible_fencers: Minimum eligible fencers needed for a tournament
    
    Returns:
        List of created Tournament objects
    """
    tournaments = []
    start = season.start_date
    end = season.end_date
    days_in_season = (end - start).days
    
    attempts = 0
    max_attempts = num_tournaments * 3  # Allow up to 3x attempts to reach target
    
    while len(tournaments) < num_tournaments and attempts < max_attempts:
        attempts += 1
        
        # Random date within season (mostly on weekends)
        days_offset = random.randint(0, days_in_season)
        tournament_date = start + timedelta(days=days_offset)
        
        # Adjust to weekend if possible (Saturday or Sunday)
        weekday = tournament_date.weekday()
        if weekday < 5:  # Monday-Friday
            # Move to next Saturday
            tournament_date += timedelta(days=(5 - weekday))
        
        # Random weapon, bracket, gender
        weapon = random.choice(WEAPONS)
        bracket = random.choice(BRACKETS)
        gender = random.choices(GENDERS, weights=[0.45, 0.45, 0.1])[0]  # Slightly more gender-specific
        
        # Check if there are enough eligible fencers
        eligible_count = count_eligible_fencers(session, weapon, bracket, gender, tournament_date)
        if eligible_count < min_eligible_fencers:
            continue  # Skip this tournament configuration
        
        # Select competition type based on weights
        comp_types, weights = zip(*COMPETITION_TYPES)
        competition_type = random.choices(comp_types, weights=weights)[0]
        
        # Set max_participants based on eligible pool and competition type
        # Ensure max_participants allows for good fill rates
        if eligible_count < 20:
            max_participants = 16
        elif eligible_count < 40:
            max_participants = random.choice([16, 32])
        elif eligible_count < 70:
            max_participants = random.choice([32, 64])
        else:
            max_participants = random.choice([32, 64, None])  # None = no limit
        
        # Generate tournament name
        location_prefixes = [
            'City', 'Metro', 'Regional', 'State', 'National',
            'North', 'South', 'East', 'West', 'Central'
        ]
        tournament_suffixes = [
            'Open', 'Championship', 'Cup', 'Classic', 'Tournament',
            'Challenge', 'Invitational', 'Grand Prix'
        ]
        
        prefix = random.choice(location_prefixes)
        suffix = random.choice(tournament_suffixes)
        tournament_name = f"{prefix} {weapon} {suffix}"
        
        # Create tournament
        tournament = Tournament(
            tournament_name=tournament_name,
            date=tournament_date,
            weapon=weapon,
            bracket=bracket,
            gender=gender,
            competition_type=competition_type,
            status="Completed",  # Mark as completed for simulation
            location=f"{prefix} Fencing Center",
            max_participants=max_participants,
            season_id=season.season_id
        )
        
        session.add(tournament)
        tournaments.append(tournament)
    
    session.commit()
    
    if len(tournaments) < num_tournaments:
        print(f"  Note: Only generated {len(tournaments)}/{num_tournaments} tournaments")
        print(f"        (Not enough eligible fencers for remaining tournaments)")
    
    return tournaments


def register_eligible_fencers(
    session: Session,
    tournament: Tournament,
    max_participants: int = None,
    min_fill_rate: float = 0.5
) -> List[Fencer]:
    """
    Register eligible fencers for a tournament.
    Ensures minimum 50% capacity to avoid poorly attended tournaments.
    
    Args:
        session: Database session
        tournament: Tournament object
        max_participants: Maximum number to register (None = all eligible)
        min_fill_rate: Minimum fill rate (default 0.5 = 50%)
    
    Returns:
        List of registered Fencer objects
    """
    # Get all fencers matching weapon
    all_fencers = session.query(Fencer).filter_by(weapon=tournament.weapon).all()
    
    eligible_fencers = []
    for fencer in all_fencers:
        # Check if fencer's age bracket matches tournament bracket
        fencer_age = calculate_age(fencer.dob, tournament.date)
        fencer_brackets = eligible_brackets(fencer_age)
        if tournament.bracket in fencer_brackets:
            # Check gender if tournament is gender-specific
            if tournament.gender is None or fencer.gender == tournament.gender:
                eligible_fencers.append(fencer)
    
    if not eligible_fencers:
        return []
    
    # More popular tournaments get more participants
    # Higher base rates to ensure good attendance
    participation_rate = {
        'Local': 0.5,          # 50% base
        'Regional': 0.65,      # 65% base
        'National': 0.75,      # 75% base
        'Championship': 0.85,  # 85% base
        'International': 0.95  # 95% base
    }
    base_rate = participation_rate.get(tournament.competition_type, 0.6)
    
    # Add randomness but ensure minimum fill rate
    # Random variance: +/- 15%
    actual_rate = base_rate + random.uniform(-0.15, 0.15)
    actual_rate = max(min_fill_rate, min(1.0, actual_rate))  # Clamp between min_fill_rate and 1.0
    
    num_to_register = int(len(eligible_fencers) * actual_rate)
    
    # If there's a max_participants limit, ensure at least min_fill_rate of capacity
    if max_participants:
        min_participants = int(max_participants * min_fill_rate)
        num_to_register = max(min_participants, min(num_to_register, max_participants))
    
    # Ensure we don't exceed available fencers
    num_to_register = min(num_to_register, len(eligible_fencers))
    
    # If we can't meet minimum fill rate, return empty (tournament should be cancelled)
    if max_participants and num_to_register < int(max_participants * min_fill_rate):
        return []
    
    registered = random.sample(eligible_fencers, num_to_register)
    return registered


def simulate_tournament_results(
    session: Session,
    tournament: Tournament,
    participants: List[Fencer]
) -> None:
    """
    Simulate tournament results for registered participants.
    
    Generates realistic placements and calculates points automatically.
    
    Args:
        session: Database session
        tournament: Tournament object
        participants: List of participating fencers
    """
    if not participants:
        return
    
    num_participants = len(participants)
    
    # Shuffle participants to randomize results
    shuffled = participants.copy()
    random.shuffle(shuffled)
    
    # Create results
    for placement, fencer in enumerate(shuffled, start=1):
        # Calculate points based on placement and competition type
        points = calculate_points(
            placement=placement,
            competition_type=tournament.competition_type
        )
        
        # Create tournament result
        result = TournamentResult(
            tournament_id=tournament.tournament_id,
            fencer_id=fencer.fencer_id,
            placement=placement,
            points_awarded=points
        )
        session.add(result)
        
        # Update fencer's ranking
        ranking = session.query(Ranking).filter_by(
            fencer_id=fencer.fencer_id,
            bracket_name=tournament.bracket
        ).first()
        
        if ranking:
            ranking.points += points
            ranking.tournaments_attended = (ranking.tournaments_attended or 0) + 1
        else:
            # Create ranking if doesn't exist
            ranking = Ranking(
                fencer_id=fencer.fencer_id,
                bracket_name=tournament.bracket,
                points=points
            )
            ranking.tournaments_attended = 1
            session.add(ranking)
    
    session.commit()


def simulate_full_season(
    session: Session,
    season_name: str,
    start_date: date,
    end_date: date,
    num_tournaments: int = 100,
    reset_rankings: bool = True
) -> Dict:
    """
    Simulate a complete season with tournaments and results.
    
    Args:
        session: Database session
        season_name: Name of the season (e.g., "2024-2025")
        start_date: Season start date
        end_date: Season end date
        num_tournaments: Number of tournaments to generate
        reset_rankings: Whether to reset all fencer rankings before simulation
    
    Returns:
        Dictionary with simulation statistics
    """
    print(f"\n{'='*60}")
    print(f"SIMULATING SEASON: {season_name}")
    print(f"{'='*60}\n")
    
    # Reset rankings if requested
    if reset_rankings:
        print("Resetting all fencer rankings...")
        rankings = session.query(Ranking).all()
        for ranking in rankings:
            ranking.points = 0
            ranking.tournaments_attended = 0
        session.commit()
        print(f"✓ Reset {len(rankings)} rankings\n")
    
    # Get or create season
    print(f"Finding season {season_name}...")
    season = session.query(Season).filter_by(name=season_name).first()
    if not season:
        print(f"Season not found, creating new season...")
        season = create_season(session, season_name, start_date, end_date)
        print(f"✓ Season created (ID: {season.season_id})\n")
    else:
        print(f"✓ Using existing season (ID: {season.season_id})\n")
    
    # Generate tournaments
    print(f"Generating {num_tournaments} tournaments...")
    tournaments = generate_random_tournaments(session, season, num_tournaments)
    print(f"✓ {len(tournaments)} tournaments created\n")
    
    # Simulate each tournament
    print("Simulating tournament results...")
    total_results = 0
    tournament_stats = []
    cancelled_tournaments = 0
    
    for i, tournament in enumerate(tournaments, 1):
        # Register participants
        participants = register_eligible_fencers(session, tournament, tournament.max_participants)
        
        if participants:
            # Simulate results
            simulate_tournament_results(session, tournament, participants)
            total_results += len(participants)
            
            # Calculate fill rate
            fill_rate = 1.0  # Default for unlimited
            if tournament.max_participants:
                fill_rate = len(participants) / tournament.max_participants
            
            tournament_stats.append({
                'name': tournament.tournament_name,
                'date': tournament.date,
                'participants': len(participants),
                'max_participants': tournament.max_participants,
                'fill_rate': fill_rate,
                'type': tournament.competition_type
            })
        else:
            # Tournament cancelled due to insufficient participants
            cancelled_tournaments += 1
            tournament.status = "Cancelled"
        
        if i % 10 == 0:
            print(f"  Progress: {i}/{len(tournaments)} tournaments processed...")
    
    print(f"✓ Simulated {total_results} tournament results")
    if cancelled_tournaments > 0:
        print(f"  ⚠ {cancelled_tournaments} tournaments cancelled (insufficient participants)\n")
    else:
        print()
    
    # Gather statistics
    completed_tournaments = [t for t in tournament_stats if t['participants'] > 0]
    avg_fill_rate = sum(t['fill_rate'] for t in completed_tournaments) / len(completed_tournaments) if completed_tournaments else 0
    
    # Calculate attendance distribution
    low_attendance = sum(1 for t in completed_tournaments if t.get('max_participants') and t['fill_rate'] < 0.5)
    medium_attendance = sum(1 for t in completed_tournaments if t.get('max_participants') and 0.5 <= t['fill_rate'] < 0.8)
    high_attendance = sum(1 for t in completed_tournaments if t.get('max_participants') and t['fill_rate'] >= 0.8)
    unlimited = sum(1 for t in completed_tournaments if not t.get('max_participants'))
    
    stats = {
        'season_id': season.season_id,
        'season_name': season_name,
        'tournaments_created': len(tournaments),
        'tournaments_completed': len(completed_tournaments),
        'tournaments_cancelled': cancelled_tournaments,
        'total_results': total_results,
        'avg_participants': total_results / len(completed_tournaments) if completed_tournaments else 0,
        'avg_fill_rate': avg_fill_rate,
        'low_attendance': low_attendance,
        'medium_attendance': medium_attendance,
        'high_attendance': high_attendance,
        'unlimited_capacity': unlimited,
        'start_date': start_date.isoformat(),
        'end_date': end_date.isoformat()
    }
    
    print(f"{'='*60}")
    print("SIMULATION COMPLETE!")
    print(f"{'='*60}")
    print(f"Season: {season_name}")
    print(f"Tournaments Created: {len(tournaments)}")
    print(f"Tournaments Completed: {len(completed_tournaments)}")
    if cancelled_tournaments > 0:
        print(f"Tournaments Cancelled: {cancelled_tournaments}")
    print(f"Total Results: {total_results}")
    print(f"Avg Participants: {stats['avg_participants']:.1f}")
    print(f"Avg Fill Rate: {avg_fill_rate:.1%}")
    print(f"\nAttendance Distribution:")
    if low_attendance > 0:
        print(f"  Low (<50%): {low_attendance}")
    print(f"  Medium (50-80%): {medium_attendance}")
    print(f"  High (≥80%): {high_attendance}")
    if unlimited > 0:
        print(f"  Unlimited capacity: {unlimited}")
    print(f"{'='*60}\n")
    
    return stats
