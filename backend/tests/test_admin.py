"""
Test admin functionality endpoints
"""

import pytest
import json
from app.models import Item, Claim


class TestAdminRoutes:
    """Test admin related endpoints"""

    def test_get_pending_claims_success(self, client, admin_headers, test_claim):
        """Test getting pending claims as admin"""
        response = client.get('/api/admin/claims/pending', headers=admin_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'claims' in data
        assert len(data['claims']) >= 1

    def test_get_pending_claims_unauthorized(self, client, auth_headers):
        """Test getting pending claims as regular user"""
        response = client.get('/api/admin/claims/pending', headers=auth_headers)
        
        assert response.status_code == 403
        data = response.get_json()
        assert 'Admin access required' in data['error']

    def test_get_all_claims_success(self, client, admin_headers, test_claim):
        """Test getting all claims as admin"""
        response = client.get('/api/admin/claims/all', headers=admin_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'claims' in data
        assert len(data['claims']) >= 1

    def test_approve_claim_success(self, client, admin_headers, test_claim):
        """Test approving a claim as admin"""
        response = client.put(
            f'/api/admin/claims/{test_claim.claim_id}/approve',
            headers=admin_headers
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'Claim approved successfully' in data['message']

    def test_approve_claim_unauthorized(self, client, auth_headers, test_claim):
        """Test approving a claim as regular user"""
        response = client.put(
            f'/api/admin/claims/{test_claim.claim_id}/approve',
            headers=auth_headers
        )
        
        assert response.status_code == 403
        data = response.get_json()
        assert 'Admin access required' in data['error']

    def test_reject_claim_success(self, client, admin_headers, app, test_claim):
        """Test rejecting a claim as admin"""
        # Create a new claim to reject (since we might have approved the test_claim)
        with app.app_context():
            from app import db
            new_claim = Claim(
                item_id=test_claim.item_id,
                user_id=test_claim.user_id,
                status='pending',
                notes='This claim will be rejected'
            )
            db.session.add(new_claim)
            db.session.commit()
            
            response = client.put(
                f'/api/admin/claims/{new_claim.claim_id}/reject',
                headers=admin_headers
            )
            
            assert response.status_code == 200
            data = response.get_json()
            assert 'Claim rejected successfully' in data['message']

    def test_add_claim_notes_success(self, client, admin_headers, test_claim):
        """Test adding notes to a claim as admin"""
        response = client.put(
            f'/api/admin/claims/{test_claim.claim_id}/notes',
            json={'notes': 'Admin notes: User provided good evidence'},
            headers=admin_headers
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'Notes added successfully' in data['message']

    def test_approve_nonexistent_claim(self, client, admin_headers):
        """Test approving a non-existent claim"""
        response = client.put('/api/admin/claims/99999/approve', headers=admin_headers)
        
        assert response.status_code == 404
        data = response.get_json()
        assert 'Claim not found' in data['error']

    def test_admin_dashboard_access(self, client, admin_headers):
        """Test that admin can access admin-specific endpoints"""
        # Test multiple admin endpoints
        endpoints = [
            '/api/admin/claims/pending',
            '/api/admin/claims/all'
        ]
        
        for endpoint in endpoints:
            response = client.get(endpoint, headers=admin_headers)
            assert response.status_code == 200

    def test_regular_user_cannot_access_admin(self, client, auth_headers):
        """Test that regular users cannot access admin endpoints"""
        endpoints = [
            '/api/admin/claims/pending',
            '/api/admin/claims/all',
            '/api/admin/claims/1/approve',
            '/api/admin/claims/1/reject'
        ]
        
        for endpoint in endpoints:
            response = client.get(endpoint, headers=auth_headers)
            assert response.status_code == 403

    def test_claim_approval_updates_item_status(self, client, admin_headers, app, test_item, test_user):
        """Test that approving a claim updates the item status"""
        with app.app_context():
            from app import db
            
            # Create a new claim to approve
            claim = Claim(
                item_id=test_item.item_id,
                user_id=test_user.user_id,
                status='pending'
            )
            db.session.add(claim)
            db.session.commit()
            
            # Approve the claim
            response = client.put(
                f'/api/admin/claims/{claim.claim_id}/approve',
                headers=admin_headers
            )
            
            assert response.status_code == 200
            
            # Check that item status is updated
            updated_item = Item.query.get(test_item.item_id)
            assert updated_item.status == 'claimed'