#!/usr/bin/env python3
"""Create admin user with password 'admin' for testing."""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from backend.models import User

def create_admin():
    """Create admin user with password 'admin'."""
    try:
        # Try to create admin user
        user = User.create_user(
            username='admin',
            email='admin@hammarby.se',
            password='admin',
            role='admin'
        )
        print(f"Admin user created: {user.username}")
    except ValueError as e:
        print(f"Admin user already exists: {e}")

if __name__ == '__main__':
    create_admin()
