"""Enhanced item endpoints with security improvements"""

from flask import request, jsonify, send_file, current_app
from app.routes import items_bp
from app.models import Item, User
from app import db
from app.utils import require_auth
from app.utils.validators import validate_image, secure_upload_filename, validate_item_data, sanitize_text_input, validate_search_query
from app.utils.security import rate_limit, log_security_event, detect_suspicious_activity
from datetime import datetime
import os

@items_bp.route('/report', methods=['POST'])
@require_auth
@rate_limit('upload')
def report_item(current_user_id):
    """Enhanced item reporting with validation"""
    print(f"\n[REPORT] Starting item report for user {current_user_id}")
    
    # Check for suspicious activity
    if detect_suspicious_activity():
        print(f"[REPORT] Suspicious activity detected for user {current_user_id}")
        log_security_event('suspicious_upload', f'User {current_user_id} making rapid uploads')
    
    # Validate photo upload
    if 'photo' not in request.files:
        print(f"[REPORT] No photo uploaded")
        return jsonify({'error': 'No photo uploaded'}), 400
    
    file = request.files['photo']
    print(f"[REPORT] Photo received: {file.filename}")
    is_valid, message = validate_image(file)
    
    if not is_valid:
        print(f"[REPORT] Invalid image: {message}")
        log_security_event('invalid_image_upload', f'Invalid image: {message}')
        return jsonify({'error': message}), 400
    
    # Validate and sanitize form data
    form_data = {
        'title': request.form.get('title', ''),
        'description': request.form.get('description', ''),
        'category': request.form.get('category', ''),
        'item_type': request.form.get('item_type', 'lost'),
        'date': request.form.get('date', ''),
        'location': request.form.get('location', '')
    }
    print(f"[REPORT] Form data received: title={form_data['title']}, category={form_data['category']}")
    
    errors, sanitized = validate_item_data(form_data)
    
    if errors:
        print(f"[REPORT] Validation errors: {errors}")
        return jsonify({'error': 'Validation failed', 'details': errors}), 400
    
    # Save file with secure filename
    filename = secure_upload_filename(file.filename)
    timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S_')
    filename = timestamp + filename
    
    filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
    
    try:
        file.save(filepath)
        
        # Create item record with sanitized data
        item = Item(
            title=sanitized['title'],
            description=sanitized['description'],
            category=sanitized['category'],
            item_type=sanitized['item_type'],
            photo_path=f'uploads/{filename}',
            date=sanitized['date'],
            location=sanitized['location'],
            user_id=current_user_id
        )
        
        db.session.add(item)
        db.session.commit()
        
        log_security_event('item_reported', f'Item reported by user {current_user_id}: {item.title}')
        
        return jsonify({
            'message': 'Item reported successfully',
            'item': item.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        log_security_event('item_upload_error', f'Error saving item: {str(e)}')
        
        # Clean up uploaded file if database save failed
        if os.path.exists(filepath):
            os.remove(filepath)
        
        return jsonify({'error': 'Failed to save item. Please try again.'}), 500

@items_bp.route('/my-items', methods=['GET'])
@require_auth
def get_my_items(current_user_id):
    """Get current user's items (both pending and verified)"""
    items = Item.query.filter_by(user_id=current_user_id).all()
    
    return jsonify({
        'total': len(items),
        'items': [item.to_dict() for item in items]
    }), 200

@items_bp.route('', methods=['GET'])
@rate_limit('default')
def get_items():
    """Enhanced item browsing with advanced search and filtering"""
    # Get query parameters
    category = request.args.get('category')
    item_type = request.args.get('item_type')
    search_query = request.args.get('q', '')
    location = request.args.get('location')
    date_from = request.args.get('date_from')
    date_to = request.args.get('date_to')
    sort_by = request.args.get('sort', 'created_at')  # created_at, date, title
    sort_order = request.args.get('order', 'desc')  # desc, asc
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 20, type=int), 100)  # Max 100 per page
    
    # Validate and sanitize search query
    if search_query:
        search_query, error = validate_search_query(search_query)
        if error:
            return jsonify({'error': error}), 400
    
    # Build base query
    query = Item.query.filter_by(is_verified=True)
    
    # Apply filters
    if category:
        valid_categories = ['electronics', 'documents', 'clothing', 'accessories', 'books', 'others']
        if category in valid_categories:
            query = query.filter_by(category=category)
    
    if item_type:
        if item_type in ['lost', 'found']:
            query = query.filter_by(item_type=item_type)
    
    if location:
        location = sanitize_text_input(location, max_length=255)
        if location:
            query = query.filter(Item.location.ilike(f'%{location}%'))
    
    # Date range filter
    if date_from:
        try:
            date_from_obj = datetime.fromisoformat(date_from.replace('Z', '+00:00'))
            query = query.filter(Item.date >= date_from_obj)
        except ValueError:
            return jsonify({'error': 'Invalid date_from format'}), 400
    
    if date_to:
        try:
            date_to_obj = datetime.fromisoformat(date_to.replace('Z', '+00:00'))
            query = query.filter(Item.date <= date_to_obj)
        except ValueError:
            return jsonify({'error': 'Invalid date_to format'}), 400
    
    # Search query (title and description)
    if search_query:
        search_term = f'%{search_query}%'
        query = query.filter(
            db.or_(
                Item.title.ilike(search_term),
                Item.description.ilike(search_term)
            )
        )
    
    # Apply sorting
    valid_sort_fields = ['created_at', 'date', 'title', 'location']
    if sort_by in valid_sort_fields:
        sort_column = getattr(Item, sort_by)
        if sort_order == 'asc':
            query = query.order_by(sort_column.asc())
        else:
            query = query.order_by(sort_column.desc())
    else:
        query = query.order_by(Item.created_at.desc())
    
    # Paginate results
    items = query.paginate(page=page, per_page=per_page)
    
    # Log search for analytics
    if search_query:
        log_security_event('item_search', f'Search query: "{search_query}" - Results: {items.total}')
    
    return jsonify({
        'total': items.total,
        'pages': items.pages,
        'current_page': page,
        'per_page': per_page,
        'items': [item.to_dict() for item in items.items],
        'filters': {
            'category': category,
            'item_type': item_type,
            'search_query': search_query,
            'location': location,
            'date_from': date_from,
            'date_to': date_to,
            'sort_by': sort_by,
            'sort_order': sort_order
        }
    }), 200

