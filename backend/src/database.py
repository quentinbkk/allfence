"""
Database Configuration and Session Management

This module handles database connection, session creation, and initialization.
It provides a centralized way to manage database connections throughout the application.
"""

from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from contextlib import contextmanager
from .models import Base
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database file path - SQLite database stored as a file
# Store database in data/database directory
db_dir = os.path.join(os.path.dirname(__file__), '..', 'data', 'database')
os.makedirs(db_dir, exist_ok=True)
db_path = os.path.join(db_dir, 'fencing_management.db')
DATABASE_URL = f"sqlite:///{db_path}"

# For PostgreSQL, the URL would look like:
# DATABASE_URL = "postgresql://username:password@localhost/fencing_db"

# Create the database engine
# echo=False to disable SQL query logging (set to True for debugging)
# future=True enables SQLAlchemy 2.0 style (recommended for new code)
# connect_args for SQLite to handle threading
engine = create_engine(
    DATABASE_URL,
    echo=False,  # Set to True to see SQL queries in console
    future=True,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {},
)

# Enable SQLite foreign keys (important for referential integrity)
@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_conn, connection_record):
    """Enable foreign key constraints for SQLite"""
    if "sqlite" in DATABASE_URL:
        cursor = dbapi_conn.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

# Session factory - creates new database sessions
# autocommit=False means changes must be explicitly committed
# autoflush=True means SQLAlchemy automatically flushes changes before queries
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


def init_db():
    """
    Initialize the database by creating all tables.
    
    This function creates all tables defined in the models (Fencer, Club, Ranking).
    If tables already exist, this does nothing (won't delete existing data).
    
    Call this once at the start of your application or when setting up a new database.
    """
    try:
        # Create all tables defined in Base (all our models)
        Base.metadata.create_all(bind=engine)
        logger.info(f"Database initialized successfully at {db_path}")
    except Exception as e:
        logger.error(f"Error initializing database: {e}")
        raise


def get_session() -> Session:
    """
    Create and return a new database session.
    
    This function creates a fresh database session that you can use to
    query and modify data. Remember to commit() changes and close() the session
    when done.
    
    Returns:
        SQLAlchemy Session object
        
    Example:
        session = get_session()
        try:
            # Do database operations
            fencer = session.query(Fencer).filter_by(fencer_id=123).first()
            session.commit()
        finally:
            session.close()
    """
    return SessionLocal()


@contextmanager
def get_session_context():
    """
    Context manager for database sessions.
    
    This ensures the session is properly closed even if an error occurs.
    Use with the 'with' statement for automatic cleanup.
    
    Returns:
        Session context manager
        
    Example:
        with get_session_context() as session:
            fencer = session.query(Fencer).filter_by(fencer_id=123).first()
            session.commit()
    
    Yields:
        SQLAlchemy Session object
    """
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception as e:
        session.rollback()
        logger.error(f"Database error: {e}")
        raise
    finally:
        session.close()


def reset_db():
    """
    WARNING: This will delete all data!
    
    Drop all tables and recreate them from scratch.
    Only use this during development/testing, never in production!
    """
    try:
        logger.warning("Dropping all database tables...")
        # Drop all tables
        Base.metadata.drop_all(bind=engine)
        logger.info("All tables dropped.")
        
        # Recreate all tables
        Base.metadata.create_all(bind=engine)
        logger.info("All tables recreated.")
    except Exception as e:
        logger.error(f"Error resetting database: {e}")
        raise

