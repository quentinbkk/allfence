#!/usr/bin/env python3
"""
Script to import data from JSON files to PostgreSQL database.
Run this after exporting from SQLite.
"""

import json
import sys
from pathlib import Path
from datetime import datetime, date

# Add backend to path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from src.database import get_session, init_db
from src.models import Club, Fencer, Ranking, Tournament, TournamentResult, User, Season


def import_data(drop_existing=False):
    """Import all data from JSON files to PostgreSQL.
    
    Args:
        drop_existing: If True, drop all existing tables before import
    """
    
    # Initialize database (create tables)
    print("\n🗄️  Initializing PostgreSQL database...\n")
    
    if drop_existing:
        from src.database import Base, engine
        print("⚠️  Dropping all existing tables...")
        Base.metadata.drop_all(engine)
        print("✓ All tables dropped\n")
    
    init_db()
    
    session = get_session()
    
    try:
        export_dir = Path(__file__).parent.parent / "data" / "export"
        
        if not export_dir.exists():
            print(f"❌ Export directory not found: {export_dir}")
            print("Run export_data.py first!")
            sys.exit(1)
        
        print("📥 Importing data from JSON files...\n")
        
        # Import Clubs first (referenced by Fencers)
        print("Importing clubs...")
        with open(export_dir / "clubs.json", "r") as f:
            clubs_data = json.load(f)
        
        for club_dict in clubs_data:
            # Remove computed fields that aren't database columns
            club_dict.pop('fencer_count', None)
            club = Club(**club_dict)
            session.merge(club)
        session.commit()
        print(f"✓ Imported {len(clubs_data)} clubs")
        
        # Import Fencers
        print("Importing fencers...")
        with open(export_dir / "fencers.json", "r") as f:
            fencers_data = json.load(f)
        
        for fencer_dict in fencers_data:
            # Convert date strings to date objects
            if fencer_dict.get('dob'):
                fencer_dict['dob'] = datetime.fromisoformat(fencer_dict['dob']).date()
            
            # Remove computed fields that aren't database columns
            fencer_dict.pop('full_name', None)
            fencer_dict.pop('age', None)
            fencer_dict.pop('bracket', None)
            fencer_dict.pop('club_name', None)
            fencer_dict.pop('rankings', None)
            fencer_dict.pop('total_points', None)
            
            fencer = Fencer(**fencer_dict)
            session.merge(fencer)
        session.commit()
        print(f"✓ Imported {len(fencers_data)} fencers")
        
        # Import Seasons
        print("Importing seasons...")
        with open(export_dir / "seasons.json", "r") as f:
            seasons_data = json.load(f)
        
        for season_dict in seasons_data:
            if season_dict.get('start_date'):
                season_dict['start_date'] = datetime.fromisoformat(season_dict['start_date']).date()
            if season_dict.get('end_date'):
                season_dict['end_date'] = datetime.fromisoformat(season_dict['end_date']).date()
            
            # Remove computed fields and auto-generated ID
            season_dict.pop('tournament_count', None)
            season_id = season_dict.pop('season_id', None)
            
            season = Season(**season_dict)
            if season_id:
                season.season_id = season_id
            session.merge(season)
        session.commit()
        print(f"✓ Imported {len(seasons_data)} seasons")
        
        # Import Tournaments
        print("Importing tournaments...")
        with open(export_dir / "tournaments.json", "r") as f:
            tournaments_data = json.load(f)
        
        for tournament_dict in tournaments_data:
            if tournament_dict.get('date'):
                tournament_dict['date'] = datetime.fromisoformat(tournament_dict['date']).date()
            
            # Remove computed fields and auto-generated ID
            tournament_dict.pop('participant_count', None)
            tournament_dict.pop('is_full', None)
            tournament_dict.pop('results', None)
            tournament_id = tournament_dict.pop('tournament_id', None)
            
            tournament = Tournament(**tournament_dict)
            if tournament_id:
                tournament.tournament_id = tournament_id
            session.merge(tournament)
        session.commit()
        print(f"✓ Imported {len(tournaments_data)} tournaments")
        
        # Import Tournament Results
        print("Importing tournament results...")
        with open(export_dir / "tournament_results.json", "r") as f:
            results_data = json.load(f)
        
        for result_dict in results_data:
            # Remove computed fields and auto-generated ID
            result_dict.pop('fencer_name', None)
            result_id = result_dict.pop('result_id', None)
            
            result = TournamentResult(**result_dict)
            if result_id:
                result.result_id = result_id
            session.merge(result)
        session.commit()
        print(f"✓ Imported {len(results_data)} tournament results")
        
        # Skip Rankings import - they are automatically created when fencers are imported
        # The Fencer.__init__() method calls assign_rankings_from_dob() which creates rankings
        print("⚠️  Skipping rankings import (auto-generated from fencers)")
        
        # Update ranking points from imported rankings data
        print("Updating ranking points from exported data...")
        with open(export_dir / "rankings.json", "r") as f:
            rankings_data = json.load(f)
        
        updated_count = 0
        for ranking_dict in rankings_data:
            # Find existing ranking and update it
            existing = session.query(Ranking).filter_by(
                fencer_id=ranking_dict['fencer_id'],
                bracket_name=ranking_dict['bracket_name']
            ).first()
            
            if existing:
                existing.points = ranking_dict['points']
                existing.tournaments_attended = ranking_dict['tournaments_attended']
                updated_count += 1
        
        session.commit()
        print(f"✓ Updated {updated_count} rankings with points and tournament data")
        
        # Import Users (passwords are already hashed)
        print("Importing users...")
        with open(export_dir / "users.json", "r") as f:
            users_data = json.load(f)
        
        for user_dict in users_data:
            user = User(**user_dict)
            session.merge(user)
        session.commit()
        print(f"✓ Imported {len(users_data)} users")
        
        print(f"\n✅ Import complete! All data migrated to PostgreSQL.")
        
    except Exception as e:
        session.rollback()
        print(f"\n❌ Error importing data: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        session.close()


if __name__ == "__main__":
    import os
    
    # Check if DATABASE_URL is set
    if not os.getenv('DATABASE_URL'):
        print("\n❌ DATABASE_URL environment variable not set!")
        print("\nSet your PostgreSQL connection string:")
        print('export DATABASE_URL="postgresql://user:pass@host:port/database"')
        sys.exit(1)
    
    # Confirm it's PostgreSQL
    if 'postgresql' not in os.getenv('DATABASE_URL', ''):
        print("\n⚠️  Warning: DATABASE_URL doesn't look like PostgreSQL!")
        print("Are you sure you want to continue? (y/n)")
        if input().lower() != 'y':
            sys.exit(0)
    
    # Ask if user wants to drop existing tables
    print("\n⚠️  This will import data into your PostgreSQL database.")
    print("Do you want to DROP all existing tables first? (y/n)")
    print("(Choose 'y' for a fresh start, 'n' to append/update existing data)")
    drop = input().lower().strip() == 'y'
    
    import_data(drop_existing=drop)
