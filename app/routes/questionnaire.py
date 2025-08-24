from flask import Blueprint, request, jsonify, session, redirect, url_for
import os
import uuid
import json
from app.services.claude_sonnet_service import ClaudeSonnetService
from app.services.supabase_service import SupabaseManager
from app.services.prompt_templates import ERROR_MESSAGES

bp = Blueprint('questionnaire', __name__, url_prefix='/api/v1/questionnaire')

# Initialize services
try:
    claude_service = ClaudeSonnetService()
except Exception as e:
    print(f"Error initializing Claude Sonnet service: {e}")
    claude_service = None

@bp.route('/generate', methods=['GET'])
def generate_questionnaire():
    """Generate a dynamic health questionnaire with Claude 3.7 Sonnet"""
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'success': False, 'error': ERROR_MESSAGES['authentication']}), 401
        
        # Generate questionnaire
        if claude_service:
            questionnaire = claude_service.generate_questionnaire()
        else:
            # Use fallback questionnaire from prompt_templates
            from app.services.prompt_templates import FALLBACK_QUESTIONNAIRE
            questionnaire = FALLBACK_QUESTIONNAIRE
        
        # Store the questionnaire in the session for later use
        session['questionnaire'] = questionnaire
        
        return jsonify({
            'success': True,
            'questionnaire': questionnaire
        })
    except Exception as e:
        print(f"Error generating questionnaire: {e}")
        return jsonify({
            'success': False, 
            'error': ERROR_MESSAGES['questionnaire_generation']
        }), 500

@bp.route('/submit', methods=['POST'])
def submit_questionnaire():
    """Submit questionnaire responses and get recording prompt"""
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'success': False, 'error': ERROR_MESSAGES['authentication']}), 401
        
        # Get responses from request
        data = request.json
        if not data or not data.get('responses'):
            return jsonify({'success': False, 'error': 'No questionnaire responses provided'}), 400
            
        responses = data.get('responses', {})
        
        # Store responses in session
        session['questionnaire_responses'] = responses
        
        # Generate recording prompt
        if claude_service:
            recording_prompt = claude_service.generate_recording_prompt(responses)
        else:
            from app.services.prompt_templates import FALLBACK_RECORDING_PROMPT
            recording_prompt = FALLBACK_RECORDING_PROMPT
        
        # Store the prompt in session
        session['recording_prompt'] = recording_prompt
        
        # Analyze responses to extract health context
        if claude_service:
            health_context = claude_service.analyze_responses(responses)
        else:
            from app.services.prompt_templates import FALLBACK_HEALTH_CONTEXT
            health_context = FALLBACK_HEALTH_CONTEXT
        
        # Store health context in session
        session['health_context'] = health_context
        
        # Store in database
        context_id = None
        try:
            supabase_manager = SupabaseManager()
            context_id = str(uuid.uuid4())
            
            result = supabase_manager.supabase.table('user_contexts').insert({
                'id': context_id,
                'user_id': user_id,
                'context_data': {
                    'responses': responses,
                    'health_context': health_context
                }
            }).execute()
            
            if result.data:
                context_id = result.data[0]['id']
                # Store context_id in session
                session['context_id'] = context_id
        except Exception as db_error:
            print(f"Error storing questionnaire in database: {db_error}")
            # Continue even if database operation fails, but log the error
            
        return jsonify({
            'success': True,
            'recording_prompt': recording_prompt,
            'health_context': health_context,
            'context_id': context_id
        })
    except Exception as e:
        print(f"Error submitting questionnaire: {e}")
        return jsonify({
            'success': False, 
            'error': ERROR_MESSAGES['questionnaire_generation']
        }), 500

