"""Validation utilities"""

import re
import os
from werkzeug.utils import secure_filename

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
MAX_FILE_SIZE = 16 * 1024 * 1024  # 16MB

def validate_email(email):
    """Validate email format - must be Strathmore email"""
    # Check basic email format
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(pattern, email):
        return False
    
    # Check if it's a Strathmore email
    if not email.lower().endswith('@strathmore.ac.ke'):
        return False
    
    return True

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def validate_image(file):
    """Validate image file"""
    if not file:
        return False, 'No file provided'
    
    if file.filename == '':
        return False, 'No file selected'
    
    if not allowed_file(file.filename):
        return False, f'Only {", ".join(ALLOWED_EXTENSIONS)} files are allowed'
    
    # Check file size
    file.seek(0, os.SEEK_END)
    file_size = file.tell()
    file.seek(0)
    
    if file_size > MAX_FILE_SIZE:
        return False, f'File size exceeds {MAX_FILE_SIZE / 1024 / 1024}MB limit'
    
    return True, 'Valid'

def secure_upload_filename(filename):
    """Generate secure filename"""
    return secure_filename(filename)
