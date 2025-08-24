import os
import uuid
import hashlib
import bcrypt
from app.services.supabase_service import SupabaseManager

class UserService:
    """Service for user authentication and management"""
    
    def __init__(self):
        """Initialize the user service"""
        self.supabase_manager = SupabaseManager()
        
    def register_user(self, email, password):
        """Register a new user with email and password"""
        try:
            # Check if user already exists
            existing_user = self.supabase_manager.supabase.table('users').select('*').eq('email', email).execute()
            
            if existing_user.data and len(existing_user.data) > 0:
                return {
                    'success': False,
                    'error': 'Email already exists'
                }
            
            # Hash the password using bcrypt
            password_hash = self._hash_password(password)
            
            # Create user with UUID
            user_id = str(uuid.uuid4())
            user_result = self.supabase_manager.supabase.table('users').insert({
                'id': user_id,
                'email': email,
                'password_hash': password_hash
            }).execute()
            
            if not user_result.data:
                return {
                    'success': False,
                    'error': 'Failed to create user'
                }
            
            # Create profile
            profile_result = self.supabase_manager.supabase.table('profiles').insert({
                'id': user_id,
                'preferences': {}
            }).execute()
            
            return {
                'success': True,
                'user': {
                    'id': user_id,
                    'email': email,
                    'created_at': user_result.data[0]['created_at']
                }
            }
            
        except Exception as e:
            print(f"Error registering user: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def login_user(self, email, password):
        """Authenticate a user with email and password"""
        try:
            # Get user by email
            user_result = self.supabase_manager.supabase.table('users').select('*').eq('email', email).execute()
            
            if not user_result.data or len(user_result.data) == 0:
                return {
                    'success': False,
                    'error': 'Invalid email or password'
                }
            
            user = user_result.data[0]
            
            # Verify password
            if not self._verify_password(password, user['password_hash']):
                return {
                    'success': False,
                    'error': 'Invalid email or password'
                }
            
            # Update last login time
            self.supabase_manager.supabase.table('users').update({
                'last_login': 'now()'
            }).eq('id', user['id']).execute()
            
            return {
                'success': True,
                'user': {
                    'id': user['id'],
                    'email': user['email'],
                    'created_at': user['created_at']
                }
            }
            
        except Exception as e:
            print(f"Error logging in user: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_user_by_id(self, user_id):
        """Get user by ID"""
        try:
            user_result = self.supabase_manager.supabase.table('users').select('*').eq('id', user_id).execute()
            
            if not user_result.data or len(user_result.data) == 0:
                return None
            
            user = user_result.data[0]
            
            return {
                'id': user['id'],
                'email': user['email'],
                'created_at': user['created_at']
            }
            
        except Exception as e:
            print(f"Error getting user by ID: {e}")
            return None
    
    def update_user(self, user_id, data):
        """Update user data"""
        try:
            # Don't allow updating email or password through this method
            update_data = {}
            if 'preferences' in data:
                # Update preferences in profile table
                profile_result = self.supabase_manager.supabase.table('profiles').update({
                    'preferences': data['preferences']
                }).eq('id', user_id).execute()
            
            return {
                'success': True
            }
            
        except Exception as e:
            print(f"Error updating user: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def change_password(self, user_id, current_password, new_password):
        """Change user password"""
        try:
            # Get user
            user_result = self.supabase_manager.supabase.table('users').select('*').eq('id', user_id).execute()
            
            if not user_result.data or len(user_result.data) == 0:
                return {
                    'success': False,
                    'error': 'User not found'
                }
            
            user = user_result.data[0]
            
            # Verify current password
            if not self._verify_password(current_password, user['password_hash']):
                return {
                    'success': False,
                    'error': 'Current password is incorrect'
                }
            
            # Hash new password
            password_hash = self._hash_password(new_password)
            
            # Update password
            self.supabase_manager.supabase.table('users').update({
                'password_hash': password_hash
            }).eq('id', user_id).execute()
            
            return {
                'success': True
            }
            
        except Exception as e:
            print(f"Error changing password: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _hash_password(self, password):
        """Hash a password using bcrypt"""
        # Generate a salt
        salt = bcrypt.gensalt(rounds=12)
        
        # Hash the password
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        
        return hashed.decode('utf-8')
    
    def _verify_password(self, password, hashed):
        """Verify a password against a hash"""
        try:
            return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
        except Exception as e:
            print(f"Error verifying password: {e}")
            return False