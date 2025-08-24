from flask import Blueprint, render_template, session, redirect, url_for, request
from datetime import datetime
from app.services.supabase_service import SupabaseManager

bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    """Render the home page"""
    user_id = session.get('user_id')
    if user_id:
        return redirect(url_for('main.dashboard'))
    return render_template('index.html')

@bp.route('/login')
def login_page():
    """Render the login page"""
    if session.get('user_id'):
        return redirect(url_for('main.dashboard'))
    
    return render_template('login.html')

@bp.route('/register')
def register_page():
    """Render the registration page"""
    if session.get('user_id'):
        return redirect(url_for('main.dashboard'))
    
    return render_template('register.html')

@bp.route('/questionnaire')
def questionnaire():
    """Render the Claude 3.7 Sonnet powered questionnaire page"""
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('main.login_page'))

    return render_template('questionnaire.html', user_id=user_id)

@bp.route('/recording')
def recording():
    """Render the voice recording page"""
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('main.login_page'))
    
    # Get context data from questionnaire
    context_id = request.args.get('context_id')
    
    return render_template('recording.html', user_id=user_id, context_id=context_id)

@bp.route('/results/<session_id>')
def results(session_id):
    """Render the results page"""
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('main.login_page'))
    
    # Format timestamp
    timestamp = datetime.now().strftime('%d/%m/%Y, %H:%M:%S %p')
    
    return render_template('results.html', user_id=user_id, session_id=session_id, session_timestamp=timestamp)

@bp.route('/dashboard')
def dashboard():
    """Render the user dashboard"""
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('main.login_page'))
    
    # Get user's analysis history
    supabase_manager = SupabaseManager()
    history = []
    avg_confidence = 0
    common_result = "Normal"
    total_count = 0
    
    try:
        # Get user's voice sessions with predictions
        result = supabase_manager.supabase.from_('voice_sessions').select(
            '*, glucose_predictions(*)'
        ).eq('user_id', user_id).order('created_at', desc=True).limit(20).execute()
        
        if result.data:
            # Format the history data
            total_confidence = 0
            confidence_count = 0
            result_counts = {}
            
            for item in result.data:
                prediction_data = None
                confidence = 0
                
                if item.get('glucose_predictions') and len(item['glucose_predictions']) > 0:
                    prediction = item['glucose_predictions'][0]
                    if prediction.get('prediction_result') and prediction['prediction_result'].get('glucose_assessment'):
                        glucose_assessment = prediction['prediction_result']['glucose_assessment']
                        primary_estimate = glucose_assessment.get('primary_estimate', 'unknown')
                        confidence = glucose_assessment.get('confidence_score', 0)
                        
                        prediction_data = {
                            'primary_estimate': primary_estimate,
                            'confidence_score': confidence
                        }
                        
                        # Count for most common result
                        if primary_estimate in result_counts:
                            result_counts[primary_estimate] += 1
                        else:
                            result_counts[primary_estimate] = 1
                        
                        # Add to total confidence
                        total_confidence += confidence
                        confidence_count += 1
                
                # Format timestamp
                timestamp = item.get('created_at')
                if timestamp:
                    from datetime import datetime
                    try:
                        dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                        formatted_timestamp = dt.strftime('%d %b %Y, %H:%M')
                    except:
                        formatted_timestamp = timestamp
                else:
                    formatted_timestamp = "Unknown"
                
                history.append({
                    'session_id': item.get('id'),
                    'timestamp': formatted_timestamp,
                    'prediction': prediction_data
                })
                
                # Increment total count for each valid analysis
                total_count += 1
            
            # Calculate average confidence
            if confidence_count > 0:
                avg_confidence = int((total_confidence / confidence_count) * 100)
            
            # Find most common result
            if result_counts:
                common_result = max(result_counts.items(), key=lambda x: x[1])[0]
                common_result = common_result.capitalize()
    except Exception as e:
        print(f"Error fetching dashboard data: {e}")
    
    # Convert history to JSON for chart
    import json
    history_json = json.dumps(history)
    
    return render_template(
        'dashboard.html', 
        user_id=user_id,
        history=history,
        history_json=history_json,
        avg_confidence=avg_confidence,
        common_result=common_result,
        total_count=total_count
    )

@bp.route('/profile')
def profile_page():
    """Render the user profile page"""
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('main.login_page'))
    
    return render_template('profile.html', user_id=user_id)

@bp.route('/new-analysis')
def new_analysis():
    """Start a new analysis - redirect to questionnaire"""
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('main.login_page'))

    # Clear any previous session data
    if 'analysis_result' in session:
        session.pop('analysis_result')
    if 'questionnaire' in session:
        session.pop('questionnaire')
    if 'questionnaire_responses' in session:
        session.pop('questionnaire_responses')
    if 'recording_prompt' in session:
        session.pop('recording_prompt')
    if 'health_context' in session:
        session.pop('health_context')
    if 'context_id' in session:
        session.pop('context_id')

    print("Redirecting to questionnaire page for new analysis")
    return redirect(url_for('main.questionnaire'))

@bp.route('/about')
def about():
    """Render the about page"""
    return render_template('about.html')

@bp.route('/privacy')
def privacy():
    """Render the privacy policy page"""
    return render_template('privacy.html')

@bp.route('/terms')
def terms():
    """Render the terms of service page"""
    return render_template('terms.html')