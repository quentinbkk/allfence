"""
Configuration settings for AllFence application.
Handles environment-specific settings for development and production.
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Base configuration."""
    
    # Flask settings
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
    
    # Database settings
    DATABASE_URL = os.getenv('DATABASE_URL')
    
    # If DATABASE_URL is not set, use SQLite for local development
    if not DATABASE_URL:
        import os.path as path
        db_dir = path.join(path.dirname(__file__), 'data', 'database')
        os.makedirs(db_dir, exist_ok=True)
        db_path = path.join(db_dir, 'fencing_management.db')
        DATABASE_URL = f"sqlite:///{db_path}"
    
    # Fix for Render/Heroku DATABASE_URL (postgres:// -> postgresql://)
    if DATABASE_URL and DATABASE_URL.startswith('postgres://'):
        DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)
    
    # CORS settings
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', '*').split(',')
    
    # JWT settings
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', SECRET_KEY)
    JWT_ALGORITHM = 'HS256'
    JWT_EXPIRATION_HOURS = 24
    
    # Server settings
    HOST = os.getenv('HOST', '0.0.0.0')
    PORT = int(os.getenv('PORT', 5001))


class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True


class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False


# Select config based on environment
ENV = os.getenv('FLASK_ENV', 'development')
if ENV == 'production':
    config = ProductionConfig()
else:
    config = DevelopmentConfig()
