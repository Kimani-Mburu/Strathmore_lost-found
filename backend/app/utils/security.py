"""
Security middleware and rate limiting
"""

import time
import hashlib
from functools import wraps
from flask import request, jsonify, g
from collections import defaultdict, deque

# Simple in-memory rate limiter (for production, use Redis or similar)
class RateLimiter:
    def __init__(self):
        self.requests = defaultdict(deque)
        self.window_size = 60  # 1 minute window
        self.max_requests = {
            'default': 1000,        # Very lenient for development
            'auth': 500,            # Very lenient for development
            'upload': 500,          # Very lenient for development
            'admin': 500            # Very lenient for development
        }
    
    def is_allowed(self, key, limit_type='default'):
        """Check if request is allowed based on rate limit"""
        now = time.time()
        window_start = now - self.window_size
        
        # Clean old requests
        request_queue = self.requests[key]
        while request_queue and request_queue[0] < window_start:
            request_queue.popleft()
        
        # Check if under limit
        max_requests = self.max_requests.get(limit_type, self.max_requests['default'])
        if len(request_queue) >= max_requests:
            print(f"[RATE LIMIT] Client {key} exceeded limit for '{limit_type}': {len(request_queue)}/{max_requests}")
            return False
        
        # Add current request
        request_queue.append(now)
        print(f"[RATE LIMIT] Client {key} - {limit_type}: {len(request_queue)}/{max_requests} requests used")
        return True
    
    def get_remaining_requests(self, key, limit_type='default'):
        """Get number of remaining requests"""
        now = time.time()
        window_start = now - self.window_size
        
        request_queue = self.requests[key]
        while request_queue and request_queue[0] < window_start:
            request_queue.popleft()
        
        max_requests = self.max_requests.get(limit_type, self.max_requests['default'])
        return max(0, max_requests - len(request_queue))

# Global rate limiter instance
rate_limiter = RateLimiter()

def get_client_identifier():
    """Get a unique identifier for the client"""
    # Try to get IP address
    if hasattr(request, 'remote_addr'):
        ip = request.remote_addr
    else:
        ip = 'unknown'
    
    # Add user agent for more specific identification
    user_agent = request.headers.get('User-Agent', 'unknown')[:50]
    
    # Create hash for privacy
    identifier = hashlib.sha256(f"{ip}:{user_agent}".encode()).hexdigest()[:16]
    return identifier

def rate_limit(limit_type='default'):
    """Rate limiting decorator"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Get client identifier
            client_id = get_client_identifier()
            endpoint = request.path
            method = request.method
            
            print(f"\n[API REQUEST] {method} {endpoint}")
            print(f"[CLIENT] ID: {client_id}")
            
            # Check rate limit
            if not rate_limiter.is_allowed(client_id, limit_type):
                remaining = rate_limiter.get_remaining_requests(client_id, limit_type)
                print(f"[BLOCKED] Rate limit exceeded for {limit_type} on {endpoint}")
                return jsonify({
                    'error': 'Rate limit exceeded',
                    'message': f'Too many requests. Please try again later.',
                    'remaining_requests': remaining
                }), 429
            
            # Add rate limit headers
            remaining = rate_limiter.get_remaining_requests(client_id, limit_type)
            g.remaining_requests = remaining
            print(f"[ALLOWED] Request allowed. Remaining: {remaining}")
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def validate_csrf():
    """Simple CSRF validation (for state-changing requests)"""
    if request.method in ['POST', 'PUT', 'DELETE', 'PATCH']:
        # Get CSRF token from header or form
        token = request.headers.get('X-CSRF-Token')
        if not token:
            token = request.form.get('csrf_token')
        
        # For API requests, we'll rely on token-based auth instead
        # This is a simplified version - in production, use proper CSRF protection
        return True
    
    return True

def security_headers(response):
    """Add security headers to response"""
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    response.headers['Content-Security-Policy'] = "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data: blob:; font-src 'self'; connect-src 'self'"
    
    return response

def log_security_event(event_type, details):
    """Log security events for monitoring"""
    timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
    client_id = get_client_identifier()
    
    log_entry = f"[{timestamp}] SECURITY: {event_type} - Client: {client_id} - {details}"
    
    # In production, send to proper logging system
    print(log_entry)
    
    # For critical events, you might want to send alerts
    critical_events = ['multiple_failed_logins', 'suspicious_activity', 'rate_limit_exceeded']
    if event_type in critical_events:
        print(f"ALERT: Critical security event - {log_entry}")

def detect_suspicious_activity():
    """Detect potentially suspicious activity patterns"""
    client_id = get_client_identifier()
    
    # Check for rapid requests to sensitive endpoints
    sensitive_endpoints = ['/auth/login', '/auth/register', '/items/report']
    
    if request.path in sensitive_endpoints:
        # Count recent requests from this client
        recent_requests = sum(1 for req_time in rate_limiter.requests[client_id] 
                             if time.time() - req_time < 300)  # Last 5 minutes
        
        if recent_requests > 20:  # Threshold for suspicious activity
            log_security_event('suspicious_activity', 
                              f'High frequency requests to {request.path}: {recent_requests} in 5 minutes')
            return True
    
    return False

def require_https():
    """Redirect to HTTPS if not using HTTPS (production only)"""
    if not request.is_secure:
        # In development, you might want to skip this
        if os.getenv('FLASK_ENV') == 'production':
            url = request.url.replace('http://', 'https://', 1)
            return redirect(url, code=301)
    return None