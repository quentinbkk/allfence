"""
Database Configuration and Session Management

This module handles database connection, session creation, and initialization.
It provides a centralized way to manage database connections throughout the application.
Supports both SQLite (development) and PostgreSQL (production).
"""

from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool, NullPool
from contextlib import contextmanager
from .models import Base
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Get database URL from environment variable or use SQLite for local development
DATABASE_URL = os.getenv('DATABASE_URL')

if not DATABASE_URL:
    # SQLite fallback for local development
    db_dir = os.path.join(os.path.dirname(__file__), '..', 'data', 'database')
    os.makedirs(db_dir, exist_ok=True)
    db_path = os.path.join(db_dir, 'fencing_management.db')
    DATABASE_URL = f"sqlite:///{db_path}"
    logger.info(f"Using SQLite database at {db_path}")
else:
    # Fix for Render/Heroku postgres:// URLs
    if DATABASE_URL.startswith('postgres://'):
        DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)
    logger.info("Using PostgreSQL database from environment")

# Determine if we're using SQLite or PostgreSQL
is_sqlite = 'sqlite' in DATABASE_URL

# Create the database engine
# Different settings for SQLite vs PostgreSQL
if is_sqlite:
    engine = create_engine(
        DATABASE_URL,
        echo=False,
        future=True,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
else:
    # PostgreSQL configuration
    engine = create_engine(
        DATABASE_URL,
        echo=False,
        future=True,
        pool_pre_ping=True,  # Verify connections before using
        pool_size=10,
        max_overflow=20,
    )

# Enable SQLite foreign keys (important for referential integrity)
if is_sqlite:
    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_conn, connection_record):
        """Enable foreign key constraints for SQLite"""
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
        db_location = DATABASE_URL if not is_sqlite else db_path
        logger.info(f"Database initialized successfully at {db_location}")
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

