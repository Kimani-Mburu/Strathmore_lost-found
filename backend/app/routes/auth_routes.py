"""Enhanced authentication endpoints with security improvements"""

from flask import request, jsonify
from app.routes import auth_bp
from app.models import User
from app import db
from app.utils import generate_token, require_auth
from app.utils.validators import validate_email, sanitize_text_input, validate_password_strength
from app.utils.security import rate_limit, log_security_event

@auth_bp.route('/register', methods=['POST'])
@rate_limit('auth')
def register():
    """Register a new user with enhanced validation"""
    data = request.get_json()
    print(f"\n[REGISTER] Starting registration process")
    print(f"[REGISTER] Received data: email={data.get('email') if data else 'None'}")
    
    # Validate required fields
    if not data or not data.get('email') or not data.get('password') or not data.get('name'):
        print(f"[REGISTER] Missing required fields")
        return jsonify({'error': 'Missing required fields: name, email, and password are required'}), 400
    
    # Validate and sanitize email
    is_valid, message = validate_email(data['email'])
    if not is_valid:
        print(f"[REGISTER] Invalid email: {message}")
        log_security_event('invalid_registration_attempt', f'Invalid email: {data["email"]}')
        return jsonify({'error': message}), 400
    
    # Validate password strength
    is_valid, message = validate_password_strength(data['password'])
    if not is_valid:
        print(f"[REGISTER] Weak password: {message}")
        return jsonify({'error': message}), 400
    
    # Sanitize name
    name = sanitize_text_input(data['name'], max_length=255)
    if len(name) < 2:
        print(f"[REGISTER] Name too short")
        return jsonify({'error': 'Name must be at least 2 characters long'}), 400
    
    # Check if email already exists
    existing = User.query.filter_by(email=data['email'].lower()).first()
    if existing:
        print(f"[REGISTER] Email already registered: {data['email']}")
        log_security_event('duplicate_registration_attempt', f'Email already exists: {data["email"]}')
        return jsonify({'error': 'Email already registered'}), 400
    
    # Create user
    print(f"[REGISTER] Creating new user: {data['email']}")
    user = User(
        name=name,
        email=data['email'].lower(),
        role='user'
    )
    user.set_password(data['password'])
    
    try:
        db.session.add(user)
        db.session.commit()
        print(f"[REGISTER] User successfully created and committed to DB: {user.email}")
        
        log_security_event('user_registered', f'New user registered: {user.email}')
        
        return jsonify({
            'message': 'User registered successfully',
            'user': user.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        log_security_event('registration_error', f'Database error: {str(e)}')
        return jsonify({'error': 'Registration failed. Please try again.'}), 500

@auth_bp.route('/login', methods=['POST'])
@rate_limit('auth')
def login():
    """Enhanced login with security monitoring"""
    data = request.get_json()
    
    # Validate required fields
    if not data or not data.get('email') or not data.get('password'):
        return jsonify({'error': 'Missing email or password'}), 400
    
    # Basic email validation
    is_valid, message = validate_email(data['email'])
    if not is_valid:
        log_security_event('invalid_login_attempt', f'Invalid email format: {data["email"]}')
        return jsonify({'error': message}), 400
    
    # Find user
    user = User.query.filter_by(email=data['email'].lower()).first()
    
    if not user or not user.check_password(data['password']):
        log_security_event('failed_login', f'Failed login attempt for: {data["email"]}')
        return jsonify({'error': 'Invalid email or password'}), 401
    
    # Generate token
    token = generate_token(user.user_id)
    
    log_security_event('successful_login', f'User logged in: {user.email}')
    
    return jsonify({
        'message': 'Login successful',
        'token': token,
        'user': user.to_dict()
    }), 200

@auth_bp.route('/profile', methods=['GET'])
@require_auth
def get_profile(current_user_id):
    """Get current user profile"""
    user = User.query.get(current_user_id)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    return jsonify(user.to_dict()), 200
