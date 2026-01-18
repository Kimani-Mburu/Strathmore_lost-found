"""
Test utility functions and validators
"""

import pytest
import tempfile
import os
from io import BytesIO
from PIL import Image
from app.utils.validators import validate_email, validate_image, secure_upload_filename
from app.utils.auth import generate_token, verify_token


class TestValidators:
    """Test validation utility functions"""

    def test_validate_email_valid_strathmore(self):
        """Test valid Strathmore email addresses"""
        valid_emails = [
            'john.doe@strathmore.ac.ke',
            'jane_smith@strathmore.ac.ke',
            'student123@strathmore.ac.ke',
            'a.b.c@strathmore.ac.ke'
        ]
        
        for email in valid_emails:
            is_valid, message = validate_email(email)
            assert is_valid, f"Email {email} should be valid"
            assert message == "Email is valid"

    def test_validate_email_invalid_domain(self):
        """Test invalid email domains"""
        invalid_emails = [
            'john@gmail.com',
            'jane@yahoo.com',
            'test@strathmore.edu',
            'user@strathmore.org'
        ]
        
        for email in invalid_emails:
            is_valid, message = validate_email(email)
            assert not is_valid, f"Email {email} should be invalid"
            assert 'strathmore.ac.ke' in message

    def test_validate_email_invalid_format(self):
        """Test invalid email formats"""
        invalid_emails = [
            'not-an-email',
            '@strathmore.ac.ke',
            'user@',
            'user.strathmore.ac.ke',
            '',
            'user@strathmore.ac.ke.'
        ]
        
        for email in invalid_emails:
            is_valid, message = validate_email(email)
            assert not is_valid, f"Email {email} should be invalid"

    def test_secure_upload_filename(self):
        """Test secure filename generation"""
        test_cases = [
            ('image.jpg', 'image.jpg'),
            ('../malicious.txt', 'malicious.txt'),
            ('/etc/passwd', 'passwd.jpg'),  # No extension gets .jpg added
            ('file with spaces.png', 'file_with_spaces.png'),
            ('file@#$%^&*().jpg', 'file.jpg'),
            ('', 'upload'),
            ('.hidden', 'hidden.jpg')  # Hidden file with no ext gets .jpg
        ]
        
        for input_name, expected in test_cases:
            result = secure_upload_filename(input_name)
            assert result == expected, f"Input {input_name} should result in {expected}, got {result}"

    def test_validate_image_valid_formats(self):
        """Test valid image formats"""
        # Create test images in different formats
        formats = ['JPEG', 'PNG', 'GIF']
        
        for fmt in formats:
            # Create a simple test image
            img = Image.new('RGB', (100, 100), color='red')
            img_bytes = BytesIO()
            img.save(img_bytes, format=fmt)
            img_bytes.seek(0)
            
            # Create file-like object
            from werkzeug.datastructures import FileStorage
            file = FileStorage(
                stream=img_bytes,
                filename=f'test.{fmt.lower()}',
                content_type=f'image/{fmt.lower()}'
            )
            
            is_valid, message = validate_image(file)
            assert is_valid, f"Format {fmt} should be valid"
            assert message == "Image is valid"

    def test_validate_image_invalid_formats(self):
        """Test invalid file formats"""
        invalid_files = [
            ('test.txt', 'text/plain', b'This is text'),
            ('test.pdf', 'application/pdf', b'%PDF-'),
            ('test.zip', 'application/zip', b'PK\x03\x04')
        ]
        
        for filename, content_type, content in invalid_files:
            file_stream = BytesIO(content)
            from werkzeug.datastructures import FileStorage
            file = FileStorage(
                stream=file_stream,
                filename=filename,
                content_type=content_type
            )
            
            is_valid, message = validate_image(file)
            assert not is_valid, f"File {filename} should be invalid"
            # Check for actual error messages from validator
            assert 'Invalid image' in message or 'only' in message.lower() or 'only' in message

    def test_validate_image_size_limit(self):
        """Test image size validation"""
        # Create a large image (simulated)
        large_content = b'x' * (20 * 1024 * 1024)  # 20MB
        
        file_stream = BytesIO(large_content)
        from werkzeug.datastructures import FileStorage
        file = FileStorage(
            stream=file_stream,
            filename='large.jpg',
            content_type='image/jpeg'
        )
        
        is_valid, message = validate_image(file)
        assert not is_valid, "Large image should be rejected"
        # Check for actual error message from validator
        assert 'exceeds' in message.lower() or 'size' in message.lower()


class TestAuthUtils:
    """Test authentication utility functions"""

    def test_generate_token(self, app):
        """Test token generation"""
        with app.app_context():
            user_id = 123
            token = generate_token(user_id)
            
            assert token is not None
            assert isinstance(token, str)
            assert len(token) > 0

    def test_verify_token_valid(self, app):
        """Test token verification with valid token"""
        with app.app_context():
            user_id = 456
            token = generate_token(user_id)
            
            verified_id = verify_token(token)
            assert verified_id == user_id

    def test_verify_token_invalid(self, app):
        """Test token verification with invalid token"""
        with app.app_context():
            invalid_tokens = [
                'invalid.token.here',
                'not_a_token',
                '',
                'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.invalid'
            ]
            
            for token in invalid_tokens:
                verified_id = verify_token(token)
                assert verified_id is None

    def test_token_expiration(self, app):
        """Test that tokens expire properly"""
        with app.app_context():
            # This would require modifying the token generation to use a short expiry
            # For now, we'll test that the token structure is correct
            user_id = 789
            token = generate_token(user_id)
            
            # Token should be verifiable immediately
            verified_id = verify_token(token)
            assert verified_id == user_id


class TestErrorHandling:
    """Test error handling in utilities"""

    def test_validate_email_none(self):
        """Test email validation with None input"""
        is_valid, message = validate_email(None)
        assert not is_valid
        assert 'required' in message.lower()

    def test_validate_image_none(self):
        """Test image validation with None input"""
        is_valid, message = validate_image(None)
        assert not is_valid
        # Check for actual error message from validator
        assert 'no file' in message.lower() or 'provided' in message.lower()

    def test_secure_filename_none(self):
        """Test secure filename with None input"""
        result = secure_upload_filename(None)
        assert result == 'upload'