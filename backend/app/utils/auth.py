"""Authentication utilities"""

from functools import wraps
from flask import request, jsonify
import secrets
from datetime import datetime, timedelta

# In-memory token store (for demo purposes)
TOKEN_STORE = {}

def generate_token(user_id):
    """Generate authentication token"""
    token = secrets.token_urlsafe(32)
    TOKEN_STORE[token] = {
        'user_id': user_id,
        'created_at': datetime.utcnow(),
        'expires_at': datetime.utcnow() + timedelta(days=7)
    }
    return token

def verify_token(token):
    """Verify and retrieve user from token"""
    if token not in TOKEN_STORE:
        return None
    
    token_data = TOKEN_STORE[token]
    
    # Check if token expired
    if datetime.utcnow() > token_data['expires_at']:
        del TOKEN_STORE[token]
        return None
    
    return token_data['user_id']

def require_auth(f):
    """Decorator to require authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.headers.get('Authorization')
        
        if not token:
            return jsonify({'error': 'Missing authorization token'}), 401
        
        # Remove 'Bearer ' prefix if present
        if token.startswith('Bearer '):
            token = token[7:]
        
        user_id = verify_token(token)
        if not user_id:
            return jsonify({'error': 'Invalid or expired token'}), 401
        
        kwargs['current_user_id'] = user_id
        return f(*args, **kwargs)
    
    return decorated_function
