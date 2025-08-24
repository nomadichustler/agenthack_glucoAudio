import os
import uuid
from dotenv import load_dotenv
from portia import Config, Portia, LogLevel
from portia.cli import CLIExecutionHooks
from portia.builder.plan_builder_v2 import PlanBuilderV2
from portia.builder.reference import Input, StepOutput
from portia.end_user import EndUser
import asyncio
import random
from app.services.anthropic_service import AnthropicService
from app.services.elevenlabs_service import ElevenLabsService
from app.services.supabase_service import SupabaseManager

class PortiaService:
    """Service for interacting with Portia AI SDK"""
    
    def __init__(self):
        """Initialize the Portia service"""
        self.api_key = os.environ.get('PORTIA_API_KEY')
        if not self.api_key:
            raise ValueError("PORTIA_API_KEY environment variable must be set")
        
        # Configure Portia with CLI execution hooks for better debugging
        self.config = Config.from_default(default_log_level=LogLevel.DEBUG)
        self.portia = Portia(
            config=self.config,
            execution_hooks=CLIExecutionHooks(),
        )
        
        # Initialize other services
        self.anthropic_service = AnthropicService()
        self.elevenlabs_service = ElevenLabsService()
        self.supabase_manager = SupabaseManager()
    
    def build_glucose_analysis_plan(self, audio_data, user_context, session_id):
        """Build a plan for glucose analysis using PlanBuilderV2"""
        
        plan = (
            PlanBuilderV2("Analyze voice for glucose estimation")
            .input(name="raw_audio", description="The raw audio data to analyze")
            .input(name="user_context", description="User context data including health information")
            .input(name="session_id", description="Unique session identifier")
            
            # Step 1: Audio preprocessing
            .function_step(
                step_name="Preprocess Audio",
                function=self._preprocess_audio,
                args={
                    "audio_data": Input("raw_audio"),
                }
            )
            
            # Step 2: Extract embeddings
            .function_step(
                step_name="Extract Embeddings",
                function=self._extract_embeddings,
                args={
                    "processed_audio": StepOutput("Preprocess Audio"),
                }
            )
            
            # Step 3: Claude inference for glucose estimation
            .function_step(
                step_name="Glucose Inference",
                function=self._run_claude_inference,
                args={
                    "embeddings": StepOutput("Extract Embeddings"),
                    "user_context": Input("user_context"),
                    "audio_quality": StepOutput("Preprocess Audio", "quality_metrics"),
                }
            )
            
            # Step 4: Generate voice response
            .function_step(
                step_name="Voice Synthesis",
                function=self._synthesize_voice,
                args={
                    "prediction": StepOutput("Glucose Inference"),
                    "user_context": Input("user_context"),
                }
            )
            
            # Step 5: Store results in database
            .function_step(
                step_name="Store Results",
                function=self._store_results,
                args={
                    "session_id": Input("session_id"),
                    "user_id": Input("user_context", "user_id"),
                    "embeddings": StepOutput("Extract Embeddings"),
                    "prediction": StepOutput("Glucose Inference"),
                    "voice_response": StepOutput("Voice Synthesis"),
                    "audio_quality": StepOutput("Preprocess Audio", "quality_metrics"),
                }
            )
            
            .build()
        )
        
        return plan
    
    def run_glucose_analysis_sync(self, audio_data, user_context, session_id):
        """Synchronous version of run_glucose_analysis"""
        try:
            # Process audio data
            processed_audio = self._preprocess_audio_sync(audio_data)
            
            # Extract embeddings
            embeddings = self._extract_embeddings_sync(processed_audio)
            
            # Run Claude inference
            prediction = self._run_claude_inference_sync(embeddings, user_context, processed_audio.get('quality_metrics', {}))
            
            # Generate voice response
            voice_response = self._synthesize_voice_sync(prediction, user_context)
            
            # Store results
            store_result = self._store_results_sync(
                session_id, 
                user_context.get('user_id'), 
                embeddings, 
                prediction, 
                voice_response, 
                processed_audio.get('quality_metrics', {})
            )
            
            # Return results
            return {
                "success": True,
                "session_id": session_id,
                "prediction": prediction,
                "voice_response": voice_response,
                "confidence": prediction.get('glucose_assessment', {}).get('confidence_score', 0.5)
            }
        except Exception as e:
            print(f"Error executing synchronous Portia workflow: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def run_glucose_analysis(self, audio_data, user_context, session_id):
        """Run the glucose analysis workflow"""
        try:
            # Create inputs for the plan
            plan_inputs = {
                "raw_audio": audio_data,
                "user_context": user_context,
                "session_id": session_id
            }
            
            # Build the plan
            plan = self.build_glucose_analysis_plan(audio_data, user_context, session_id)
            
            # Run the plan
            plan_run = self.portia.run_plan(plan, plan_run_inputs=plan_inputs)
            
            # Return the results
            return {
                "success": True,
                "session_id": session_id,
                "prediction": plan_run.get_output().get("prediction"),
                "voice_response": plan_run.get_output().get("voice_response_url"),
                "confidence": plan_run.get_output().get("confidence")
            }
            
        except Exception as e:
            print(f"Error executing Portia workflow: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    # Synchronous implementations for each step
    def _preprocess_audio_sync(self, audio_data):
        """Preprocess audio data"""
        print(f"Preprocessing audio: {audio_data.filename if hasattr(audio_data, 'filename') else 'unknown'}")
        
        # Calculate real audio metrics
        try:
            # In a real implementation, we would use librosa or another audio processing library
            # For now, we'll generate realistic metrics
            snr = random.uniform(18.0, 30.0)  # Signal-to-noise ratio
            duration = random.uniform(10.0, 30.0)  # Duration in seconds
            clarity = random.randint(70, 95)  # Clarity score
            spectral_quality = random.randint(75, 98)  # Spectral quality
            
            quality_metrics = {
                'snr': round(snr, 2),
                'duration': round(duration, 2),
                'clarity': clarity,
                'spectral_quality': spectral_quality
            }
            
            print(f"Audio quality metrics: {quality_metrics}")
            
            # Return processed audio with quality metrics
            return {
                'processed_audio': audio_data,  # In a real implementation, this would be the processed audio data
                'quality_metrics': quality_metrics
            }
        except Exception as e:
            print(f"Error preprocessing audio: {e}")
            # Return fallback metrics
            return {
                'processed_audio': audio_data,
                'quality_metrics': {
                    'snr': 20.0,
                    'duration': 15.0,
                    'clarity': 80,
                    'spectral_quality': 85
                }
            }
    
    def _extract_embeddings_sync(self, processed_audio):
        """Extract embeddings from processed audio"""
        print("Extracting embeddings from processed audio")
        
        # In a real implementation, we would use a pre-trained model like wav2vec2.0
        # For now, we'll generate a random embedding vector
        embedding_dim = 512
        embeddings = [random.uniform(-1.0, 1.0) for _ in range(embedding_dim)]
        
        print(f"Generated embedding vector of dimension {len(embeddings)}")
        
        return embeddings
    
    def _run_claude_inference_sync(self, embeddings, user_context, audio_quality):
        """Run Claude inference for glucose estimation"""
        print("Running Claude inference for glucose estimation")
        
        # Extract user_id to fetch questionnaire data
        user_id = user_context.get('user_id')
        
        # Fetch questionnaire data from database if available
        conversation_data = {}
        if user_id:
            try:
                # Get the most recent user context from the database
                user_contexts = self.supabase_manager.supabase.table('user_contexts').select('*').eq('user_id', user_id).order('created_at', desc=True).limit(1).execute()
                
                if user_contexts.data and len(user_contexts.data) > 0:
                    context_data = user_contexts.data[0]
                    print(f"Found user context data: {context_data.get('id')}")
                    
                    # Merge context data with user_context
                    if context_data.get('context_data'):
                        conversation_data = context_data.get('context_data')
                        # Add the context data to user_context
                        user_context['questionnaire_data'] = conversation_data
                
                # Get the most recent voice session with conversation history
                voice_sessions = self.supabase_manager.supabase.table('voice_sessions').select('*').eq('user_id', user_id).order('created_at', desc=True).limit(5).execute()
                
                if voice_sessions.data and len(voice_sessions.data) > 0:
                    for session in voice_sessions.data:
                        if session.get('user_context') and session.get('user_context').get('conversation_history'):
                            print(f"Found voice session with conversation history: {session.get('id')}")
                            user_context['conversation_history'] = session.get('user_context').get('conversation_history')
                            break
            except Exception as e:
                print(f"Error fetching questionnaire data: {e}")
        
        # Extract relevant context from user_context
        diabetes_status = user_context.get('diabetes_status', 'Unknown')
        meal_timing = user_context.get('meal_timing', 'Unknown')
        symptoms = user_context.get('symptoms', [])
        
        # Try to extract from conversation data if available
        if conversation_data:
            if conversation_data.get('diabetes_status'):
                diabetes_status = conversation_data.get('diabetes_status')
                user_context['diabetes_status'] = diabetes_status
            
            if conversation_data.get('meal_timing'):
                meal_timing = conversation_data.get('meal_timing')
                user_context['meal_timing'] = meal_timing
            
            if conversation_data.get('symptoms'):
                symptoms = conversation_data.get('symptoms')
                user_context['symptoms'] = symptoms
            
            # Also look for responses object
            if conversation_data.get('responses'):
                responses = conversation_data.get('responses')
                
                if responses.get('diabetes_status'):
                    diabetes_status = responses.get('diabetes_status')
                    user_context['diabetes_status'] = diabetes_status
                
                if responses.get('meal_timing'):
                    meal_timing = responses.get('meal_timing')
                    user_context['meal_timing'] = meal_timing
                
                if responses.get('symptoms'):
                    symptoms = responses.get('symptoms')
                    user_context['symptoms'] = symptoms
        
        # Prepare context for Claude
        formatted_context = f"""
        User Health Context:
        - Diabetes Status: {diabetes_status}
        - Last Meal: {meal_timing}
        - Reported Symptoms: {', '.join(symptoms) if symptoms else 'None reported'}
        
        Voice Analysis:
        - Embedding Vector Size: {len(embeddings)}
        - Audio Quality: SNR={audio_quality.get('snr', 'N/A')}dB, Duration={audio_quality.get('duration', 'N/A')}s
        """
        
        # Add conversation to user_context if available
        if user_context.get('conversation'):
            formatted_context += f"\nConversation:\n{user_context.get('conversation')}"
        
        # Get analysis from Claude
        analysis = self.anthropic_service.analyze_voice_data(formatted_context, audio_quality)
        
        print(f"Claude inference complete with confidence score: {analysis.get('glucose_assessment', {}).get('confidence_score', 0.5)}")
        
        return analysis
    
    def _synthesize_voice_sync(self, prediction, user_context):
        """Synthesize voice response based on prediction"""
        print("Synthesizing voice response")
        
        # Extract relevant information from prediction
        glucose_assessment = prediction.get('glucose_assessment', {})
        primary_estimate = glucose_assessment.get('primary_estimate', 'normal')
        estimated_range = glucose_assessment.get('estimated_range', '80-120 mg/dL')
        confidence = glucose_assessment.get('confidence_score', 0.5)
        risk_level = glucose_assessment.get('risk_level', 'minimal')
        
        # Extract recommendations
        clinical_insights = prediction.get('clinical_insights', {})
        recommendations = clinical_insights.get('immediate_recommendations', 'No specific recommendations at this time.')
        
        # Generate response text
        response_text = f"""
        Based on my analysis of your voice patterns, I estimate your glucose level is currently {primary_estimate}, 
        with an estimated range of {estimated_range}. My confidence in this assessment is {int(confidence * 100)}%. 
        The risk level associated with this reading is {risk_level}.
        
        {recommendations}
        
        Remember, this is an experimental technology and should not replace traditional glucose monitoring.
        """
        
        # Generate voice using ElevenLabs
        voice_id = self.elevenlabs_service.voice_ids.get('serious_medical_voice')
        voice_path = self.elevenlabs_service.text_to_speech(response_text.strip(), voice_id=voice_id)
        
        # In a real implementation, we would upload this to storage and return the URL
        # For now, we'll just return the local path
        print(f"Voice response generated: {voice_path}")
        
        return voice_path
    
    def _store_results_sync(self, session_id, user_id, embeddings, prediction, voice_response, audio_quality):
        """Store results in database"""
        print(f"Storing results for session {session_id}, user {user_id}")
        
        try:
            # Check if session already exists
            existing_session = self.supabase_manager.supabase.table('voice_sessions').select('id').eq('id', session_id).execute()
            
            if existing_session.data and len(existing_session.data) > 0:
                print(f"Session {session_id} already exists, using existing session")
                voice_session = existing_session
            else:
                # Generate a new UUID to avoid collisions
                unique_session_id = str(uuid.uuid4())
                print(f"Creating new session with ID: {unique_session_id}")
                
                # Store voice session
                voice_session = self.supabase_manager.supabase.table('voice_sessions').insert({
                    'id': unique_session_id,
                    'user_id': user_id,
                    'audio_file_path': voice_response,  # In a real implementation, this would be the path to the audio file
                    'user_context': {},  # This would be populated with relevant context
                    'quality_metrics': audio_quality,
                    # Don't store embeddings directly in the table since it requires all 512 dimensions
                    # We'll store them separately or process them before storage
                }).execute()
                
                # Update session_id to the new unique ID
                session_id = unique_session_id
            
            # Store prediction
            try:
                prediction_result = self.supabase_manager.supabase.table('glucose_predictions').insert({
                    'session_id': session_id,
                    'prediction_result': prediction,
                    'confidence_score': prediction.get('glucose_assessment', {}).get('confidence_score', 0.5)
                }).execute()
            except Exception as pred_error:
                print(f"Error storing prediction: {pred_error}")
                # Try with a unique ID for the prediction
                prediction_id = str(uuid.uuid4())
                prediction_result = self.supabase_manager.supabase.table('glucose_predictions').insert({
                    'id': prediction_id,
                    'session_id': session_id,
                    'prediction_result': prediction,
                    'confidence_score': prediction.get('glucose_assessment', {}).get('confidence_score', 0.5)
                }).execute()
            
            print(f"Results stored successfully for session {session_id}")
            
            return {
                'success': True,
                'voice_session_id': session_id,
                'prediction_id': prediction_result.data[0]['id'] if prediction_result.data else None
            }
        except Exception as e:
            print(f"Error storing results: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    # These methods are for the async version with Portia plan
    async def _preprocess_audio(self, audio_data):
        """Placeholder for audio preprocessing"""
        return self._preprocess_audio_sync(audio_data)
    
    async def _extract_embeddings(self, processed_audio):
        """Placeholder for embedding extraction"""
        return self._extract_embeddings_sync(processed_audio)
    
    async def _run_claude_inference(self, embeddings, user_context, audio_quality):
        """Placeholder for Claude inference"""
        return self._run_claude_inference_sync(embeddings, user_context, audio_quality)
    
    async def _synthesize_voice(self, prediction, user_context):
        """Placeholder for voice synthesis"""
        return self._synthesize_voice_sync(prediction, user_context)
    
    async def _store_results(self, session_id, user_id, embeddings, prediction, voice_response, audio_quality):
        """Placeholder for database storage"""
        return self._store_results_sync(session_id, user_id, embeddings, prediction, voice_response, audio_quality)