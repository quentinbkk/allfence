#!/usr/bin/env python3
"""
Initialize database and load data for production deployment.
This runs once when the app starts if database doesn't exist.
"""

import os
from pathlib import Path
from src.database import init_db, get_session
from src.models import Fencer

def initialize_if_needed():
    """Initialize database and load data if it doesn't exist."""
    
    # Check if database exists and has data
    try:
        session = get_session()
        fencer_count = session.query(Fencer).count()
        session.close()
        
        if fencer_count > 0:
            print(f"✓ Database already initialized with {fencer_count} fencers")
            return
    except Exception as e:
        print(f"Database needs initialization: {e}")
    
    # Initialize database
    print("🗄️  Initializing database...")
    init_db()
    
    # Load realistic data
    print("📥 Loading data...")
    try:
        import sys
        import subprocess
        # Run the load_realistic_data script as a subprocess
        result = subprocess.run(
            [sys.executable, 'scripts/load_realistic_data.py'],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent
        )
        if result.returncode == 0:
            print("✓ Database initialized successfully with data")
            print(result.stdout)
        else:
            print(f"⚠️  Error loading data: {result.stderr}")
            print("Database initialized but empty")
    except Exception as e:
        print(f"⚠️  Error loading data: {e}")
        print("Database initialized but empty")

if __name__ == "__main__":
    initialize_if_needed()
