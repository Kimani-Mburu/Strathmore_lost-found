"""Item endpoints"""

from flask import request, jsonify, send_file, current_app
from app.routes import items_bp
from app.models import Item, User
from app import db
from app.utils import require_auth, validate_image, secure_upload_filename
from datetime import datetime
import os

@items_bp.route('/report', methods=['POST'])
@require_auth
def report_item(current_user_id):
    """Report a lost or found item"""
    
    if 'photo' not in request.files:
        return jsonify({'error': 'No photo uploaded'}), 400
    
    file = request.files['photo']
    is_valid, message = validate_image(file)
    
    if not is_valid:
        return jsonify({'error': message}), 400
    
    # Save file
    filename = secure_upload_filename(file.filename)
    timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S_')
    filename = timestamp + filename
    
    filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)
    
    # Create item record
    item = Item(
        title=request.form.get('title'),
        description=request.form.get('description'),
        category=request.form.get('category'),
        item_type=request.form.get('item_type', 'lost'),
        photo_path=f'uploads/{filename}',
        date=datetime.fromisoformat(request.form.get('date', '')),
        location=request.form.get('location'),
        user_id=current_user_id
    )
    
    db.session.add(item)
    db.session.commit()
    
    return jsonify({
        'message': 'Item reported successfully',
        'item': item.to_dict()
    }), 201

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
def get_items():
    """Get all verified items"""
    category = request.args.get('category')
    item_type = request.args.get('item_type')
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    query = Item.query.filter_by(is_verified=True)
    
    if category:
        query = query.filter_by(category=category)
    
    if item_type:
        query = query.filter_by(item_type=item_type)
    
    items = query.paginate(page=page, per_page=per_page)
    
    return jsonify({
        'total': items.total,
        'pages': items.pages,
        'current_page': page,
        'items': [item.to_dict() for item in items.items]
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
