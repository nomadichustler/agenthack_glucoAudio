import os
from supabase import create_client, Client
from app.models.user import User
from app.models.voice_session import VoiceSession
from app.models.prediction import GlucosePrediction
from app.models.feedback import UserFeedback
import json

class SupabaseManager:
    """Service class for Supabase database interactions"""
    
    def __init__(self):
        url = os.environ.get("SUPABASE_URL")
        key = os.environ.get("SUPABASE_ANON_KEY")
        if not url or not key:
            raise ValueError("SUPABASE_URL and SUPABASE_ANON_KEY environment variables must be set")
        self.supabase: Client = create_client(url, key)
    
    # User methods
    async def create_user(self, email, preferences=None):
        """Create a new user"""
        user_data = {
            'email': email,
            'preferences': preferences or {}
        }
        
        result = self.supabase.table('users').insert(user_data).execute()
        return User.from_dict(result.data[0] if result.data else None)
    
    async def get_user(self, user_id):
        """Get user by ID"""
        result = self.supabase.table('users').select('*').eq('id', user_id).execute()
        return User.from_dict(result.data[0] if result.data else None)
    
    async def update_user(self, user):
        """Update user information"""
        result = self.supabase.table('users').update(user.to_dict()).eq('id', user.id).execute()
        return User.from_dict(result.data[0] if result.data else None)
    
    # Voice session methods
    async def create_voice_session(self, user_id, audio_data, context):
        """Create new voice analysis session"""
        # Upload audio file to storage
        audio_file_path = await self._upload_audio(audio_data)
        
        # Assess audio quality
        quality_metrics = await self._assess_audio_quality(audio_data)
        
        # Convert context to JSON if it's not already
        if isinstance(context, dict):
            context_json = context
        else:
            try:
                context_json = json.loads(context)
            except:
                context_json = {'raw_context': str(context)}
        
        session_data = {
            'user_id': user_id,
            'audio_file_path': audio_file_path,
            'user_context': context_json,
            'quality_metrics': quality_metrics
        }
        
        result = self.supabase.table('voice_sessions').insert(session_data).execute()
        return VoiceSession.from_dict(result.data[0] if result.data else None)
    
    async def get_voice_session(self, session_id):
        """Get voice session by ID"""
        result = self.supabase.table('voice_sessions').select('*').eq('id', session_id).execute()
        return VoiceSession.from_dict(result.data[0] if result.data else None)
    
    async def update_voice_session(self, session):
        """Update voice session information"""
        result = self.supabase.table('voice_sessions').update(session.to_dict()).eq('id', session.id).execute()
        return VoiceSession.from_dict(result.data[0] if result.data else None)
    
    async def update_embeddings(self, session_id, embeddings):
        """Update voice embeddings for a session"""
        result = self.supabase.table('voice_sessions').update({
            'embeddings': embeddings
        }).eq('id', session_id).execute()
        return VoiceSession.from_dict(result.data[0] if result.data else None)
    
    # Prediction methods
    async def store_prediction(self, session_id, prediction_data):
        """Store glucose prediction results"""
        # Convert prediction_data to JSON if it's not already
        if isinstance(prediction_data, dict):
            prediction_json = prediction_data
        else:
            try:
                prediction_json = json.loads(prediction_data)
            except:
                prediction_json = {'raw_prediction': str(prediction_data)}
        
        # Extract confidence score from glucose_assessment if available
        confidence_score = None
        if isinstance(prediction_json, dict):
            if 'glucose_assessment' in prediction_json and 'confidence_score' in prediction_json['glucose_assessment']:
                confidence_score = prediction_json['glucose_assessment']['confidence_score']
            elif 'confidence_score' in prediction_json:
                confidence_score = prediction_json['confidence_score']
        
        prediction_record = {
            'session_id': session_id,
            'prediction_result': prediction_json,
            'confidence_score': confidence_score,
            'claude_response': prediction_json.get('raw_claude_response')
        }
        
        result = self.supabase.table('glucose_predictions').insert(prediction_record).execute()
        return GlucosePrediction.from_dict(result.data[0] if result.data else None)
    
    async def get_prediction(self, prediction_id):
        """Get prediction by ID"""
        result = self.supabase.table('glucose_predictions').select('*').eq('id', prediction_id).execute()
        return GlucosePrediction.from_dict(result.data[0] if result.data else None)
    
    async def get_prediction_by_session(self, session_id):
        """Get prediction by session ID"""
        result = self.supabase.table('glucose_predictions').select('*').eq('session_id', session_id).execute()
        return GlucosePrediction.from_dict(result.data[0] if result.data else None)
    
    # Feedback methods
    async def store_feedback(self, session_id, actual_glucose, feedback_rating, comments=None):
        """Store user feedback"""
        feedback_data = {
            'session_id': session_id,
            'actual_glucose': actual_glucose,
            'feedback_rating': feedback_rating,
            'comments': comments
        }
        
        result = self.supabase.table('user_feedback').insert(feedback_data).execute()
        return UserFeedback.from_dict(result.data[0] if result.data else None)
    
    # User history
    async def get_user_history(self, user_id, limit=50):
        """Retrieve user's analysis history"""
        result = (self.supabase
                .table('voice_sessions')
                .select('*, glucose_predictions(*)')
                .eq('user_id', user_id)
                .order('created_at', desc=True)
                .limit(limit)
                .execute())
        
        history = []
        for item in result.data:
            session = VoiceSession.from_dict(item)
            prediction = None
            if item.get('glucose_predictions'):
                prediction = GlucosePrediction.from_dict(item.get('glucose_predictions')[0])
            
            history.append({
                'session': session,
                'prediction': prediction
            })
            
        return history
    
    # Private helper methods
    async def _upload_audio(self, audio_data):
        """Upload audio file to Supabase storage"""
        # Generate a unique filename
        filename = f"audio_{str(os.urandom(4).hex())}.wav"
        
        # Upload to storage
        result = self.supabase.storage.from_('voice_samples').upload(
            path=filename,
            file=audio_data
        )
        
        # Return the path
        return f"voice_samples/{filename}"
    
    async def _assess_audio_quality(self, audio_data):
        """Assess audio quality metrics"""
        import tempfile
        import librosa
        import numpy as np
        
        # Save the audio data to a temporary file
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
            temp_path = temp_file.name
            audio_data.save(temp_path)
            
            try:
                # Load the audio file
                y, sr = librosa.load(temp_path, sr=None)
                
                # Calculate duration
                duration = librosa.get_duration(y=y, sr=sr)
                
                # Calculate signal-to-noise ratio
                # Use the ratio of signal power to the noise power
                signal_power = np.mean(y ** 2)
                noise_estimate = np.var(y) * 0.1  # Simple noise estimate
                snr = 10 * np.log10(signal_power / noise_estimate) if noise_estimate > 0 else 30.0
                
                # Calculate spectral centroid as a clarity measure
                cent = librosa.feature.spectral_centroid(y=y, sr=sr)[0]
                clarity_score = min(100, max(0, int(np.mean(cent) / 50)))
                
                # Calculate spectral bandwidth for spectral quality
                spec_bw = librosa.feature.spectral_bandwidth(y=y, sr=sr)[0]
                spectral_quality = min(100, max(0, int(100 - np.mean(spec_bw) / 100)))
                
                return {
                    'snr': float(snr),
                    'duration': float(duration),
                    'clarity': clarity_score,
                    'spectral_quality': spectral_quality
                }
            except Exception as e:
                print(f"Error assessing audio quality: {e}")
                # Return default values if analysis fails
                return {
                    'snr': 20.0,
                    'duration': 5.0,
                    'clarity': 70,
                    'spectral_quality': 75
                }
            finally:
                # Clean up the temporary file
                import os
                if os.path.exists(temp_path):
                    os.remove(temp_path)
