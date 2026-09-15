#!/usr/bin/env python3
"""
Build the read-only demo SQLite database from the committed JSON exports
in data/export/. This is the database that ships with the deployment.

Run whenever data/export/*.json changes:
    python backend/scripts/build_demo_db.py
"""

import json
import sys
from pathlib import Path
from datetime import datetime

backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

DB_PATH = backend_dir / "data" / "database" / "fencing_management.db"

# Make sure src.database picks up this exact path before it's imported
DB_PATH.parent.mkdir(parents=True, exist_ok=True)
if DB_PATH.exists():
    DB_PATH.unlink()

from src.database import init_db, get_session  # noqa: E402
from src.models import Club, Fencer, Ranking, Tournament, TournamentResult, Season  # noqa: E402


def build():
    export_dir = backend_dir / "data" / "export"

    print("Creating schema...")
    init_db()
    session = get_session()

    try:
        with open(export_dir / "clubs.json") as f:
            clubs_data = json.load(f)
        for club_dict in clubs_data:
            club_dict.pop("fencer_count", None)
            session.add(Club(**club_dict))
        session.commit()
        print(f"  {len(clubs_data)} clubs")

        with open(export_dir / "fencers.json") as f:
            fencers_data = json.load(f)
        for fencer_dict in fencers_data:
            if fencer_dict.get("dob"):
                fencer_dict["dob"] = datetime.fromisoformat(fencer_dict["dob"]).date()
            for field in ("full_name", "age", "bracket", "club_name", "rankings", "total_points"):
                fencer_dict.pop(field, None)
            session.add(Fencer(**fencer_dict))
        session.commit()
        print(f"  {len(fencers_data)} fencers")

        with open(export_dir / "seasons.json") as f:
            seasons_data = json.load(f)
        for season_dict in seasons_data:
            if season_dict.get("start_date"):
                season_dict["start_date"] = datetime.fromisoformat(season_dict["start_date"]).date()
            if season_dict.get("end_date"):
                season_dict["end_date"] = datetime.fromisoformat(season_dict["end_date"]).date()
            season_dict.pop("tournament_count", None)
            season_id = season_dict.pop("season_id", None)
            season = Season(**season_dict)
            if season_id:
                season.season_id = season_id
            session.add(season)
        session.commit()
        print(f"  {len(seasons_data)} seasons")

        with open(export_dir / "tournaments.json") as f:
            tournaments_data = json.load(f)
        for tournament_dict in tournaments_data:
            if tournament_dict.get("date"):
                tournament_dict["date"] = datetime.fromisoformat(tournament_dict["date"]).date()
            for field in ("participant_count", "is_full", "results"):
                tournament_dict.pop(field, None)
            tournament_id = tournament_dict.pop("tournament_id", None)
            tournament = Tournament(**tournament_dict)
            if tournament_id:
                tournament.tournament_id = tournament_id
            session.add(tournament)
        session.commit()
        print(f"  {len(tournaments_data)} tournaments")

        with open(export_dir / "tournament_results.json") as f:
            results_data = json.load(f)
        for result_dict in results_data:
            result_dict.pop("fencer_name", None)
            result_id = result_dict.pop("result_id", None)
            result = TournamentResult(**result_dict)
            if result_id:
                result.result_id = result_id
            session.add(result)
        session.commit()
        print(f"  {len(results_data)} tournament results")

        # Rankings are auto-created (0 points) by Fencer.__init__; apply the real point totals.
        with open(export_dir / "rankings.json") as f:
            rankings_data = json.load(f)
        updated = 0
        for ranking_dict in rankings_data:
            existing = (
                session.query(Ranking)
                .filter_by(fencer_id=ranking_dict["fencer_id"], bracket_name=ranking_dict["bracket_name"])
                .first()
            )
            if existing:
                existing.points = ranking_dict["points"]
                existing.tournaments_attended = ranking_dict.get("tournaments_attended", 0)
                updated += 1
        session.commit()
        print(f"  {updated} rankings updated with points")

        print(f"\nDemo database written to {DB_PATH}")
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


if __name__ == "__main__":
    build()
