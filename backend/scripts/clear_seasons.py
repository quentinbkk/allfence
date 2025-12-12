"""
Script to delete all seasons from the database
"""
import sqlite3
import os

# Database path
DB_PATH = os.path.join(os.path.dirname(__file__), '../data/database/fencing_management.db')

def delete_all_seasons():
    print(f"Connecting to database: {DB_PATH}")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # Get all seasons
        cursor.execute("SELECT season_id, name FROM seasons")
        seasons = cursor.fetchall()
        
        if not seasons:
            print("No seasons found in database")
            return
        
        print(f"\nFound {len(seasons)} season(s):")
        for season_id, name in seasons:
            print(f"  - {name} (ID: {season_id})")
        
        # Delete all seasons
        cursor.execute("DELETE FROM seasons")
        conn.commit()
        
        print(f"\n✓ Deleted all {len(seasons)} season(s)")
        print("You can now create new seasons without conflicts")
        
    except Exception as e:
        print(f"Error: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()

if __name__ == '__main__':
    delete_all_seasons()
