"""Enhanced validation utilities with security improvements"""

import re
import os
import html
from datetime import datetime, timedelta

# Try to import optional dependencies
try:
    import bleach
    HAS_BLEACH = True
except ImportError:
    HAS_BLEACH = False

try:
    from werkzeug.utils import secure_filename
    HAS_WERKZEUG = True
except ImportError:
    HAS_WERKZEUG = False
    # Fallback implementation
    def secure_filename(filename):
        filename = str(filename).strip(' \t\r\n')
        filename = re.sub(r'(?u)[^-\w.]', '', filename)
        filename = filename.strip(' .')
        return filename or 'upload'

try:
    from PIL import Image
    HAS_PIL = True
except ImportError:
    HAS_PIL = False
    # Create a dummy Image class for compatibility
    class Image:
        class ImageFile:
            pass

try:
    from io import BytesIO
except ImportError:
    try:
        from cStringIO import StringIO as BytesIO
    except ImportError:
        from StringIO import StringIO as BytesIO

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
MAX_FILE_SIZE = 16 * 1024 * 1024  # 16MB
MAX_IMAGE_DIMENSION = 4096  # Maximum width/height in pixels

# HTML sanitization configuration
ALLOWED_HTML_TAGS = []
ALLOWED_HTML_ATTRIBUTES = {}

def validate_email(email):
    """Validate email format with enhanced security checks"""
    if not email or not isinstance(email, str):
        return False, "Email is required and must be a string"
    
    email = email.strip().lower()
    
    # Length check
    if len(email) > 254:
        return False, "Email address is too long"
    
    # Check basic email format with more strict pattern
    pattern = r'^[a-zA-Z0-9]([a-zA-Z0-9._-]*[a-zA-Z0-9])?@[a-zA-Z0-9]([a-zA-Z0-9.-]*[a-zA-Z0-9])?\.[a-zA-Z]{2,}$'
    if not re.match(pattern, email):
        return False, "Invalid email format"
    
    # Check if it's a Strathmore email
    if not email.endswith('@strathmore.ac.ke'):
        return False, "Only @strathmore.ac.ke email addresses are allowed"
    
    # Additional security checks
    if '..' in email:
        return False, "Invalid email format"
    
    return True, "Email is valid"

def sanitize_text_input(text, max_length=None, allow_html=False):
    """Sanitize text input to prevent XSS and injection attacks"""
    if not text or not isinstance(text, str):
        return ""
    
    text = text.strip()
    
    # Length check
    if max_length and len(text) > max_length:
        text = text[:max_length]
    
    if HAS_BLEACH and allow_html:
        # Allow certain HTML tags but sanitize
        text = bleach.clean(
            text,
            tags=ALLOWED_HTML_TAGS,
            attributes=ALLOWED_HTML_ATTRIBUTES,
            strip=True
        )
    elif HAS_BLEACH:
        # Remove all HTML tags and entities
        text = bleach.clean(text, tags=[], strip=True)
    else:
        # Fallback: basic HTML tag removal
        text = re.sub(r'<[^>]+>', '', text)
    
    # Additional XSS protection
    text = html.escape(text)
    
    return text

def validate_item_data(data):
    """Validate and sanitize item report data"""
    errors = {}
    sanitized = {}
    
    # Title validation
    if not data.get('title'):
        errors['title'] = 'Title is required'
    else:
        title = sanitize_text_input(data['title'], max_length=255)
        if len(title) < 3:
            errors['title'] = 'Title must be at least 3 characters long'
        elif len(title) > 255:
            errors['title'] = 'Title must be less than 255 characters'
        else:
            sanitized['title'] = title
    
    # Description validation
    if not data.get('description'):
        errors['description'] = 'Description is required'
    else:
        description = sanitize_text_input(data['description'], max_length=2000)
        if len(description) < 10:
            errors['description'] = 'Description must be at least 10 characters long'
        elif len(description) > 2000:
            errors['description'] = 'Description must be less than 2000 characters'
        else:
            sanitized['description'] = description
    
    # Category validation
    valid_categories = ['electronics', 'documents', 'clothing', 'accessories', 'books', 'others']
    category = sanitize_text_input(data.get('category', ''), max_length=100)
    if not category or category not in valid_categories:
        errors['category'] = f'Category must be one of: {", ".join(valid_categories)}'
    else:
        sanitized['category'] = category
    
    # Item type validation
    valid_types = ['lost', 'found']
    item_type = sanitize_text_input(data.get('item_type', ''), max_length=50)
    if not item_type or item_type not in valid_types:
        errors['item_type'] = f'Item type must be either "lost" or "found"'
    else:
        sanitized['item_type'] = item_type
    
    # Location validation
    if not data.get('location'):
        errors['location'] = 'Location is required'
    else:
        location = sanitize_text_input(data['location'], max_length=255)
        if len(location) < 3:
            errors['location'] = 'Location must be at least 3 characters long'
        else:
            sanitized['location'] = location
    
    # Date validation
    if not data.get('date'):
        errors['date'] = 'Date is required'
    else:
        try:
            # Parse datetime-local format (no timezone info)
            date_str = data['date']
            if 'T' in date_str:
                date_obj = datetime.fromisoformat(date_str)
            else:
                date_obj = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            
            # Check if date is reasonable (not too far in past or future)
            now = datetime.utcnow()
            if date_obj > now + timedelta(days=30):
                errors['date'] = 'Date cannot be more than 30 days in the future'
            elif date_obj < now - timedelta(days=365):
                errors['date'] = 'Date cannot be more than 1 year in the past'
            else:
                sanitized['date'] = date_obj
        except (ValueError, TypeError):
            errors['date'] = 'Invalid date format'
    
    return errors, sanitized

