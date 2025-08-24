from datetime import datetime
import uuid

class GlucosePrediction:
    """Glucose prediction model for Supabase integration"""
    
    def __init__(self, id=None, session_id=None, prediction_result=None,
                 confidence_score=None, claude_response=None, created_at=None):
        self.id = id or str(uuid.uuid4())
        self.session_id = session_id
        self.prediction_result = prediction_result or {}
        self.confidence_score = confidence_score
        self.claude_response = claude_response or {}
        self.created_at = created_at or datetime.now()
    
    @classmethod
    def from_dict(cls, data):
        """Create a GlucosePrediction instance from dictionary data"""
        if not data:
            return None
            
        return cls(
            id=data.get('id'),
            session_id=data.get('session_id'),
            prediction_result=data.get('prediction_result', {}),
            confidence_score=data.get('confidence_score'),
            claude_response=data.get('claude_response', {}),
            created_at=data.get('created_at')
        )
    
    def to_dict(self):
        """Convert GlucosePrediction instance to dictionary"""
        return {
            'id': self.id,
            'session_id': self.session_id,
            'prediction_result': self.prediction_result,
            'confidence_score': self.confidence_score,
            'claude_response': self.claude_response,
            'created_at': self.created_at
        }
