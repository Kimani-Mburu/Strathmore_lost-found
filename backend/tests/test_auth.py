"""
Test authentication endpoints
"""

import pytest
import json
from app.models import User


class TestAuthRoutes:
    """Test authentication related endpoints"""

    def test_register_success(self, client):
        """Test successful user registration"""
        response = client.post('/api/auth/register', json={
            'name': 'John Doe',
            'email': 'john.doe@strathmore.ac.ke',
            'password': 'SecurePass123'
        })
        
        assert response.status_code == 201
        data = response.get_json()
        assert data['message'] == 'User registered successfully'
        assert 'user' in data
        assert data['user']['email'] == 'john.doe@strathmore.ac.ke'

    def test_register_invalid_email(self, client):
        """Test registration with invalid email domain"""
        response = client.post('/api/auth/register', json={
            'name': 'Jane Doe',
            'email': 'jane@gmail.com',
            'password': 'SecurePass123'
        })
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data
        assert 'strathmore.ac.ke' in data['error']

    def test_register_duplicate_email(self, client, test_user):
        """Test registration with duplicate email"""
        response = client.post('/api/auth/register', json={
            'name': 'Another User',
            'email': test_user.email,
            'password': 'SecurePass123'
        })
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data
        assert 'already exists' in data['error']

    def test_register_missing_fields(self, client):
        """Test registration with missing required fields"""
        response = client.post('/api/auth/register', json={
            'name': 'John Doe',
            'email': 'john.doe@strathmore.ac.ke'
            # Missing password
        })
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data

    def test_login_success(self, client, test_user):
        """Test successful login"""
        response = client.post('/api/auth/login', json={
            'email': test_user.email,
            'password': 'TestPass123'
        })
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'token' in data
        assert 'user' in data
        assert data['user']['email'] == test_user.email

    def test_login_invalid_credentials(self, client, test_user):
        """Test login with invalid password"""
        response = client.post('/api/auth/login', json={
            'email': test_user.email,
            'password': 'WrongPassword123'
        })
        
        assert response.status_code == 401
        data = response.get_json()
        assert 'error' in data
        assert 'Invalid credentials' in data['error']

    def test_login_nonexistent_user(self, client):
        """Test login with non-existent user"""
        response = client.post('/api/auth/login', json={
            'email': 'nonexistent@strathmore.ac.ke',
            'password': 'Password123'
        })
        
        assert response.status_code == 401
        data = response.get_json()
        assert 'error' in data

    def test_get_profile_success(self, client, auth_headers, test_user):
        """Test getting user profile with valid token"""
        response = client.get('/api/auth/profile', headers=auth_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['user']['email'] == test_user.email
        assert data['user']['name'] == test_user.name

    def test_get_profile_invalid_token(self, client):
        """Test getting profile with invalid token"""
        response = client.get('/api/auth/profile', headers={
            'Authorization': 'Bearer invalid_token'
        })
        
        assert response.status_code == 401
        data = response.get_json()
        assert 'error' in data

    def test_get_profile_no_token(self, client):
        """Test getting profile without token"""
        response = client.get('/api/auth/profile')
        
        assert response.status_code == 401
        data = response.get_json()
        assert 'error' in data

    def test_password_hashing(self, app):
        """Test that passwords are properly hashed"""
        with app.app_context():
            user = User(
                name='Test User',
                email='test@strathmore.ac.ke'
            )
            user.set_password('plaintext123')
            
            # Password should not be stored as plaintext
            assert user.password_hash != 'plaintext123'
            assert len(user.password_hash) == 64  # SHA-256 hash length
            
            # Password verification should work
            assert user.check_password('plaintext123')
            assert not user.check_password('wrongpassword')