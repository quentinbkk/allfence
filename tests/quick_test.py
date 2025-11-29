"""
Quick Test Script - Demonstrates All Major Features

Run this to quickly test all functionality:
/opt/anaconda3/bin/python3 quick_test.py
"""

import sys
import os

# Add parent directory to path so we can import src
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.database import get_session_context, init_db
from src.models import Fencer, Tournament, Ranking
from src.tournament_management import (
    create_tournament, register_fencer_for_tournament, 
    record_tournament_results, get_tournament_results,
    import_tournament_results_from_csv
)
from src.tournament_points import calculate_points, print_point_structure
import pandas as pd

print("="*70)
print("Quick Test - Fencing Management System")
print("="*70)

# Initialize database
print("\n1. Initializing database...")
init_db()

with get_session_context() as session:
    # Check existing data
    fencer_count = session.query(Fencer).count()
    print(f"   Found {fencer_count} fencers in database")
    
    if fencer_count == 0:
        print("\n   ⚠️  No fencers found! Please run migrate_csv_to_db.py first.")
        exit(1)
    
    # Test point calculation
    print("\n2. Testing Point Calculation System...")
    print(f"   1st place Regional: {calculate_points(1, 'Regional')} pts")
    print(f"   1st place Championship: {calculate_points(1, 'Championship')} pts (2x multiplier)")
    print(f"   1st place International: {calculate_points(1, 'International')} pts (2.5x multiplier)")
    
    # Create a test tournament
    print("\n3. Creating Test Tournament...")
    tournament = create_tournament(
        tournament_name="Quick Test Championship",
        date=pd.Timestamp('2024-12-20'),
        weapon="Foil",
        bracket="Senior",
        competition_type="Championship",
        location="Test Arena",
        status="Registration Open",
        session=session
    )
    session.commit()
    print(f"   ✓ Created: {tournament.tournament_name}")
    print(f"   Tournament ID: {tournament.tournament_id}")
    print(f"   Competition Type: {tournament.competition_type} (2x points)")
    
    # Find eligible fencers
    print("\n4. Finding Eligible Fencers...")
    eligible_fencers = session.query(Fencer).filter_by(
        weapon="Foil"
    ).limit(5).all()
    
    print(f"   Found {len(eligible_fencers)} Foil fencers")
    
    # Show point structure
    print("\n5. Championship Point Structure:")
    print_point_structure("Championship")
    
    # Register fencers
    print("\n6. Registering Fencers...")
    registered = []
    for fencer in eligible_fencers:
        # Check bracket match
        if fencer.rankings and fencer.rankings[0].bracket_name == "Senior":
            success, message = register_fencer_for_tournament(
                fencer.fencer_id,
                tournament.tournament_id,
                session=session
            )
            if success:
                print(f"   ✓ Registered: {fencer.full_name}")
                registered.append(fencer)
            else:
                print(f"   ✗ {fencer.full_name}: {message}")
    
    if len(registered) < 3:
        print(f"\n   ⚠️  Only {len(registered)} fencers registered. Need at least 3 for results test.")
        print("   Creating results with available fencers...")
    
    # Show initial rankings
    print("\n7. Initial Rankings:")
    initial_points = {}
    for fencer in registered[:5]:
        ranking = fencer.rankings[0] if fencer.rankings else None
        if ranking:
            points = ranking.points
            initial_points[fencer.fencer_id] = points
            print(f"   {fencer.full_name}: {points} pts")
    
    # Record results
    if len(registered) >= 2:
        print("\n8. Recording Tournament Results...")
        tournament.status = "In Progress"
        session.commit()
        
        # Assign placements
        results_dict = {f.fencer_id: i+1 for i, f in enumerate(registered[:min(5, len(registered))])}
        
        success, message = record_tournament_results(
            tournament.tournament_id,
            results_dict,
            session=session
        )
        print(f"   {message}")
        
        # Show updated rankings
        print("\n9. Updated Rankings:")
        session.refresh(tournament)
        for fencer_id, placement in results_dict.items():
            fencer = session.query(Fencer).filter_by(fencer_id=fencer_id).first()
            if fencer and fencer.rankings:
                ranking = fencer.rankings[0]
                old_points = initial_points.get(fencer_id, 0)
                new_points = ranking.points
                points_gained = new_points - old_points
                expected = calculate_points(placement, tournament.competition_type)
                print(f"   {fencer.full_name}: {old_points} → {new_points} pts "
                      f"(gained {points_gained}, expected {expected})")
        
        # Show tournament results
        print("\n10. Tournament Results:")
        results = get_tournament_results(tournament.tournament_id, session=session)
        for result in results:
            fencer = result.fencer
            print(f"    {result.placement}. {fencer.full_name}: {result.points_awarded} pts")
    else:
        print("\n8. Skipping results recording (need at least 2 registered fencers)")
    
    # Test queries
    print("\n11. Query Examples:")
    total_tournaments = session.query(Tournament).count()
    print(f"    Total tournaments: {total_tournaments}")
    
    top_fencer = session.query(Ranking).filter_by(
        bracket_name="Senior"
    ).order_by(Ranking.points.desc()).first()
    if top_fencer:
        fencer = top_fencer.fencer
        print(f"    Top ranked Senior fencer: {fencer.full_name} with {top_fencer.points} pts")

print("\n" + "="*70)
print("Quick Test Complete!")
print("="*70)
print("\nNext steps:")
print("  - Run test_models.py for comprehensive model tests")
print("  - Run test_tournaments.py for tournament system tests")
print("  - Try importing results from CSV: import_tournament_results_from_csv()")
print("  - Create tournaments with different competition types and compare points")
