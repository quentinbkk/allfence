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
        from scripts.load_realistic_data import load_realistic_data
        load_realistic_data()
        print("✓ Database initialized successfully")
    except Exception as e:
        print(f"⚠️  Error loading data: {e}")
        print("Database initialized but empty")

if __name__ == "__main__":
    initialize_if_needed()
