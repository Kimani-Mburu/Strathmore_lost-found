"""Admin endpoints"""

from flask import request, jsonify
from app.routes import admin_bp
from app.models import Item, User, Claim
from app import db
from app.utils import require_auth

def require_admin(f):
    """Decorator to require admin role"""
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        current_user_id = kwargs.get('current_user_id')
        user = User.query.get(current_user_id)
        
        if not user or user.role != 'admin':
            return jsonify({'error': 'Admin access required'}), 403
        
        return f(*args, **kwargs)
    
    return decorated_function

@admin_bp.route('/items/pending', methods=['GET'])
@require_auth
@require_admin
def get_pending_items(current_user_id):
    """Get pending items for verification"""
    items = Item.query.filter_by(status='pending').all()
    
    return jsonify({
        'total': len(items),
        'items': [item.to_dict() for item in items]
    }), 200

@admin_bp.route('/items/<int:item_id>/verify', methods=['PUT'])
@require_auth
@require_admin
def verify_item(item_id, current_user_id):
    """Verify or reject an item"""
    item = Item.query.get(item_id)
    
    if not item:
        return jsonify({'error': 'Item not found'}), 404
    
    data = request.get_json() or {}
    action = data.get('action')  # 'approve' or 'reject'
    
    if action == 'approve':
        item.is_verified = True
        item.status = 'verified'
    elif action == 'reject':
        item.status = 'rejected'
    else:
        return jsonify({'error': 'Invalid action'}), 400
    
    db.session.commit()
    
    return jsonify({
        'message': f'Item {action}d successfully',
        'item': item.to_dict()
    }), 200

@admin_bp.route('/items/<int:item_id>/status', methods=['PUT'])
@require_auth
@require_admin
def update_item_status(item_id, current_user_id):
    """Update item status"""
    item = Item.query.get(item_id)
    
    if not item:
        return jsonify({'error': 'Item not found'}), 404
    
    data = request.get_json() or {}
    new_status = data.get('status')
    item.status = new_status
    
    db.session.commit()
    
    return jsonify({
        'message': 'Item status updated',
        'item': item.to_dict()
    }), 200

# ============== CLAIMS MANAGEMENT ENDPOINTS ==============

@admin_bp.route('/claims/pending', methods=['GET'])
@require_auth
@require_admin
def get_pending_claims(current_user_id):
    """Get all pending claims awaiting admin review"""
    claims = Claim.query.filter_by(status='pending').all()
    
    # Include item and user details
    claims_data = []
    for claim in claims:
        claim_dict = claim.to_dict()
        claim_dict['item'] = claim.item.to_dict() if claim.item else None
        claim_dict['claimer'] = claim.user.to_dict() if claim.user else None
        claim_dict['item_reporter'] = claim.item.reporter.to_dict() if claim.item and claim.item.reporter else None
        claims_data.append(claim_dict)
    
    return jsonify({
        'total': len(claims_data),
        'claims': claims_data
    }), 200

@admin_bp.route('/claims/all', methods=['GET'])
@require_auth
@require_admin
def get_all_claims(current_user_id):
    """Get all claims (all statuses)"""
    status = request.args.get('status')  # Optional filter by status
    
    if status:
        claims = Claim.query.filter_by(status=status).all()
    else:
        claims = Claim.query.all()
    
    # Include item and user details
    claims_data = []
    for claim in claims:
        claim_dict = claim.to_dict()
        claim_dict['item'] = claim.item.to_dict() if claim.item else None
        claim_dict['claimer'] = claim.user.to_dict() if claim.user else None
        claim_dict['item_reporter'] = claim.item.reporter.to_dict() if claim.item and claim.item.reporter else None
        claims_data.append(claim_dict)
    
    return jsonify({
        'total': len(claims_data),
        'claims': claims_data
    }), 200

@admin_bp.route('/claims/<int:claim_id>/approve', methods=['PUT'])
@require_auth
@require_admin
def approve_claim(claim_id, current_user_id):
    """Approve a claim - mark item as claimed and transfer ownership"""
    claim = Claim.query.get(claim_id)
    
    if not claim:
        return jsonify({'error': 'Claim not found'}), 404
    
    claim.status = 'approved'
    
    # Mark item as claimed
    if claim.item:
        claim.item.status = 'claimed'
    
    db.session.commit()
    
    return jsonify({
        'message': 'Claim approved successfully',
        'claim': claim.to_dict()
    }), 200

@admin_bp.route('/claims/<int:claim_id>/reject', methods=['PUT'])
@require_auth
@require_admin
def reject_claim(claim_id, current_user_id):
    """Reject a claim"""
    claim = Claim.query.get(claim_id)
    
    if not claim:
        return jsonify({'error': 'Claim not found'}), 404
    
    claim.status = 'rejected'
    
    db.session.commit()
    
    return jsonify({
        'message': 'Claim rejected',
        'claim': claim.to_dict()
    }), 200

@admin_bp.route('/claims/<int:claim_id>/notes', methods=['PUT'])
@require_auth
@require_admin
def update_claim_notes(claim_id, current_user_id):
    """Update admin notes on a claim"""
    claim = Claim.query.get(claim_id)
    
    if not claim:
        return jsonify({'error': 'Claim not found'}), 404
    
    data = request.get_json() or {}
    notes = data.get('notes', '')
    claim.notes = notes
    
    db.session.commit()
    
    return jsonify({
        'message': 'Claim notes updated',
        'claim': claim.to_dict()
    }), 200

