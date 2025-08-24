from datetime import datetime
import uuid

class VoiceSession:
    """Voice session model for Supabase integration"""
    
    def __init__(self, id=None, user_id=None, audio_file_path=None, 
                 embeddings=None, quality_metrics=None, user_context=None, 
                 created_at=None):
        self.id = id or str(uuid.uuid4())
        self.user_id = user_id
        self.audio_file_path = audio_file_path
        self.embeddings = embeddings  # 512-dimensional vector
        self.quality_metrics = quality_metrics or {}
        self.user_context = user_context or {}
        self.created_at = created_at or datetime.now()
    
    @classmethod
    def from_dict(cls, data):
        """Create a VoiceSession instance from dictionary data"""
        if not data:
            return None
            
        return cls(
            id=data.get('id'),
            user_id=data.get('user_id'),
            audio_file_path=data.get('audio_file_path'),
            embeddings=data.get('embeddings'),
            quality_metrics=data.get('quality_metrics', {}),
            user_context=data.get('user_context', {}),
            created_at=data.get('created_at')
        )
    
    def to_dict(self):
        """Convert VoiceSession instance to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'audio_file_path': self.audio_file_path,
            'embeddings': self.embeddings,
            'quality_metrics': self.quality_metrics,
            'user_context': self.user_context,
            'created_at': self.created_at
        }