@items_bp.route('/<int:item_id>', methods=['GET'])
def get_item(item_id):
    """Get item details"""
    item = Item.query.get(item_id)
    
    if not item:
        return jsonify({'error': 'Item not found'}), 404
    
    return jsonify(item.to_dict()), 200

@items_bp.route('/<int:item_id>/photo', methods=['GET'])
def get_photo(item_id):
    """Get item photo"""
    item = Item.query.get(item_id)
    
    if not item or not item.photo_path:
        return jsonify({'error': 'Photo not found'}), 404
    
    filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], os.path.basename(item.photo_path))
    
    if not os.path.exists(filepath):
        return jsonify({'error': 'Photo file not found'}), 404
    
    return send_file(filepath), 200

@items_bp.route('/<int:item_id>/claim', methods=['POST'])
@require_auth
def claim_item(item_id, current_user_id):
    """Claim an item - creates a claim pending admin approval"""
    item = Item.query.get(item_id)
    
    if not item:
        return jsonify({'error': 'Item not found'}), 404
    
    from app.models import Claim
    
    # Check if user already has a pending claim on this item
    existing_claim = Claim.query.filter_by(item_id=item_id, user_id=current_user_id, status='pending').first()
    if existing_claim:
        return jsonify({'error': 'You have already claimed this item (pending approval)'}), 400
    
    # Create claim with pending status - admin will verify
    claim = Claim(
        item_id=item_id,
        user_id=current_user_id,
        status='pending',
        notes=request.json.get('notes') if request.json else None
    )
    
    db.session.add(claim)
    db.session.commit()
    
    return jsonify({
        'message': 'Claim submitted successfully! An admin will review it shortly.',
        'claim': claim.to_dict()
    }), 201

@items_bp.route('/<int:item_id>/my-claim', methods=['GET'])
@require_auth
def get_my_claim(item_id, current_user_id):
    """Get current user's claim status for an item"""
    from app.models import Claim
    
    claim = Claim.query.filter_by(item_id=item_id, user_id=current_user_id).first()
    
    if not claim:
        return jsonify({'claim': None}), 200
    
    return jsonify({'claim': claim.to_dict()}), 200

@items_bp.route('/claims/my-claims', methods=['GET'])
@require_auth
def get_my_claims(current_user_id):
    """Get all claims made by current user"""
    from app.models import Claim
    
    claims = Claim.query.filter_by(user_id=current_user_id).all()
    
    return jsonify({
        'total': len(claims),
        'claims': [claim.to_dict() for claim in claims]
    }), 200
