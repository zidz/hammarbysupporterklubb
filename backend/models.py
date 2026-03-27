"""User model for authentication."""
import json
import os
import bcrypt
from flask_login import UserMixin


class QueryProxy:
    """Proxy for SQLAlchemy-style queries."""
    
    def __init__(self, model_class):
        self.model_class = model_class
    
    def filter_by(self, **kwargs):
        """Filter by keyword arguments."""
        return QueryFilter(self.model_class, kwargs)
    
    def first(self):
        """Get first result."""
        users = self.model_class.load_all()
        if users:
            return users[0]
        return None


class QueryFilter:
    """Query filter for SQLAlchemy-style queries."""
    
    def __init__(self, model_class, filters):
        self.model_class = model_class
        self.filters = filters
    
    def first(self):
        """Get first matching result."""
        users = self.model_class.load_all()
        for user_data in users:
            match = True
            for key, value in self.filters.items():
                if user_data.get(key) != value:
                    match = False
                    break
            if match:
                return self.model_class._from_dict(user_data)
        return None


class User(UserMixin):
    """User model with JSON storage and bcrypt password hashing."""
    
    # SQLAlchemy-style query interface
    query = QueryProxy(None)  # Will be set after class definition
    
    def __init__(self, id, username, email, password_hash, role='member'):
        self.id = id
        self.username = username
        self.email = email
        self._password_hash = password_hash
        self.role = role
    
    @property
    def password(self):
        """Return password hash (for test compatibility)."""
        return self._password_hash
    
    @password.setter
    def password(self, value):
        """Set password hash."""
        self._password_hash = value
    
    @staticmethod
    def _from_dict(data):
        """Create User from dictionary."""
        return User(
            id=data['id'],
            username=data['username'],
            email=data['email'],
            password_hash=data['password_hash'],
            role=data.get('role', 'member')
        )
    
    @staticmethod
    def get_users_file():
        """Get path to users JSON file."""
        return os.path.join(os.path.dirname(__file__), 'data', 'users.json')
    
    @staticmethod
    def load_all():
        """Load all users from JSON file."""
        users_file = User.get_users_file()
        if not os.path.exists(users_file):
            return []
        
        try:
            with open(users_file, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return []
    
    @staticmethod
    def save_all(users_data):
        """Save all users to JSON file."""
        users_file = User.get_users_file()
        os.makedirs(os.path.dirname(users_file), exist_ok=True)
        
        with open(users_file, 'w') as f:
            json.dump(users_data, f, indent=2)
    
    @staticmethod
    def find_by_username(username):
        """Find user by username."""
        users = User.load_all()
        for user_data in users:
            if user_data['username'] == username:
                return User._from_dict(user_data)
        return None
    
    @staticmethod
    def find_by_id(user_id):
        """Find user by ID."""
        users = User.load_all()
        for user_data in users:
            if user_data['id'] == user_id:
                return User._from_dict(user_data)
        return None
    
    def verify_password(self, password):
        """Verify password against hash."""
        password_bytes = password.encode('utf-8')
        hash_bytes = self._password_hash.encode('utf-8')
        return bcrypt.checkpw(password_bytes, hash_bytes)
    
    @staticmethod
    def create_user(username, email, password, role='member'):
        """Create a new user with hashed password."""
        users = User.load_all()
        
        # Check if username exists
        if User.find_by_username(username):
            raise ValueError("Username already exists")
        
        # Generate new ID
        new_id = max([u['id'] for u in users], default=0) + 1
        
        # Hash password
        password_bytes = password.encode('utf-8')
        salt = bcrypt.gensalt()
        password_hash = bcrypt.hashpw(password_bytes, salt).decode('utf-8')
        
        # Create user data
        user_data = {
            'id': new_id,
            'username': username,
            'email': email,
            'password_hash': password_hash,
            'role': role
        }
        
        users.append(user_data)
        User.save_all(users)
        
        return User._from_dict(user_data)
    
    def to_dict(self):
        """Convert user to dictionary (without password hash)."""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'role': self.role
        }

# Set query proxy after class definition
User.query = QueryProxy(User)
