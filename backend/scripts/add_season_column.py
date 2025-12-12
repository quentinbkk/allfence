"""
Migration script to add season_id column to tournaments table
"""
import sqlite3
import os

# Database path
DB_PATH = os.path.join(os.path.dirname(__file__), '../data/database/fencing_management.db')

def migrate():
    print(f"Connecting to database: {DB_PATH}")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # Check if season_id column exists
        cursor.execute("PRAGMA table_info(tournaments)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if 'season_id' not in columns:
            print("Adding season_id column to tournaments table...")
            cursor.execute("ALTER TABLE tournaments ADD COLUMN season_id INTEGER")
            print("✓ Added season_id column")
        else:
            print("season_id column already exists")
        
        # Create seasons table if it doesn't exist
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS seasons (
                season_id INTEGER PRIMARY KEY AUTOINCREMENT,
                name VARCHAR NOT NULL UNIQUE,
                start_date DATE NOT NULL,
                end_date DATE NOT NULL,
                status VARCHAR NOT NULL DEFAULT 'Upcoming',
                description VARCHAR,
                CONSTRAINT check_season_status CHECK (status IN ('Active', 'Completed', 'Upcoming'))
            )
        """)
        print("✓ Seasons table ready")
        
        # Commit changes
        conn.commit()
        print("\n✓ Migration completed successfully!")
        
    except Exception as e:
        print(f"Error during migration: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()

if __name__ == '__main__':
    migrate()
