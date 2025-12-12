"""
Recalculate all ranking points from tournament results
This fixes any inconsistencies where ranking points don't match actual tournament results
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.database import get_session_context
from src.models import Ranking, TournamentResult, Fencer
from sqlalchemy import func

def recalculate_rankings():
    """Recalculate all ranking points from tournament results"""
    print("=" * 70)
    print("🔄 RECALCULATING RANKINGS FROM TOURNAMENT RESULTS")
    print("=" * 70)
    
    with get_session_context() as session:
        # Get all rankings
        rankings = session.query(Ranking).all()
        
        print(f"\n📊 Found {len(rankings)} rankings to update")
        
        updated_count = 0
        mismatches_found = 0
        
        for ranking in rankings:
            # Calculate actual points from tournament results
            result = session.query(
                func.count(TournamentResult.result_id).label('count'),
                func.sum(TournamentResult.points_awarded).label('total_points')
            ).filter(
                TournamentResult.fencer_id == ranking.fencer_id
            ).join(
                Fencer, TournamentResult.fencer_id == Fencer.fencer_id
            ).first()
            
            actual_tournaments = result.count or 0
            actual_points = result.total_points or 0
            
            # Check if there's a mismatch
            if ranking.points != actual_points or ranking.tournaments_attended != actual_tournaments:
                mismatches_found += 1
                if mismatches_found <= 5:  # Show first 5 examples
                    print(f"\n   Mismatch found for fencer_id {ranking.fencer_id}:")
                    print(f"      Ranking: {ranking.points} pts, {ranking.tournaments_attended} tournaments")
                    print(f"      Actual:  {actual_points} pts, {actual_tournaments} tournaments")
                
                # Update the ranking
                ranking.points = actual_points
                ranking.tournaments_attended = actual_tournaments
                updated_count += 1
        
        if mismatches_found > 5:
            print(f"\n   ... and {mismatches_found - 5} more mismatches")
        
        # Commit all changes
        session.commit()
        
        print(f"\n✅ Updated {updated_count} rankings")
        print(f"   Total mismatches found: {mismatches_found}")
        print(f"   Total rankings checked: {len(rankings)}")
        
        # Verify the fix
        print("\n🔍 Verification:")
        verification = session.query(
            func.count().label('count')
        ).select_from(Ranking).join(
            Fencer, Ranking.fencer_id == Fencer.fencer_id
        ).outerjoin(
            TournamentResult, Ranking.fencer_id == TournamentResult.fencer_id
        ).group_by(
            Ranking.ranking_id
        ).having(
            func.coalesce(func.sum(TournamentResult.points_awarded), 0) != Ranking.points
        ).count()
        
        if verification == 0:
            print("   ✅ All rankings now match tournament results!")
        else:
            print(f"   ⚠️  Still {verification} mismatches remain")
        
        print("\n" + "=" * 70)
        print("✨ Ranking recalculation complete!")
        print("=" * 70)

if __name__ == "__main__":
    try:
        recalculate_rankings()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