def allowed_file(filename):
    """Check if file extension is allowed"""
    if not filename:
        return False
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def validate_image(file):
    """Enhanced image validation with security checks"""
    if not file:
        return False, 'No file provided'
    
    if not file.filename:
        return False, 'No file selected'
    
    # Check filename for security
    filename = file.filename
    if '..' in filename or '/' in filename or '\\' in filename:
        return False, 'Invalid filename'
    
    if not allowed_file(filename):
        return False, f'Only {", ".join(ALLOWED_EXTENSIONS)} files are allowed'
    
    # Check file size
    file.seek(0, os.SEEK_END)
    file_size = file.tell()
    file.seek(0)
    
    if file_size > MAX_FILE_SIZE:
        return False, f'File size exceeds {MAX_FILE_SIZE / 1024 / 1024}MB limit'
    
    if file_size == 0:
        return False, 'File is empty'
    
    # Validate image content if PIL is available
    if HAS_PIL:
        try:
            # Read file content
            file_content = file.read()
            file.seek(0)
            
            # Try to open with PIL to verify it's a valid image
            img = Image.open(BytesIO(file_content))
            
            # Check image dimensions
            width, height = img.size
            if width > MAX_IMAGE_DIMENSION or height > MAX_IMAGE_DIMENSION:
                return False, f'Image dimensions exceed {MAX_IMAGE_DIMENSION}x{MAX_IMAGE_DIMENSION} pixels'
            
            # Verify image format matches extension
            format_mapping = {
                'jpg': 'JPEG',
                'jpeg': 'JPEG',
                'png': 'PNG',
                'gif': 'GIF'
            }
            
            ext = filename.rsplit('.', 1)[1].lower()
            expected_format = format_mapping.get(ext)
            
            if expected_format and img.format and img.format.upper() != expected_format:
                return False, f'File extension does not match actual image format'
            
        except Exception as e:
            return False, f'Invalid image file: {str(e)}'
    
    return True, 'Image is valid'

def secure_upload_filename(filename):
    """Generate secure filename with enhanced security"""
    if not filename:
        return 'upload'
    
    # Remove path separators and dangerous characters
    filename = os.path.basename(filename)
    
    # Use secure_filename as base
    secure_name = secure_filename(filename)
    
    # If secure_filename returns empty, use a default
    if not secure_name:
        secure_name = 'upload'
    
    # Ensure it has an extension
    if '.' not in secure_name:
        secure_name += '.jpg'
    
    return secure_name

def validate_password_strength(password):
    """Validate password strength"""
    if not password or not isinstance(password, str):
        return False, "Password is required"
    
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    
    if len(password) > 128:
        return False, "Password must be less than 128 characters"
    
    # Check for common weak patterns
    weak_passwords = ['password', '12345678', 'qwerty123', 'strathmore', 'admin123']
    if password.lower() in weak_passwords:
        return False, "Password is too common and weak"
    
    # Check for at least one uppercase, one lowercase, and one digit
    has_upper = any(c.isupper() for c in password)
    has_lower = any(c.islower() for c in password)
    has_digit = any(c.isdigit() for c in password)
    
    if not (has_upper and has_lower and has_digit):
        return False, "Password must contain at least one uppercase letter, one lowercase letter, and one digit"
    
    return True, "Password is strong enough"

def validate_search_query(query):
    """Validate and sanitize search query"""
    if not query:
        return "", "Search query is empty"
    
    # Sanitize query
    sanitized = sanitize_text_input(query, max_length=200)
    
    # Check for SQL injection patterns
    dangerous_patterns = [
        r'union\s+select',
        r'drop\s+table',
        r'insert\s+into',
        r'delete\s+from',
        r'update\s+set',
        r'--',
        r'/\*.*\*/',
        r'xp_cmdshell',
        r'sp_executesql'
    ]
    
    for pattern in dangerous_patterns:
        if re.search(pattern, sanitized, re.IGNORECASE):
            return "", "Invalid search query"
    
    return sanitized, None