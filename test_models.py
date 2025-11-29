"""
Test Script for SQLAlchemy Models

This script demonstrates how to use the new database models and serves as
a test to verify everything is working correctly.
"""

from database import init_db, get_session_context, reset_db
from models import Fencer, Club, Ranking
from ingestion import ingest_fencers_from_csv
import pandas as pd

def test_basic_operations():
    """
    Test basic database operations: create, read, update, delete.
    """
    print("\n" + "="*50)
    print("Testing Basic Database Operations")
    print("="*50)
    
    # Initialize database (creates tables)
    init_db()
    
    # Use session context manager for automatic cleanup
    with get_session_context() as session:
        # Test 1: Create a club
        print("\n1. Creating a club...")
        club = Club(
            club_id="Test_Club_1",
            club_name="Test Fencing Club",
            start_year=2020,
            status="Active",
            weapon_club="Sabre"
        )
        session.add(club)
        session.commit()
        print(f"   Created: {club}")
        
        # Test 2: Create a fencer
        print("\n2. Creating a fencer...")
        fencer = Fencer(
            fencer_id=99999,
            first_name="Test",
            last_name="Fencer",
            dob=pd.to_datetime('2003-03-02'),
            gender='M',
            weapon='Sabre',
            club_id="Test_Club_1"
        )
        session.add(fencer)
        session.commit()
        print(f"   Created: {fencer}")
        
        # Test 3: Check that rankings were automatically created
        print("\n3. Checking automatic ranking creation...")
        # Each fencer should have exactly ONE ranking for their age bracket
        print(f"   Fencer has {len(fencer.rankings)} ranking(s):")
        if len(fencer.rankings) == 1:
            ranking = fencer.rankings[0]
            print(f"      - {ranking} (Correct: exactly one bracket)")
        else:
            print(f"      Warning: Expected 1 ranking, found {len(fencer.rankings)}")
            for ranking in fencer.rankings:
                print(f"      - {ranking}")
        
        # Test 4: Update ranking points
        print("\n4. Updating ranking points...")
        senior_ranking = fencer.get_ranking_for_bracket("Senior")
        if senior_ranking:
            senior_ranking.update_ranking(100)
            session.commit()
            print(f"   Updated Senior ranking: {senior_ranking}")
        
        # Test 5: Query fencer back from database
        print("\n5. Querying fencer from database...")
        queried_fencer = session.query(Fencer).filter_by(fencer_id=99999).first()
        if queried_fencer:
            print(f"   Found: {queried_fencer}")
            print(f"   Club: {queried_fencer.club}")
            print(f"   Total points: {queried_fencer.get_total_points()}")
        
        # Test 6: Query club and check fencers
        print("\n6. Querying club and checking fencers...")
        queried_club = session.query(Club).filter_by(club_id="Test_Club_1").first()
        if queried_club:
            print(f"   Club: {queried_club.club_name}")
            print(f"   Number of fencers: {queried_club.get_fencer_count()}")
            print(f"   Total club points: {queried_club.get_club_total_points()}")
        
        # Test 7: Delete test data
        print("\n7. Cleaning up test data...")
        session.delete(fencer)
        session.delete(club)
        session.commit()
        print("   Test data deleted")


def test_csv_ingestion():
    """
    Test ingesting data from the existing CSV file.
    """
    print("\n" + "="*50)
    print("Testing CSV Ingestion")
    print("="*50)
    
    # Initialize database
    init_db()
    
    # Check if data already exists
    with get_session_context() as session:
        from models import Fencer
        existing_count = session.query(Fencer).count()
        if existing_count > 0:
            print(f"\nDatabase already contains {existing_count} fencers.")
            print("Skipping ingestion to avoid duplicates.")
            print("If you want to re-import, reset the database first using: reset_db()")
            
            # Use existing data for testing
            fencers_dict = {f.fencer_id: f for f in session.query(Fencer).all()}
        else:
            # Ingest fencers from CSV
            print("\nIngesting fencers from CSV...")
            fencers_dict = ingest_fencers_from_csv("./data/synth_data.csv")
    
    print(f"\nSuccessfully ingested {len(fencers_dict)} fencers")
    
    # Verify data in database
    with get_session_context() as session:
        # Count fencers in database
        fencer_count = session.query(Fencer).count()
        print(f"Total fencers in database: {fencer_count}")
        
        # Count rankings
        ranking_count = session.query(Ranking).count()
        print(f"Total rankings in database: {ranking_count}")
        
        # Count clubs
        club_count = session.query(Club).count()
        print(f"Total clubs in database: {club_count}")
        
        # Query a specific fencer
        print("\nQuerying a specific fencer (ID: 70196)...")
        fencer = session.query(Fencer).filter_by(fencer_id=70196).first()
        if fencer:
            print(f"   Name: {fencer.full_name}")
            print(f"   DOB: {fencer.dob}")
            print(f"   Gender: {fencer.gender}")
            print(f"   Weapon: {fencer.weapon}")
            print(f"   Club: {fencer.club_id}")
            print(f"   Rankings:")
            for ranking in fencer.rankings:
                print(f"      - {ranking}")
        
        # Query fencers by bracket to show distribution
        print("\nFencer distribution by bracket:")
        from ranking import AGE_BRACKETS
        for bracket_name, min_age, max_age in AGE_BRACKETS:
            count = session.query(Ranking).filter_by(bracket_name=bracket_name).count()
            print(f"   {bracket_name:8s} (ages {min_age:2d}-{max_age:2d}): {count:4d} fencers")
        
        # Query top fencers by points in Senior bracket
        print("\nTop 5 fencers in Senior bracket:")
        senior_rankings = session.query(Ranking).filter_by(
            bracket_name="Senior"
        ).order_by(Ranking.points.desc()).limit(5).all()
        
        if senior_rankings:
            for ranking in senior_rankings:
                fencer = ranking.fencer
                print(f"   {fencer.full_name}: {ranking.points} pts ({fencer.weapon})")
        else:
            print("   No fencers in Senior bracket yet")


def test_relationships():
    """
    Test that relationships between models work correctly.
    """
    print("\n" + "="*50)
    print("Testing Model Relationships")
    print("="*50)
    
    with get_session_context() as session:
        # Get a club
        club = session.query(Club).first()
        if club:
            print(f"\nClub: {club.club_name}")
            print(f"   Number of fencers: {len(club.fencers)}")
            
            # Show first 3 fencers in the club
            print(f"\n   First 3 fencers:")
            for fencer in club.fencers[:3]:
                print(f"      - {fencer.full_name} ({fencer.weapon})")
        
        # Get a fencer and show their club
        fencer = session.query(Fencer).first()
        if fencer:
            print(f"\nFencer: {fencer.full_name}")
            if fencer.club:
                print(f"   Club: {fencer.club.club_name}")
            print(f"   Rankings: {len(fencer.rankings)} brackets")


if __name__ == "__main__":
    """
    Main execution - run all tests.
    """
    print("="*50)
    print("SQLAlchemy Models Test Suite")
    print("="*50)
    
    # Option to reset database (uncomment to start fresh)
    # WARNING: This will delete all data!
    # reset_db()
    
    # Run tests
    try:
        test_basic_operations()
        test_csv_ingestion()
        test_relationships()
        print("\n" + "="*50)
        print("All tests completed successfully!")
        print("="*50)
    except Exception as e:
        print(f"\nError during testing: {e}")
        import traceback
        traceback.print_exc()
