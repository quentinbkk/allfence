"""
Script to fix existing fencer rankings to use the new bracket system.

This script:
1. Removes all existing rankings
2. Reassigns each fencer to their correct single bracket based on age
3. Adds Cadet (U17) and Junior (U20) brackets as needed
"""

import sys
import os

# Add parent directory to path so we can import src
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.database import get_session_context
from src.models import Fencer, Ranking
from src.ranking import calculate_age, eligible_brackets
import pandas as pd

def fix_all_fencer_brackets():
    """
    Fix brackets for all fencers in the database.
    
    This removes old rankings where fencers had multiple brackets,
    and creates a single ranking for their correct age bracket.
    """
    print("="*60)
    print("Fixing Fencer Brackets")
    print("="*60)
    print("\nThis will:")
    print("  1. Remove all existing rankings")
    print("  2. Reassign each fencer to their correct single bracket")
    print("  3. Add Cadet (ages 15-16) and Junior (ages 17-19) brackets")
    print()
    
    with get_session_context() as session:
        # Get all fencers
        fencers = session.query(Fencer).all()
        print(f"Found {len(fencers)} fencers to process.\n")
        
        bracket_counts = {
            "U11": 0,
            "U13": 0,
            "U15": 0,
            "Cadet": 0,
            "Junior": 0,
            "Senior": 0
        }
        
        # First, delete all existing rankings
        print("Deleting all existing rankings...")
        session.query(Ranking).delete()
        session.commit()
        print("✓ All old rankings deleted\n")
        
        # Process each fencer to create new rankings
        for i, fencer in enumerate(fencers):
            # Recalculate age and get correct bracket
            age = calculate_age(fencer.dob)
            brackets = eligible_brackets(age)
            
            if brackets:
                bracket_name = brackets[0]
                
                # Create new ranking for the correct bracket
                new_ranking = Ranking(
                    fencer_id=fencer.fencer_id,
                    bracket_name=bracket_name,
                    points=0  # Reset points to 0 (you can modify to preserve old points if needed)
                )
                session.add(new_ranking)
                
                bracket_counts[bracket_name] = bracket_counts.get(bracket_name, 0) + 1
                
                if (i + 1) % 100 == 0:
                    print(f"Processed {i + 1}/{len(fencers)} fencers...")
            else:
                print(f"Warning: No bracket found for fencer {fencer.fencer_id} (age {age})")
        
        # Commit all changes
        session.commit()
        
        print(f"\n✓ Processed {len(fencers)} fencers")
        print("\nBracket Distribution:")
        for bracket, count in bracket_counts.items():
            print(f"  {bracket:8s}: {count:4d} fencers")
        
        print("\n" + "="*60)
        print("Bracket fix completed successfully!")
        print("="*60)


if __name__ == "__main__":
    try:
        fix_all_fencer_brackets()
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
