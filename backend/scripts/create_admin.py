"""
Admin User Creation Script

Creates a default admin user for the AllFence system with login credentials.
This user has full access to all system features and can authenticate via the API.

Default credentials:
- Username: admin
- Password: admin123
- Email: admin@allfence.com

Run this script once during initial setup or when you need to recreate the admin user.
"""
import sys
import os
# Add parent directory to path to import src modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.database import get_session_context
from src.models import User

def create_admin():
    """
    Create default admin user account.
    
    This function creates an admin user with predefined credentials.
    If the admin user already exists, it does nothing (idempotent operation).
    
    The admin user can:
    - Login to the system via /api/auth/login
    - Access all protected API endpoints
    - View all data in the system
    
    Security Note: Change the default password in production!
    """
    with get_session_context() as db:
        # Check if admin user already exists
        admin = db.query(User).filter(User.username == 'admin').first()
        
        if admin:
            print("✓ Admin user already exists")
            return
        
        # Create new admin user with predefined credentials
        admin = User(
            username='admin',
            email='admin@allfence.com',
            is_admin=True  # Grant admin privileges
        )
        # Hash and store the password securely (uses werkzeug security)
        admin.set_password('admin123')
        
        # Save to database
        db.add(admin)
        db.commit()
        
        print("✅ Admin user created successfully!")
        print("   Username: admin")
        print("   Password: admin123")
        print("\n⚠️  IMPORTANT: Change this password in production!")

if __name__ == '__main__':
    # Allow script to be run directly: python scripts/create_admin.py
    create_admin()
