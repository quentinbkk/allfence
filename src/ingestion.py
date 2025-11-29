"""
Data Ingestion Module - Import CSV data into the database

This module provides functions to load data from CSV files and populate
the database with Fencer, Club, and Ranking records.
"""

import pandas as pd
from sqlalchemy.orm import Session
from .models import Fencer, Club, Ranking
from .database import get_session_context
from typing import Dict


def ingest_fencers_from_csv(file_path: str, session: Session = None) -> Dict[int, Fencer]:
    """
    Load fencer data from CSV file and populate the database.
    
    This function reads a CSV file with fencer information, creates Fencer objects,
    automatically creates Club objects if they don't exist, and populates the database.
    Rankings are automatically created based on each fencer's age.
    
    Args:
        file_path: Path to the CSV file containing fencer data
                  Expected columns: fencer_id, first_name, last_name, dob, gender, weapon, club_id
        session: Optional database session. If None, creates a new session.
    
    Returns:
        Dictionary mapping fencer_id to Fencer objects (for backward compatibility)
    
    Example CSV format:
        fencer_id,first_name,last_name,dob,gender,weapon,club_id
        70196,Joseph,Barber,1981-11-03,1,Foil,Club_4
        54354,Marc,Velasquez,1987-10-02,1,Foil,Club_4
    """
    # Use context manager if no session provided (automatic cleanup)
    if session is None:
        with get_session_context() as session:
            return _ingest_fencers_impl(file_path, session)
    else:
        return _ingest_fencers_impl(file_path, session)


def _ingest_fencers_impl(file_path: str, session: Session) -> Dict[int, Fencer]:
    """
    Internal implementation of fencer ingestion.
    
    This is separated from the public function to handle both
    session management patterns (context manager or provided session).
    
    Args:
        file_path: Path to CSV file
        session: Active database session
    
    Returns:
        Dictionary of fencer_id -> Fencer objects
    """
    # Read CSV file into pandas DataFrame
    df = pd.read_csv(file_path)
    
    # Dictionary to store created fencers (for return value)
    fencers_dict = {}
    
    # Dictionary to track which clubs we've already created in this session
    # Prevents duplicate club creation
    clubs_created = {}
    
    # Set to track fencer IDs we've already processed in this batch
    # This prevents duplicates within the same transaction
    fencers_in_batch = set()
    
    # Iterate through each row in the CSV
    for index, row in df.iterrows():
        # Extract data from row
        fencer_id = int(row["fencer_id"])
        
        # Skip if we've already processed this fencer in this batch
        # This prevents duplicate inserts within the same transaction
        if fencer_id in fencers_in_batch:
            continue
        
        first_name = str(row["first_name"])
        last_name = str(row["last_name"])
        dob = row["dob"]  # Will be converted to date in Fencer.__init__
        gender = row["gender"]
        weapon = str(row["weapon"])
        club_id = str(row["club_id"]) if pd.notna(row["club_id"]) else None
        
        # Check if club exists in database, if not create it
        if club_id and club_id not in clubs_created:
            # Check if club already exists in database
            existing_club = session.query(Club).filter_by(club_id=club_id).first()
            
            if existing_club is None:
                # Create new club with minimal information
                # You can enhance this later to read club details from a separate CSV
                club = Club(
                    club_id=club_id,
                    club_name=club_id,  # Using club_id as name if no other info available
                    status="Active"
                )
                session.add(club)
                clubs_created[club_id] = club
                print(f"Created new club: {club_id}")
            else:
                clubs_created[club_id] = existing_club
        
        # Check if fencer already exists in database
        # Note: This won't see fencers added in the current session that haven't been committed yet
        # That's why we also check fencers_in_batch above
        existing_fencer = session.query(Fencer).filter_by(fencer_id=fencer_id).first()
        
        if existing_fencer is None:
            try:
                # Create new Fencer object
                # The __init__ method automatically:
                # - Converts dob to date format
                # - Normalizes gender (0/1 -> F/M)
                # - Calls assign_rankings_from_dob() to create Ranking entries
                fencer = Fencer(
                    fencer_id=fencer_id,
                    first_name=first_name,
                    last_name=last_name,
                    dob=dob,
                    gender=gender,
                    weapon=weapon,
                    club_id=club_id
                )
                
                # Add to session (not yet saved to database)
                session.add(fencer)
                
                # Mark as processed in this batch
                fencers_in_batch.add(fencer_id)
                fencers_dict[fencer_id] = fencer
            except Exception as e:
                # If there's an error (e.g., duplicate constraint), skip this fencer
                print(f"Error creating fencer {fencer_id}: {e}. Skipping...")
                continue
        else:
            # Fencer already exists in database, use existing one
            fencers_in_batch.add(fencer_id)  # Mark as processed
            fencers_dict[fencer_id] = existing_fencer
            if len(fencers_dict) % 100 == 0:  # Only print every 100 to avoid spam
                print(f"Processed {len(fencers_dict)} fencers...")
    
    # Commit all changes to database
    # This is when all the INSERT statements are actually executed
    try:
        session.commit()
        print(f"Successfully ingested {len(fencers_dict)} fencers from {file_path}")
    except Exception as e:
        # If commit fails, rollback the transaction
        session.rollback()
        print(f"Error committing to database: {e}")
        print("Transaction rolled back. Please check for duplicate data.")
        raise
    
    return fencers_dict


