"""Authentication utilities"""

from functools import wraps
from flask import request, jsonify, current_app
import secrets
import json
import os
from datetime import datetime, timedelta

# In-memory token store with file persistence
TOKEN_STORE = {}
TOKEN_FILE = None

def get_token_file():
    """Get the path to the token storage file"""
    global TOKEN_FILE
    if TOKEN_FILE is None:
        instance_path = current_app.instance_path if current_app else os.path.join(os.path.dirname(__file__), '../../instance')
        os.makedirs(instance_path, exist_ok=True)
        TOKEN_FILE = os.path.join(instance_path, 'tokens.json')
    return TOKEN_FILE

def load_tokens():
    """Load tokens from file"""
    global TOKEN_STORE
    token_file = get_token_file()
    if os.path.exists(token_file):
        try:
            with open(token_file, 'r') as f:
                data = json.load(f)
                # Reconstruct datetime objects
                for token, token_data in data.items():
                    token_data['created_at'] = datetime.fromisoformat(token_data['created_at'])
                    token_data['expires_at'] = datetime.fromisoformat(token_data['expires_at'])
                TOKEN_STORE = data
        except Exception as e:
            print(f"Error loading tokens: {e}")
            TOKEN_STORE = {}
    else:
        TOKEN_STORE = {}

def save_tokens():
    """Save tokens to file"""
    token_file = get_token_file()
    try:
        data = {}
        for token, token_data in TOKEN_STORE.items():
            data[token] = {
                'user_id': token_data['user_id'],
                'created_at': token_data['created_at'].isoformat(),
                'expires_at': token_data['expires_at'].isoformat()
            }
        with open(token_file, 'w') as f:
            json.dump(data, f)
    except Exception as e:
        print(f"Error saving tokens: {e}")

def generate_token(user_id):
    """Generate authentication token"""
    load_tokens()  # Load existing tokens
    token = secrets.token_urlsafe(32)
    TOKEN_STORE[token] = {
        'user_id': user_id,
        'created_at': datetime.utcnow(),
        'expires_at': datetime.utcnow() + timedelta(days=7)
    }
    save_tokens()  # Save updated tokens
    return token

def verify_token(token):
    """Verify and retrieve user from token"""
    load_tokens()  # Load existing tokens
    
    if token not in TOKEN_STORE:
        return None
    
    token_data = TOKEN_STORE[token]
    
    # Check if token expired
    if datetime.utcnow() > token_data['expires_at']:
        del TOKEN_STORE[token]
        save_tokens()
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
