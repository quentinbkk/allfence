#!/usr/bin/env python3
"""
Script to export data from SQLite database to JSON format.
Use this before migrating to PostgreSQL.
"""

import json
import sys
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from src.database import get_session
from src.models import Club, Fencer, Ranking, Tournament, TournamentResult, User, Season


def export_data():
    """Export all data from SQLite to JSON files."""
    session = get_session()
    
    try:
        print("\n🗄️  Exporting AllFence database to JSON...\n")
        
        export_dir = Path(__file__).parent.parent / "data" / "export"
        export_dir.mkdir(exist_ok=True)
        
        # Export Clubs
        clubs = session.query(Club).all()
        with open(export_dir / "clubs.json", "w") as f:
            json.dump([c.to_dict() for c in clubs], f, indent=2, default=str)
        print(f"✓ Exported {len(clubs)} clubs")
        
        # Export Fencers
        fencers = session.query(Fencer).all()
        with open(export_dir / "fencers.json", "w") as f:
            json.dump([f.to_dict(include_rankings=False) for f in fencers], f, indent=2, default=str)
        print(f"✓ Exported {len(fencers)} fencers")
        
        # Export Rankings
        rankings = session.query(Ranking).all()
        with open(export_dir / "rankings.json", "w") as f:
            json.dump([r.to_dict() for r in rankings], f, indent=2, default=str)
        print(f"✓ Exported {len(rankings)} rankings")
        
        # Export Tournaments
        tournaments = session.query(Tournament).all()
        with open(export_dir / "tournaments.json", "w") as f:
            json.dump([t.to_dict() for t in tournaments], f, indent=2, default=str)
        print(f"✓ Exported {len(tournaments)} tournaments")
        
        # Export Tournament Results
        results = session.query(TournamentResult).all()
        with open(export_dir / "tournament_results.json", "w") as f:
            json.dump([r.to_dict() for r in results], f, indent=2, default=str)
        print(f"✓ Exported {len(results)} tournament results")
        
        # Export Users (careful with passwords!)
        users = session.query(User).all()
        with open(export_dir / "users.json", "w") as f:
            json.dump([u.to_dict() for u in users], f, indent=2, default=str)
        print(f"✓ Exported {len(users)} users")
        
        # Export Seasons
        seasons = session.query(Season).all()
        with open(export_dir / "seasons.json", "w") as f:
            json.dump([s.to_dict() for s in seasons], f, indent=2, default=str)
        print(f"✓ Exported {len(seasons)} seasons")
        
        print(f"\n✅ Export complete! Files saved to: {export_dir}")
        print("\nNext steps:")
        print("1. Set DATABASE_URL to your PostgreSQL connection string")
        print("2. Run: python backend/scripts/import_data.py")
        
    except Exception as e:
        print(f"\n❌ Error exporting data: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        session.close()


if __name__ == "__main__":
    export_data()
