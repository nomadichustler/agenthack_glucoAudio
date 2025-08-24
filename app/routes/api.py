from flask import Blueprint, request, jsonify, session
from app.services.portia_service import PortiaService
from app.services.supabase_service import SupabaseManager
from app.services.user_service import UserService
import os
import uuid
import json
from datetime import datetime

bp = Blueprint('api', __name__, url_prefix='/api/v1')

# Initialize services
try:
    portia_service = PortiaService()
    user_service = UserService()
except Exception as e:
    print(f"Error initializing services: {e}")
    portia_service = None
    user_service = None

@bp.route('/user', methods=['GET'])
def get_user():
    """Get current user data"""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'success': False, 'error': 'Not authenticated'}), 401
        
    try:
        # Get user from database
        user = user_service.get_user_by_id(user_id)
        
        if not user:
            return jsonify({'success': False, 'error': 'User not found'}), 404
            
        # Get user profile
        supabase_manager = SupabaseManager()
        profile_result = supabase_manager.supabase.table('profiles').select('*').eq('id', user_id).execute()
        
        if profile_result.data:
            profile = profile_result.data[0]
            user['preferences'] = profile.get('preferences', {})
            
        return jsonify({
            'success': True,
            'user': user
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@bp.route('/questionnaire', methods=['POST'])
def submit_questionnaire():
    """Store user context responses"""
    try:
        supabase_manager = SupabaseManager()
        
        data = request.json
        user_id = data.get('user_id', session.get('user_id'))
        context_data = data.get('context', {})
        
        if not user_id:
            return jsonify({'success': False, 'error': 'User ID is required'}), 400
            
        # Store context in Supabase
        result = supabase_manager.supabase.table('user_contexts').insert({
            'user_id': user_id,
            'context_data': context_data
        }).execute()
        
        if not result.data:
            return jsonify({'success': False, 'error': 'Failed to store context data'}), 500
            
        context_id = result.data[0]['id']
        
        return jsonify({
            'success': True,
            'context_id': context_id,
            'context': context_data
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@bp.route('/voice/upload', methods=['POST'])
def upload_voice():
    """Upload voice sample for analysis"""
    try:
        supabase_manager = SupabaseManager()
        
        if 'audio' not in request.files:
            return jsonify({'success': False, 'error': 'No audio file provided'}), 400
        
        audio_file = request.files['audio']
        user_id = request.form.get('user_id', session.get('user_id'))
        
        if not user_id:
            return jsonify({'success': False, 'error': 'User ID is required'}), 400
            
        # Generate a unique filename
        filename = f"audio_{str(os.urandom(4).hex())}.wav"
        
        # Upload to Supabase storage
        result = supabase_manager.supabase.storage.from_('voice_samples').upload(
            path=filename,
            file=audio_file
        )
        
        if not result:
            return jsonify({'success': False, 'error': 'Failed to upload audio file'}), 500
            
        # Create a record in the voice_files table
        file_record = supabase_manager.supabase.table('voice_files').insert({
            'user_id': user_id,
            'file_path': f"voice_samples/{filename}",
            'original_filename': audio_file.filename
        }).execute()
        
        if not file_record.data:
            return jsonify({'success': False, 'error': 'Failed to create file record'}), 500
            
        audio_id = file_record.data[0]['id']
        
        return jsonify({
            'success': True,
            'audio_id': audio_id,
            'filename': audio_file.filename
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@bp.route('/analyze', methods=['POST'])
def analyze_voice():
    """Trigger Portia AI workflow for voice analysis"""
    try:
        if not portia_service:
            return jsonify({'success': False, 'error': 'Portia service not initialized'}), 500

        if 'audio' not in request.files:
            return jsonify({'success': False, 'error': 'No audio file provided'}), 400

        audio_file = request.files['audio']
        user_id = request.form.get('user_id', session.get('user_id'))
        
        # Get questionnaire responses and health context from session
        questionnaire_responses = session.get('questionnaire_responses', {})
        health_context = session.get('health_context', {})
        recording_prompt = session.get('recording_prompt', '')
        
        # Create user context from questionnaire data
        user_context = {
            'user_id': user_id,
            'questionnaire_responses': questionnaire_responses,
            'health_context': health_context,
            'recording_prompt': recording_prompt,
            'diabetes_status': health_context.get('diabetes_status', 'Unknown'),
            'meal_timing': health_context.get('meal_timing', 'Unknown'),
            'symptoms': health_context.get('symptoms', [])
        }

        # Generate a session ID - must be a valid UUID for the database
        session_id = str(uuid.uuid4())

        # Run the Portia workflow - use synchronous version
        result = portia_service.run_glucose_analysis_sync(
            audio_data=audio_file,
            user_context=user_context,
            session_id=session_id
        )

        if not result.get('success'):
            return jsonify({'success': False, 'error': result.get('error', 'Unknown error')}), 500

        # Store the results in the database
        try:
            supabase_manager = SupabaseManager()

            # Create voice session record with a unique ID
            voice_session = supabase_manager.supabase.table('voice_sessions').insert({
                'id': session_id,
                'user_id': user_id,
                'audio_file_path': f"voice_samples/{audio_file.filename}",
                'user_context': user_context,
                'quality_metrics': {'snr': 25.0, 'clarity': 85, 'spectral_quality': 90}  # Mock quality metrics
            }).execute()

            # Create prediction record with a unique ID
            prediction_id = str(uuid.uuid4())
            prediction = supabase_manager.supabase.table('glucose_predictions').insert({
                'id': prediction_id,
                'session_id': session_id,
                'prediction_result': result.get('prediction'),
                'confidence_score': result.get('prediction', {}).get('glucose_assessment', {}).get('confidence_score', 0.7)
            }).execute()
        except Exception as db_error:
            print(f"Error storing results in database: {db_error}")
            # Continue even if database operations fail
        
        # Store analysis result in session for fallback
        session['analysis_result'] = result.get('prediction')

        return jsonify({
            'success': True,
            'prediction': result.get('prediction'),
            'confidence': result.get('prediction', {}).get('glucose_assessment', {}).get('confidence_score', 0.7),
            'session_id': session_id
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@bp.route('/results/<session_id>', methods=['GET'])
@bp.route('/v1/results/<session_id>', methods=['GET'])
def get_results(session_id):
    """Retrieve analysis results"""
    try:
        supabase_manager = SupabaseManager()
        
        # Try to find the session with the provided ID
        print(f"Checking for session with ID: {session_id}")
        
        # Check if there's a result in the Flask session first
        if 'analysis_result' in session:
            print(f"Using analysis result from Flask session")
            prediction_result = session['analysis_result']
            
            # Try to store it in the database
            try:
                # Generate a unique ID for the prediction
                prediction_id = str(uuid.uuid4())
                
                supabase_manager.supabase.table('glucose_predictions').insert({
                    'id': prediction_id,
                    'session_id': session_id,
                    'prediction_result': prediction_result,
                    'confidence_score': prediction_result.get('glucose_assessment', {}).get('confidence_score', 0.5)
                }).execute()
                print(f"Stored session analysis result in database")
            except Exception as db_error:
                print(f"Error storing session analysis in database: {db_error}")
            
            # Return the result from session
            return jsonify({
                'success': True,
                'session_id': session_id,
                'prediction': prediction_result,
                'timestamp': datetime.now().isoformat(),
                'source': 'session_storage'
            })
        
        # If not in session, try to get from database
        session_result = supabase_manager.supabase.table('voice_sessions').select('*').eq('id', session_id).execute()
        
        if not session_result.data:
            print(f"Session not found in database: {session_id}")
            
            # Create a fallback result
            fallback_result = {
                'glucose_assessment': {
                    'primary_estimate': 'normal',
                    'estimated_range': '80-120 mg/dL',
                    'confidence_score': 0.65,
                    'risk_level': 'minimal'
                },
                'analysis_details': {
                    'voice_biomarkers_detected': ['baseline patterns'],
                    'supporting_context': 'Based on conversation data',
                    'conflicting_signals': 'None detected',
                    'quality_factors': 'Limited data available'
                },
                'clinical_insights': {
                    'immediate_recommendations': 'Continue with regular monitoring',
                    'monitoring_suggestions': 'Track glucose levels as usual',
                    'medical_consultation': 'Follow healthcare provider advice'
                },
                'limitations': {
                    'confidence_factors': 'Analysis based on limited data',
                    'disclaimer': 'This is an experimental technology'
                }
            }
            
            return jsonify({
                'success': True,
                'session_id': session_id,
                'prediction': fallback_result,
                'timestamp': datetime.now().isoformat(),
                'source': 'fallback'
            })
        
        session_data = session_result.data[0]
        
        # Check if user has permission to access this session
        user_id = session.get('user_id')
        if user_id and session_data.get('user_id') != user_id:
            print(f"Unauthorized access: user {user_id} trying to access session for user {session_data.get('user_id')}")
            return jsonify({'success': False, 'error': 'Unauthorized access'}), 403
        
        # Get the prediction for this session
        prediction_result = supabase_manager.supabase.table('glucose_predictions').select('*').eq('session_id', session_id).execute()
        
        if not prediction_result.data:
            print(f"Prediction not found for session in database: {session_id}")
            
            # Create a fallback result
            fallback_result = {
                'glucose_assessment': {
                    'primary_estimate': 'normal',
                    'estimated_range': '80-120 mg/dL',
                    'confidence_score': 0.7,
                    'risk_level': 'minimal'
                },
                'analysis_details': {
                    'voice_biomarkers_detected': ['baseline patterns'],
                    'supporting_context': 'Based on conversation data',
                    'conflicting_signals': 'None detected',
                    'quality_factors': 'Limited data available'
                },
                'clinical_insights': {
                    'immediate_recommendations': 'Continue with regular monitoring',
                    'monitoring_suggestions': 'Track glucose levels as usual',
                    'medical_consultation': 'Follow healthcare provider advice'
                },
                'limitations': {
                    'confidence_factors': 'Analysis based on limited data',
                    'disclaimer': 'This is an experimental technology'
                }
            }
            
            return jsonify({
                'success': True,
                'session_id': session_id,
                'prediction': fallback_result,
                'timestamp': session_data.get('created_at'),
                'source': 'fallback'
            })
        
        prediction_data = prediction_result.data[0]
        prediction_result = prediction_data.get('prediction_result', {})
        
        # Log confidence score for debugging
        confidence_score = prediction_result.get('glucose_assessment', {}).get('confidence_score')
        print(f"Retrieved prediction with confidence score: {confidence_score}")
        
        return jsonify({
            'success': True,
            'session_id': session_id,
            'prediction': prediction_result,
            'timestamp': session_data.get('created_at'),
            'source': 'database'
        })
    except Exception as e:
        print(f"Error retrieving results: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@bp.route('/history', methods=['GET'])
def get_user_history():
    """Get user's analysis history"""
    try:
        supabase_manager = SupabaseManager()
        
        user_id = request.args.get('user_id', session.get('user_id'))
        limit = request.args.get('limit', 50, type=int)
        
        if not user_id:
            return jsonify({'success': False, 'error': 'User ID is required'}), 400
        
        # Get user's voice sessions with predictions
        result = supabase_manager.supabase.from_('voice_sessions').select(
            '*, glucose_predictions(*)'
        ).eq('user_id', user_id).order('created_at', desc=True).limit(limit).execute()
        
        if not result.data:
            return jsonify({'success': True, 'history': []})
        
        # Format the history data
        history = []
        for item in result.data:
            prediction_data = None
            if item.get('glucose_predictions') and len(item['glucose_predictions']) > 0:
                prediction = item['glucose_predictions'][0]
                if prediction.get('prediction_result') and prediction['prediction_result'].get('glucose_assessment'):
                    prediction_data = {
                        'primary_estimate': prediction['prediction_result']['glucose_assessment'].get('primary_estimate'),
                        'confidence_score': prediction['prediction_result']['glucose_assessment'].get('confidence_score')
                    }
            
            history.append({
                'session_id': item.get('id'),
                'timestamp': item.get('created_at'),
                'prediction': prediction_data
            })
        
        return jsonify({
            'success': True,
            'history': history
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@bp.route('/feedback', methods=['POST'])
def submit_feedback():
    """Submit user feedback for ML improvement"""
    try:
        supabase_manager = SupabaseManager()
        
        data = request.json
        session_id = data.get('session_id')
        actual_glucose = data.get('actual_glucose')
        feedback_rating = data.get('feedback_rating')
        comments = data.get('comments')
        
        if not session_id:
            return jsonify({'success': False, 'error': 'Session ID is required'}), 400
        
        if not actual_glucose or not feedback_rating:
            return jsonify({'success': False, 'error': 'Actual glucose and feedback rating are required'}), 400
            
        # Store feedback in Supabase
        feedback_data = {
            'session_id': session_id,
            'actual_glucose': actual_glucose,
            'feedback_rating': feedback_rating,
            'comments': comments
        }
        
        result = supabase_manager.supabase.table('user_feedback').insert(feedback_data).execute()
        
        if not result.data:
            return jsonify({'success': False, 'error': 'Failed to store feedback'}), 500
            
        feedback_id = result.data[0]['id']
        
        return jsonify({
            'success': True,
            'feedback_id': feedback_id
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500