def ingest_clubs_from_csv(file_path: str, session: Session = None):
    """
    Load club data from CSV file and populate the database.
    
    This function reads club information from a CSV and creates/updates Club objects.
    If clubs already exist, their information is updated.
    
    Args:
        file_path: Path to CSV file with club data
                  Expected columns: club_id, club_name, start_year, status, weapon_club
        session: Optional database session
    
    Example CSV format:
        club_id,club_name,start_year,status,weapon_club
        Club_1,Metropolitan Fencing,1995,Active,Sabre
        Club_2,City Fencing Academy,2000,Active,All
    """
    if session is None:
        with get_session_context() as session:
            _ingest_clubs_impl(file_path, session)
    else:
        _ingest_clubs_impl(file_path, session)


def _ingest_clubs_impl(file_path: str, session: Session):
    """
    Internal implementation of club ingestion.
    
    Args:
        file_path: Path to CSV file
        session: Active database session
    """
    df = pd.read_csv(file_path)
    
    for index, row in df.iterrows():
        club_id = str(row["club_id"])
        
        # Check if club exists
        club = session.query(Club).filter_by(club_id=club_id).first()
        
        if club is None:
            # Create new club
            club = Club(
                club_id=club_id,
                club_name=str(row.get("club_name", club_id)),
                start_year=int(row["start_year"]) if pd.notna(row.get("start_year")) else None,
                status=str(row.get("status", "Active")),
                weapon_club=str(row["weapon_club"]) if pd.notna(row.get("weapon_club")) else None
            )
            session.add(club)
        else:
            # Update existing club
            if "club_name" in row and pd.notna(row["club_name"]):
                club.club_name = str(row["club_name"])
            if "start_year" in row and pd.notna(row["start_year"]):
                club.start_year = int(row["start_year"])
            if "status" in row and pd.notna(row["status"]):
                club.status = str(row["status"])
            if "weapon_club" in row and pd.notna(row["weapon_club"]):
                club.weapon_club = str(row["weapon_club"])
    
    session.commit()
    print(f"Successfully ingested clubs from {file_path}")


def migrate_from_dict_to_db(fencers_dict: dict, session: Session = None):
    """
    Migrate data from old dictionary-based storage to database.
    
    This helper function is useful if you have existing data in dictionary format
    (from the old class-based approach) and want to migrate it to the database.
    
    Args:
        fencers_dict: Dictionary mapping fencer_id to FencerID objects (old format)
        session: Optional database session
    """
    if session is None:
        with get_session_context() as session:
            _migrate_impl(fencers_dict, session)
    else:
        _migrate_impl(fencers_dict, session)


def _migrate_impl(fencers_dict: dict, session: Session):
    """
    Internal migration implementation.
    
    Args:
        fencers_dict: Dictionary of old FencerID objects
        session: Active database session
    """
    clubs_created = {}
    
    for fencer_id, old_fencer in fencers_dict.items():
        # Check if club exists
        if old_fencer.club_id and old_fencer.club_id not in clubs_created:
            existing_club = session.query(Club).filter_by(club_id=old_fencer.club_id).first()
            if existing_club is None:
                club = Club(
                    club_id=old_fencer.club_id,
                    club_name=old_fencer.club_id,
                    status="Active"
                )
                session.add(club)
                clubs_created[old_fencer.club_id] = club
        
        # Check if fencer exists
        existing_fencer = session.query(Fencer).filter_by(fencer_id=old_fencer.id).first()
        if existing_fencer is None:
            # Convert old FencerID to new Fencer model
            fencer = Fencer(
                fencer_id=old_fencer.id,
                first_name=old_fencer.first_name,
                last_name=old_fencer.last_name,
                dob=old_fencer.dob,
                gender=old_fencer.gender,
                weapon=old_fencer.weapon,
                club_id=old_fencer.club_id
            )
            
            # Migrate ranking points
            for bracket_name, old_ranking in old_fencer.rankings.items():
                ranking = fencer.get_ranking_for_bracket(bracket_name)
                if ranking:
                    ranking.points = old_ranking.points
            
            session.add(fencer)
    
    session.commit()
    print(f"Successfully migrated {len(fencers_dict)} fencers to database")
