from datetime import datetime
import uuid

class User:
    """User model for Supabase integration"""
    
    def __init__(self, id=None, email=None, created_at=None, last_active=None, preferences=None):
        self.id = id or str(uuid.uuid4())
        self.email = email
        self.created_at = created_at or datetime.now()
        self.last_active = last_active or datetime.now()
        self.preferences = preferences or {}
    
    @classmethod
    def from_dict(cls, data):
        """Create a User instance from dictionary data"""
        if not data:
            return None
            
        return cls(
            id=data.get('id'),
            email=data.get('email'),
            created_at=data.get('created_at'),
            last_active=data.get('last_active'),
            preferences=data.get('preferences', {})
        )
    
    def to_dict(self):
        """Convert User instance to dictionary"""
        return {
            'id': self.id,
            'email': self.email,
            'created_at': self.created_at,
            'last_active': self.last_active,
            'preferences': self.preferences
        }
    
    def update_last_active(self):
        """Update the last active timestamp"""
        self.last_active = datetime.now()
        return self
