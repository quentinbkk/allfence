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


def import_data():
    """Import all data from JSON files to PostgreSQL."""
    
    # Initialize database (create tables)
    print("\n🗄️  Initializing PostgreSQL database...\n")
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
            
            season = Season(**season_dict)
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
            
            tournament = Tournament(**tournament_dict)
            session.merge(tournament)
        session.commit()
        print(f"✓ Imported {len(tournaments_data)} tournaments")
        
        # Import Tournament Results
        print("Importing tournament results...")
        with open(export_dir / "tournament_results.json", "r") as f:
            results_data = json.load(f)
        
        for result_dict in results_data:
            result = TournamentResult(**result_dict)
            session.merge(result)
        session.commit()
        print(f"✓ Imported {len(results_data)} tournament results")
        
        # Import Rankings
        print("Importing rankings...")
        with open(export_dir / "rankings.json", "r") as f:
            rankings_data = json.load(f)
        
        for ranking_dict in rankings_data:
            ranking = Ranking(**ranking_dict)
            session.merge(ranking)
        session.commit()
        print(f"✓ Imported {len(rankings_data)} rankings")
        
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
    
    import_data()
