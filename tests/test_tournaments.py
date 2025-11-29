"""
Test Suite for Tournament System

This script tests tournament creation, registration, results recording,
and CSV import functionality.
"""

import sys
import os

# Add parent directory to path so we can import src
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.database import get_session_context, init_db
from src.models import Tournament, TournamentResult, Fencer, Ranking
from src.tournament_management import (
    create_tournament, register_fencer_for_tournament, record_tournament_results,
    import_tournament_results_from_csv, get_tournament_participants, get_tournament_results
)
from src.tournament_points import calculate_points, print_point_structure, get_point_structure
import pandas as pd


def test_point_calculation():
    """
    Test the point calculation system with different competition types.
    """
    print("\n" + "="*60)
    print("Testing Point Calculation System")
    print("="*60)
    
    print("\n1. Testing base points by placement:")
    print(f"   1st place: {calculate_points(1, 'Regional')} pts")
    print(f"   2nd place: {calculate_points(2, 'Regional')} pts")
    print(f"   3rd place: {calculate_points(3, 'Regional')} pts")
    print(f"   5th place: {calculate_points(5, 'Regional')} pts")
    
    print("\n2. Testing competition type multipliers:")
    placements = [1, 2, 3, 5]
    competition_types = ["Local", "Regional", "National", "Championship", "International"]
    
    print(f"\n   {'Placement':<12}", end="")
    for ct in competition_types:
        print(f"{ct:<15}", end="")
    print()
    print("-" * 90)
    
    for placement in placements:
        print(f"   {placement}{'th':<10}", end="")
        for ct in competition_types:
            points = calculate_points(placement, ct)
            print(f"{points:<15}", end="")
        print()
    
    print("\n3. Displaying point structure for Championship competitions:")
    print_point_structure("Championship")


def test_tournament_creation():
    """
    Test creating tournaments with different competition types.
    """
    print("\n" + "="*60)
    print("Testing Tournament Creation")
    print("="*60)
    
    with get_session_context() as session:
        # Create a Regional tournament
        tournament1 = create_tournament(
            tournament_name="Spring Regional Open",
            date=pd.Timestamp('2024-04-15'),
            weapon="Foil",
            bracket="Senior",
            competition_type="Regional",
            location="City Sports Center",
            status="Registration Open",
            session=session
        )
        session.commit()
        print(f"\n✓ Created tournament: {tournament1}")
        print(f"  Tournament ID: {tournament1.tournament_id}")
        
        # Create a Championship tournament
        tournament2 = create_tournament(
            tournament_name="National Championships",
            date=pd.Timestamp('2024-06-20'),
            weapon="Sabre",
            bracket="Senior",
            competition_type="Championship",
            location="National Arena",
            status="Upcoming",
            max_participants=64,
            session=session
        )
        session.commit()
        print(f"\n✓ Created tournament: {tournament2}")
        print(f"  Tournament ID: {tournament2.tournament_id}")
        print(f"  Max participants: {tournament2.max_participants}")
        
        # Test tournament methods
        print(f"\n✓ Tournament full? {tournament2.is_full()}")
        print(f"  Participant count: {tournament2.get_participant_count()}")


def test_fencer_registration():
    """
    Test registering fencers for tournaments.
    """
    print("\n" + "="*60)
    print("Testing Fencer Registration")
    print("="*60)
    
    with get_session_context() as session:
        # Get a tournament
        tournament = session.query(Tournament).first()
        if not tournament:
            print("\n✗ No tournaments found. Run test_tournament_creation first.")
            return
        
        # Get some fencers that match the tournament criteria
        matching_fencers = session.query(Fencer).filter_by(
            weapon=tournament.weapon
        ).limit(5).all()
        
        if not matching_fencers:
            print(f"\n✗ No fencers found matching tournament weapon ({tournament.weapon})")
            return
        
        print(f"\nTournament: {tournament.tournament_name}")
        print(f"  Weapon: {tournament.weapon}, Bracket: {tournament.bracket}")
        print(f"  Competition Type: {tournament.competition_type}")
        
        # Try to register fencers
        registered_count = 0
        for fencer in matching_fencers:
            success, message = register_fencer_for_tournament(
                fencer.fencer_id,
                tournament.tournament_id,
                session=session
            )
            if success:
                print(f"\n✓ Registered: {fencer.full_name} (ID: {fencer.fencer_id})")
                registered_count += 1
            else:
                print(f"\n✗ Could not register {fencer.full_name}: {message}")
        
        session.commit()
        print(f"\n✓ Successfully registered {registered_count} fencers")


