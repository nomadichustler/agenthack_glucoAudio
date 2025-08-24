from flask import Blueprint, request, jsonify, session, redirect, url_for
import uuid
from app.services.user_service import UserService

bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/login', methods=['GET', 'POST'])
def login():
    """Handle user login"""
    if request.method == 'POST':
        try:
            user_service = UserService()
            
            data = request.json or {}
            email = data.get('email')
            password = data.get('password')
            
            if not email or not password:
                return jsonify({'success': False, 'error': 'Email and password are required'}), 400
            
            # Authenticate with our custom service
            result = user_service.login_user(email, password)
            
            if not result['success']:
                return jsonify({'success': False, 'error': result['error']}), 401
            
            # Store user data in session
            user = result['user']
            session['user_id'] = user['id']
            session['email'] = user['email']
            
            return jsonify({
                'success': True,
                'user': user
            })
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500
    
    # GET request - render login page
    return redirect(url_for('main.login_page'))

@bp.route('/logout', methods=['GET', 'POST'])
def logout():
    """Handle user logout"""
    # Clear session
    session.clear()
    
    if request.method == 'POST':
        return jsonify({'success': True})
    
    # GET request - redirect to home
    return redirect(url_for('main.index'))

@bp.route('/register', methods=['GET', 'POST'])
def register():
    """Handle user registration"""
    if request.method == 'POST':
        try:
            user_service = UserService()
            
            data = request.json or {}
            email = data.get('email')
            password = data.get('password')
            
            if not email or not password:
                return jsonify({'success': False, 'error': 'Email and password are required'}), 400
            
            if len(password) < 6:
                return jsonify({'success': False, 'error': 'Password must be at least 6 characters'}), 400
            
            # Register with our custom service
            result = user_service.register_user(email, password)
            
            if not result['success']:
                return jsonify({'success': False, 'error': result['error']}), 400
            
            user = result['user']
            
            # Create session
            session['user_id'] = user['id']
            session['email'] = user['email']
            
            return jsonify({
                'success': True,
                'user': user
            })
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500
    
    # GET request - render registration page
    return redirect(url_for('main.register_page'))

@bp.route('/profile', methods=['GET', 'PUT'])
def profile():
    """Handle user profile management"""
    user_id = session.get('user_id')
    
    if not user_id:
        if request.method == 'GET':
            return redirect(url_for('main.login_page'))
        else:
            return jsonify({'success': False, 'error': 'Not authenticated'}), 401
    
    user_service = UserService()
    
    if request.method == 'PUT':
        try:
            data = request.json or {}
            preferences = data.get('preferences', {})
            
            # Update user profile
            result = user_service.update_user(user_id, {
                'preferences': preferences
            })
            
            if not result['success']:
                return jsonify({'success': False, 'error': result['error']}), 500
            
            # Get updated user
            user = user_service.get_user_by_id(user_id)
            
            return jsonify({
                'success': True,
                'user': {
                    'id': user_id,
                    'email': session.get('email'),
                    'preferences': preferences
                }
            })
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500
    
    # GET request - render profile page
    return redirect(url_for('main.profile_page'))

@bp.route('/change-password', methods=['POST'])
def change_password():
    """Handle password change"""
    user_id = session.get('user_id')
    
    if not user_id:
        return jsonify({'success': False, 'error': 'Not authenticated'}), 401
    
    try:
        user_service = UserService()
        
        data = request.json or {}
        current_password = data.get('current_password')
        new_password = data.get('new_password')
        
        if not current_password or not new_password:
            return jsonify({'success': False, 'error': 'Current password and new password are required'}), 400
        
        if len(new_password) < 6:
            return jsonify({'success': False, 'error': 'New password must be at least 6 characters'}), 400
        
        # Change password
        result = user_service.change_password(user_id, current_password, new_password)
        
        if not result['success']:
            return jsonify({'success': False, 'error': result['error']}), 400
        
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500