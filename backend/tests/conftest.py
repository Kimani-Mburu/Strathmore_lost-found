"""
Test configuration and fixtures for the Lost & Found application
"""

import pytest
import tempfile
import os
from datetime import datetime
from app import create_app, db
from app.models import User, Item, Claim


@pytest.fixture
def app():
    """Create and configure a test app"""
    # Create a temporary file for the test database
    db_fd, db_path = tempfile.mkstemp()
    
    # Disable auto-init to avoid admin user creation during app startup
    os.environ['SKIP_ADMIN_INIT'] = '1'
    
    app = create_app('testing')
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
    app.config['WTF_CSRF_ENABLED'] = False
    
    # Create test upload directory
    app.config['UPLOAD_FOLDER'] = tempfile.mkdtemp()
    
    with app.app_context():
        db.create_all()
        yield app
        # Clean session before dropping
        db.session.remove()
        db.drop_all()
    
    # Clean up env
    os.environ.pop('SKIP_ADMIN_INIT', None)
    os.close(db_fd)
    os.unlink(db_path)


@pytest.fixture
def client(app):
    """A test client for the app"""
    return app.test_client()


@pytest.fixture
def runner(app):
    """A test runner for the app's Click commands"""
    return app.test_cli_runner()


@pytest.fixture
def test_user(app):
    """Create a test user"""
    with app.app_context():
        user = User(
            name='Test User',
            email='test@strathmore.ac.ke',
            role='user'
        )
        user.set_password('TestPass123')
        db.session.add(user)
        db.session.commit()
        user_id = user.user_id
        # Expunge the user to avoid DetachedInstanceError
        db.session.expunge(user)
        
    # Return a fresh query result instead of the detached object
    with app.app_context():
        return User.query.filter_by(user_id=user_id).first()


@pytest.fixture
def admin_user(app):
    """Create an admin user"""
    with app.app_context():
        admin = User(
            name='Admin User',
            email='admin@strathmore.ac.ke',
            role='admin'
        )
        admin.set_password('AdminPass123')
        db.session.add(admin)
        db.session.commit()
        admin_id = admin.user_id
        db.session.expunge(admin)
        
    with app.app_context():
        return User.query.filter_by(user_id=admin_id).first()


@pytest.fixture
def test_item(app, test_user):
    """Create a test item"""
    with app.app_context():
        item = Item(
            title='Test Lost Phone',
            description='Samsung Galaxy S21 in black case',
            category='electronics',
            item_type='lost',
            date=datetime.utcnow(),
            location='Library Main Building',
            user_id=test_user.user_id,
            is_verified=True
        )
        db.session.add(item)
        db.session.commit()
        item_id = item.item_id
        db.session.expunge(item)
        
    with app.app_context():
        return Item.query.filter_by(item_id=item_id).first()


@pytest.fixture
def test_claim(app, test_item, test_user):
    """Create a test claim"""
    with app.app_context():
        claim = Claim(
            item_id=test_item.item_id,
            user_id=test_user.user_id,
            status='pending',
            notes='This is my phone, I can provide proof'
        )
        db.session.add(claim)
        db.session.commit()
        claim_id = claim.claim_id
        db.session.expunge(claim)
        
    with app.app_context():
        return Claim.query.filter_by(claim_id=claim_id).first()


@pytest.fixture
def auth_token(client, test_user):
    """Get authentication token for test user"""
    response = client.post('/api/auth/login', json={
        'email': test_user.email,
        'password': 'TestPass123'
    })
    data = response.get_json()
    return data['token']


@pytest.fixture
def admin_token(client, admin_user):
    """Get authentication token for admin user"""
    response = client.post('/api/auth/login', json={
        'email': admin_user.email,
        'password': 'AdminPass123'
    })
    data = response.get_json()
    return data['token']


@pytest.fixture
def auth_headers(auth_token):
    """Authentication headers for API requests"""
    return {'Authorization': f'Bearer {auth_token}'}


@pytest.fixture
def admin_headers(admin_token):
    """Admin authentication headers for API requests"""
    return {'Authorization': f'Bearer {admin_token}'}


@pytest.fixture
def sample_image():
    """Create a sample image file for testing"""
    # This would typically be a real image file
    # For testing purposes, we'll create a simple file
    return (b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01'
            b'\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89'
            b'\x00\x00\x00\nIDATx\x9cc`\x00\x00\x00\x02\x00\x01'
            b'\xe2!\xbc\x33\x00\x00\x00\x00IEND\xaeB`\x82', 'test.png')