def test_results_recording():
    """
    Test recording tournament results and verifying point updates.
    """
    print("\n" + "="*60)
    print("Testing Results Recording")
    print("="*60)
    
    with get_session_context() as session:
        # Get a tournament with registered fencers
        tournament = session.query(Tournament).first()
        if not tournament:
            print("\n✗ No tournaments found.")
            return
        
        # Get participants
        participants = get_tournament_participants(tournament.tournament_id, session=session)
        
        if len(participants) < 3:
            print(f"\n✗ Tournament needs at least 3 participants, found {len(participants)}")
            return
        
        print(f"\nTournament: {tournament.tournament_name}")
        print(f"  Competition Type: {tournament.competition_type}")
        print(f"  Participants: {len(participants)}")
        
        # Get initial rankings
        print("\nInitial Rankings:")
        initial_rankings = {}
        for fencer in participants[:5]:  # Show first 5
            ranking = fencer.rankings[0] if fencer.rankings else None
            if ranking:
                points = ranking.points
                initial_rankings[fencer.fencer_id] = points
                print(f"  {fencer.full_name}: {points} pts")
        
        # Set tournament status to allow results
        tournament.status = "In Progress"
        session.commit()
        
        # Create results dictionary (assign placements)
        results_dict = {}
        for i, fencer in enumerate(participants[:5], start=1):
            results_dict[fencer.fencer_id] = i
        
        # Record results
        success, message = record_tournament_results(
            tournament.tournament_id,
            results_dict,
            session=session
        )
        
        if success:
            print(f"\n✓ {message}")
            
            # Check updated rankings
            print("\nUpdated Rankings:")
            session.refresh(tournament)
            for fencer_id, placement in results_dict.items():
                fencer = session.query(Fencer).filter_by(fencer_id=fencer_id).first()
                if fencer and fencer.rankings:
                    ranking = fencer.rankings[0]
                    old_points = initial_rankings.get(fencer_id, 0)
                    new_points = ranking.points
                    points_gained = new_points - old_points
                    expected_points = calculate_points(placement, tournament.competition_type)
                    print(f"  {fencer.full_name}: {old_points} → {new_points} pts "
                          f"(gained {points_gained}, expected {expected_points})")
        else:
            print(f"\n✗ Error: {message}")


def test_csv_import():
    """
    Test importing tournament results from CSV.
    """
    print("\n" + "="*60)
    print("Testing CSV Import")
    print("="*60)
    
    with get_session_context() as session:
        # Get some fencers to use in test CSV
        fencers = session.query(Fencer).filter_by(weapon="Foil").limit(5).all()
        
        if len(fencers) < 3:
            print("\n✗ Need at least 3 Foil fencers for CSV test")
            return
        
        # Create test CSV
        csv_dir = os.path.join(os.path.dirname(__file__), "..", "data", "csv")
        os.makedirs(csv_dir, exist_ok=True)
        csv_file = os.path.join(csv_dir, "test_tournament_results.csv")
        
        # Create CSV with results
        results_data = {
            'fencer_id': [f.fencer_id for f in fencers[:5]],
            'placement': [1, 2, 3, 4, 5]
        }
        df = pd.DataFrame(results_data)
        df.to_csv(csv_file, index=False)
        print(f"\n✓ Created test CSV: {csv_file}")
        
        # Create tournament first
        tournament = create_tournament(
            tournament_name="CSV Import Test Tournament",
            date=pd.Timestamp.today(),
            weapon="Foil",
            bracket="Senior",
            competition_type="Championship",  # Test weighted points
            status="Registration Open",
            session=session
        )
        session.commit()
        print(f"✓ Created tournament ID: {tournament.tournament_id}")
        
        # Import results from CSV
        success, message, result_tournament_id = import_tournament_results_from_csv(
            csv_file,
            tournament_id=tournament.tournament_id,
            session=session
        )
        
        # Clean up test CSV
        if os.path.exists(csv_file):
            os.remove(csv_file)
            print(f"\n✓ Cleaned up test CSV file")
        
        if success:
            print(f"\n✓ {message}")
            
            # Verify results
            results = get_tournament_results(result_tournament_id, session=session)
            print(f"\nTournament Results:")
            for result in results:
                fencer = session.query(Fencer).filter_by(fencer_id=result.fencer_id).first()
                if fencer:
                    print(f"  {result.placement}. {fencer.full_name}: {result.points_awarded} pts")
        else:
            print(f"\n✗ Error: {message}")


def test_tournament_queries():
    """
    Test querying tournaments and results.
    """
    print("\n" + "="*60)
    print("Testing Tournament Queries")
    print("="*60)
    
    with get_session_context() as session:
        # Get all tournaments
        tournaments = session.query(Tournament).all()
        print(f"\nTotal tournaments in database: {len(tournaments)}")
        
        for tournament in tournaments:
            print(f"\n  {tournament.tournament_name}")
            print(f"    ID: {tournament.tournament_id}")
            print(f"    Status: {tournament.status}")
            print(f"    Competition Type: {tournament.competition_type}")
            print(f"    Participants: {tournament.get_participant_count()}")
            
            if tournament.results:
                print(f"    Results recorded: Yes")
                top_result = min(tournament.results, key=lambda r: r.placement)
                print(f"    Winner (by placement): Fencer ID {top_result.fencer_id}")


if __name__ == "__main__":
    """
    Main execution - run all tournament tests.
    """
    print("="*60)
    print("Tournament System Test Suite")
    print("="*60)
    
    # Initialize database to ensure tables exist
    init_db()
    
    try:
        # Run all tests
        test_point_calculation()
        test_tournament_creation()
        test_fencer_registration()
        test_results_recording()
        test_csv_import()
        test_tournament_queries()
        
        print("\n" + "="*60)
        print("All tournament tests completed!")
        print("="*60)
    except Exception as e:
        print(f"\n✗ Error during testing: {e}")
        import traceback
        traceback.print_exc()
