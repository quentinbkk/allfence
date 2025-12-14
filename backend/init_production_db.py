#!/usr/bin/env python3
"""
Production Database Initialization Script

This module handles first-time database setup for production deployments.
It checks if the database exists and has data; if not, it creates tables,
loads sample data, and creates an admin user.

Used by: app.py on startup (Render deployment)
"""

import os
from pathlib import Path
from src.database import init_db, get_session
from src.models import Fencer

def initialize_if_needed():
    """
    Initialize database and load data if it doesn't already exist.
    
    This function is idempotent - safe to call multiple times.
    It checks if data exists before doing anything, so it won't
    overwrite an existing database.
    
    Process:
    1. Check if database has data (count fencers)
    2. If data exists, skip initialization
    3. If no data, create tables (init_db)
    4. Load realistic sample data via subprocess
    5. Create default admin user for system access
    """
    
    # Step 1: Check if database already has data by counting fencers
    try:
        session = get_session()
        fencer_count = session.query(Fencer).count()
        session.close()
        
        # If fencers exist, database is already initialized
        if fencer_count > 0:
            print(f"✓ Database already initialized with {fencer_count} fencers")
            return
    except Exception as e:
        # If query fails, database likely doesn't exist yet
        print(f"Database needs initialization: {e}")
    
    # Step 2: Initialize database schema (create all tables)
    print("🗄️  Initializing database...")
    init_db()
    
    # Step 3: Load realistic sample data (600 fencers, 15 clubs, tournaments)
    print("📥 Loading data...")
    try:
        import sys
        import subprocess
        # Run load_realistic_data.py as a subprocess to avoid import issues
        # This script populates the database with sample fencers, clubs, tournaments
        result = subprocess.run(
            [sys.executable, 'scripts/load_realistic_data.py'],
            capture_output=True,  # Capture stdout/stderr
            text=True,            # Return strings instead of bytes
            cwd=Path(__file__).parent  # Run from backend directory
        )
        if result.returncode == 0:
            print("✓ Data loaded successfully")
            print(result.stdout)
        else:
            print(f"⚠️  Error loading data: {result.stderr}")
            print("Database initialized but empty")
    except Exception as e:
        print(f"⚠️  Error loading data: {e}")
    
    # Step 4: Create default admin user (username: admin, password: admin123)
    print("👤 Creating admin user...")
    try:
        # Run create_admin.py as subprocess to create the admin account
        result = subprocess.run(
            [sys.executable, 'scripts/create_admin.py'],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent
        )
        if result.returncode == 0:
            print(result.stdout)
        else:
            print(f"⚠️  Error creating admin user: {result.stderr}")
    except Exception as e:
        print(f"⚠️  Error creating admin user: {e}")

if __name__ == "__main__":
    # Allow script to be run directly for manual database initialization
    initialize_if_needed()
