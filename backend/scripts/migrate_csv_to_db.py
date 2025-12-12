"""
Migration Script - Import existing CSV data into SQLAlchemy database

This script migrates your existing CSV data into the new database format.
Run this once to populate your database with data from synth_data.csv
"""

import sys
import os

# Add parent directory to path so we can import src
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.database import init_db, get_session_context, reset_db
from src.ingestion import ingest_fencers_from_csv

def main():
    """
    Main migration function.
    
    This function:
    1. Initializes the database (creates tables)
    2. Ingests fencer data from CSV
    3. Verifies the migration was successful
    """
    print("="*60)
    print("CSV to Database Migration Script")
    print("="*60)
    
    # Ask user if they want to reset the database
    # (Only do this if you want to start fresh)
    # Check if running interactively
    try:
        reset_choice = input("\nDo you want to reset the database? (This will delete all data) [y/N]: ")
    except EOFError:
        # Running non-interactively (e.g., in a script), default to not resetting
        print("\nRunning non-interactively. Keeping existing data.")
        reset_choice = 'n'
    
    if reset_choice.lower() == 'y':
        print("\nResetting database...")
        reset_db()
    else:
        print("\nInitializing database (keeping existing data)...")
        init_db()
    
    # Path to CSV file - look in the root data directory (two levels up from scripts)
    csv_file = os.path.join(os.path.dirname(__file__), "..", "..", "data", "csv", "synth_data.csv")
    
    print(f"\nMigrating data from {csv_file}...")
    print("This may take a moment...\n")
    
    try:
        # Ingest all fencers from CSV
        # This function automatically:
        # - Creates Club objects for each unique club_id
        # - Creates Fencer objects with all attributes
        # - Creates Ranking objects for each eligible bracket
        fencers_dict = ingest_fencers_from_csv(csv_file)
        
        print(f"\n✓ Successfully migrated {len(fencers_dict)} fencers")
        
        # Verify the data was saved correctly
        with get_session_context() as session:
            from src.models import Fencer, Club, Ranking
            
            # Count records
            fencer_count = session.query(Fencer).count()
            club_count = session.query(Club).count()
            ranking_count = session.query(Ranking).count()
            
            print(f"\nDatabase Statistics:")
            print(f"  - Fencers: {fencer_count}")
            print(f"  - Clubs: {club_count}")
            print(f"  - Rankings: {ranking_count}")
            
            # Show a sample fencer
            sample_fencer = session.query(Fencer).first()
            if sample_fencer:
                print(f"\nSample Fencer (first in database):")
                print(f"  Name: {sample_fencer.full_name}")
                print(f"  ID: {sample_fencer.fencer_id}")
                print(f"  Weapon: {sample_fencer.weapon}")
                print(f"  Club: {sample_fencer.club_id}")
                print(f"  Rankings: {len(sample_fencer.rankings)} brackets")
        
        print("\n" + "="*60)
        print("Migration completed successfully!")
        print("="*60)
        print("\nNext steps:")
        print("  1. Run test_models.py to verify everything works")
        print("  2. Start using the database models in your code")
        print("  3. The database file is: fencing_management.db")
        
    except FileNotFoundError:
        print(f"\n✗ Error: Could not find CSV file: {csv_file}")
        print("   Please make sure the file exists in the data/ directory")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Error during migration: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
