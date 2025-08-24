from datetime import datetime
import uuid

class UserFeedback:
    """User feedback model for Supabase integration"""
    
    def __init__(self, id=None, session_id=None, actual_glucose=None,
                 feedback_rating=None, comments=None, created_at=None):
        self.id = id or str(uuid.uuid4())
        self.session_id = session_id
        self.actual_glucose = actual_glucose
        self.feedback_rating = feedback_rating
        self.comments = comments
        self.created_at = created_at or datetime.now()
    
    @classmethod
    def from_dict(cls, data):
        """Create a UserFeedback instance from dictionary data"""
        if not data:
            return None
            
        return cls(
            id=data.get('id'),
            session_id=data.get('session_id'),
            actual_glucose=data.get('actual_glucose'),
            feedback_rating=data.get('feedback_rating'),
            comments=data.get('comments'),
            created_at=data.get('created_at')
        )
    
    def to_dict(self):
        """Convert UserFeedback instance to dictionary"""
        return {
            'id': self.id,
            'session_id': self.session_id,
            'actual_glucose': self.actual_glucose,
            'feedback_rating': self.feedback_rating,
            'comments': self.comments,
            'created_at': self.created_at
        }
