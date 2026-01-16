"""
Strathmore University Digital Lost & Found Web Application
Backend Flask Application Initialization
"""

from flask import Flask, render_template, send_from_directory, redirect, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
import os

db = SQLAlchemy()

def create_app(config_name='development'):
    """Application factory function"""
    app = Flask(__name__, static_folder='static', static_url_path='/static', instance_relative_config=True)
    
    # Ensure instance folder exists
    try:
        os.makedirs(app.instance_path, exist_ok=True)
    except OSError:
        pass
    
    # Load configuration
    if config_name == 'production':
        app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///' + os.path.join(app.instance_path, 'lostnfound.db'))
    else:
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(app.instance_path, 'lostnfound.db')
    
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max upload
    app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(__file__), 'uploads')
    
    # Ensure upload folder exists
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    # Initialize extensions
    db.init_app(app)
    CORS(app)
    
    # Register blueprints
    from app.routes import auth_bp, items_bp, admin_bp
    app.register_blueprint(auth_bp)
    app.register_blueprint(items_bp)
    app.register_blueprint(admin_bp)
    
    # Helper function to check admin from token
    def get_user_from_token():
        """Extract user info from auth token"""
        auth_header = request.headers.get('Authorization', '')
        if auth_header.startswith('Bearer '):
            token = auth_header[7:]
            try:
                from app.utils.auth import verify_token
                user_id = verify_token(token)
                if user_id:
                    from app.models import User
                    user = User.query.get(user_id)
                    return user
            except Exception as e:
                print(f"Error verifying token: {e}")
                return None
        return None
    
    # Frontend routes - serve HTML pages
    @app.route('/')
    def index():
        return send_from_directory(app.static_folder, 'index.html')
    
    @app.route('/login')
    def login():
        return send_from_directory(app.static_folder, 'login.html')
    
    @app.route('/register')
    def register():
        return send_from_directory(app.static_folder, 'register.html')
    
    @app.route('/browse')
    def browse():
        return send_from_directory(app.static_folder, 'browse.html')
    
    @app.route('/report')
    def report():
        return send_from_directory(app.static_folder, 'report.html')
    
    @app.route('/dashboard')
    def dashboard():
        return send_from_directory(app.static_folder, 'dashboard.html')
    
    @app.route('/my-dashboard')
    def my_dashboard():
        return send_from_directory(app.static_folder, 'my-dashboard.html')
    
    @app.route('/browse-lost')
    def browse_lost():
        return send_from_directory(app.static_folder, 'browse-lost.html')
    
    @app.route('/browse-found')
    def browse_found():
        return send_from_directory(app.static_folder, 'browse-found.html')
    
    @app.route('/admin-dashboard')
    def admin_dashboard():
        return send_from_directory(app.static_folder, 'admin-dashboard.html')
    
    @app.route('/test-login')
    def test_login_page():
        return send_from_directory(app.static_folder, 'test-login.html')
    
    # Create database tables
    with app.app_context():
        db.create_all()
    
    return app
