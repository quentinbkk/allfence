"""
Add tournaments_attended column to rankings table
"""

import sqlite3
import os

# Get database path
db_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'database', 'fencing_management.db')

print(f"Database path: {db_path}")
print(f"Database exists: {os.path.exists(db_path)}")

# Connect to database
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

try:
    # Check if column already exists
    cursor.execute("PRAGMA table_info(rankings)")
    columns = [row[1] for row in cursor.fetchall()]
    
    if 'tournaments_attended' not in columns:
        print("Adding tournaments_attended column to rankings table...")
        cursor.execute("""
            ALTER TABLE rankings 
            ADD COLUMN tournaments_attended INTEGER DEFAULT 0 NOT NULL
        """)
        
        # Set initial value to 0 for existing records
        cursor.execute("""
            UPDATE rankings 
            SET tournaments_attended = 0 
            WHERE tournaments_attended IS NULL
        """)
        
        conn.commit()
        print("✅ Successfully added tournaments_attended column")
    else:
        print("ℹ️  Column tournaments_attended already exists")
    
except Exception as e:
    print(f"❌ Error: {e}")
    conn.rollback()
finally:
    conn.close()

print("Migration complete!")
