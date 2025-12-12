#!/usr/bin/env python3
"""
Script to simulate a fencing season with well-attended tournaments.

This script ensures:
- Minimum 50% fill rate for all tournaments
- Smart tournament generation based on eligible fencer pool
- Balanced distribution of competition types
- Realistic attendance patterns
"""

import sys
from datetime import date
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from src.database import get_session
from src.season_simulation import simulate_full_season


def main():
    """Run season simulation with improved attendance logic."""
    session = get_session()
    
    try:
        print("\n🤺 AllFence Season Simulator 🤺\n")
        
        # Get user input
        season_name = input("Enter season name (e.g., 2024-2025): ").strip() or "2024-2025"
        
        year_input = input("Enter start year (default 2024): ").strip()
        start_year = int(year_input) if year_input else 2024
        
        num_input = input("Enter number of tournaments (default 100): ").strip()
        num_tournaments = int(num_input) if num_input else 100
        
        reset_input = input("Reset all rankings before simulation? (y/N): ").strip().lower()
        reset_rankings = reset_input == 'y'
        
        # Set dates
        start_date = date(start_year, 9, 1)  # September 1
        end_date = date(start_year + 1, 6, 30)  # June 30 next year
        
        print(f"\n📅 Season: {season_name}")
        print(f"📅 Dates: {start_date} to {end_date}")
        print(f"🏆 Tournaments: {num_tournaments}")
        print(f"🔄 Reset rankings: {reset_rankings}")
        print()
        
        # Run simulation
        stats = simulate_full_season(
            session=session,
            season_name=season_name,
            start_date=start_date,
            end_date=end_date,
            num_tournaments=num_tournaments,
            reset_rankings=reset_rankings
        )
        
        # Display summary
        print("\n✅ SIMULATION SUCCESSFUL!\n")
        print("📊 Summary:")
        print(f"   • Completed: {stats['tournaments_completed']}/{stats['tournaments_created']}")
        print(f"   • Average fill rate: {stats['avg_fill_rate']:.1%}")
        print(f"   • Average participants: {stats['avg_participants']:.1f}")
        print(f"   • Total results recorded: {stats['total_results']}")
        
        if stats['tournaments_cancelled'] > 0:
            print(f"\n⚠️  {stats['tournaments_cancelled']} tournaments cancelled (insufficient participants)")
        
        print(f"\n🎯 Attendance Quality:")
        if stats['low_attendance'] == 0:
            print(f"   ✅ No poorly attended tournaments!")
        else:
            print(f"   ⚠️  Low (<50%): {stats['low_attendance']}")
        print(f"   ✓ Medium (50-80%): {stats['medium_attendance']}")
        print(f"   ✓ High (≥80%): {stats['high_attendance']}")
        
        print("\n🎉 Season simulation complete!\n")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Simulation cancelled by user.\n")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}\n")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        session.close()


if __name__ == "__main__":
    main()
