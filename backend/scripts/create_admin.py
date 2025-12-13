"""
Create default admin user for AllFence system
Run this once to create admin account
"""
import sys
import os
# Add parent directory to path to import src modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.database import get_session_context
from src.models import User

def create_admin():
    with get_session_context() as db:
        # Check if admin exists
        admin = db.query(User).filter(User.username == 'admin').first()
        
        if admin:
            print("✓ Admin user already exists")
            return
        
        # Create admin user
        admin = User(
            username='admin',
            email='admin@allfence.com',
            is_admin=True
        )
        admin.set_password('admin123')
        
        db.add(admin)
        db.commit()
        
        print("✅ Admin user created successfully!")
        print("   Username: admin")
        print("   Password: admin123")
        print("\n⚠️  IMPORTANT: Change this password in production!")

if __name__ == '__main__':
    create_admin()
