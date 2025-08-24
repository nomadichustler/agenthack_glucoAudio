from app.services.supabase_service import SupabaseManager

class DatabaseAgent:
    """Agent for secure storage and retrieval of user data"""
    
    def __init__(self):
        self.db_manager = SupabaseManager()
    
    async def store_results(self, session_id, user_id, embeddings, prediction, voice_response, audio_quality):
        """Store analysis results and session data"""
        try:
            # First, create or update the voice session
            session = await self.db_manager.create_voice_session(
                session_id=session_id,
                user_id=user_id,
                embeddings=embeddings,
                audio_quality=audio_quality
            )
            
            # Then store the prediction
            if prediction and prediction.get('glucose_prediction'):
                prediction_data = prediction.get('glucose_prediction')
                stored_prediction = await self.db_manager.store_prediction(
                    session_id=session_id,
                    prediction_data=prediction_data
                )
                
                # Store voice response if available
                if voice_response:
                    await self.db_manager.store_voice_response(
                        session_id=session_id,
                        voice_response_url=voice_response.get('voice_response'),
                        voice_script=voice_response.get('voice_script')
                    )
                
                return {
                    "success": True,
                    "session_id": session_id,
                    "prediction_id": stored_prediction.get('id') if stored_prediction else None,
                    "voice_response_url": voice_response.get('voice_response') if voice_response else None
                }
            else:
                return {
                    "success": False,
                    "error": "Missing prediction data"
                }
            
        except Exception as e:
            print(f"Error storing results in database: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_user_history(self, user_id, limit=50):
        """Get user history"""
        try:
            # Get history from database
            history = await self.db_manager.get_user_history(
                user_id=user_id,
                limit=limit
            )
            
            return {
                "success": True,
                "history": history
            }
            
        except Exception as e:
            print(f"Error retrieving user history: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def store_feedback(self, session_id, actual_glucose, feedback_rating, comments=None):
        """Store user feedback"""
        try:
            # Store feedback in database
            feedback = await self.db_manager.store_feedback(
                session_id=session_id,
                actual_glucose=actual_glucose,
                feedback_rating=feedback_rating,
                comments=comments
            )
            
            return {
                "success": True,
                "feedback_id": feedback.get('id') if feedback else None
            }
            
        except Exception as e:
            print(f"Error storing feedback: {e}")
            return {
                "success": False,
                "error": str(e)
            }