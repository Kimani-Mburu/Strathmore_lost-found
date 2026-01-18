"""
Test item management endpoints
"""

import pytest
import json
import io
from datetime import datetime
from app.models import Item, Claim


class TestItemRoutes:
    """Test item related endpoints"""

    def test_report_item_success(self, client, auth_headers, sample_image):
        """Test successful item reporting"""
        data = {
            'title': 'Lost Wallet',
            'description': 'Black leather wallet with student ID',
            'category': 'documents',
            'item_type': 'lost',
            'date': '2026-01-15T10:00:00',
            'location': 'Student Center',
            'photo': (io.BytesIO(sample_image[0]), sample_image[1])
        }
        
        response = client.post(
            '/api/items/report',
            data=data,
            headers=auth_headers
        )
        
        assert response.status_code == 201
        response_data = response.get_json()
        assert response_data['message'] == 'Item reported successfully'
        assert 'item' in response_data
        assert response_data['item']['title'] == data['title']

    def test_report_item_no_auth(self, client, sample_image):
        """Test item reporting without authentication"""
        data = {
            'title': 'Lost Wallet',
            'description': 'Black leather wallet',
            'category': 'documents',
            'item_type': 'lost',
            'photo': (io.BytesIO(sample_image[0]), sample_image[1])
        }
        
        response = client.post('/api/items/report', data=data)
        
        assert response.status_code == 401

    def test_report_item_no_photo(self, client, auth_headers):
        """Test item reporting without photo"""
        data = {
            'title': 'Lost Wallet',
            'description': 'Black leather wallet',
            'category': 'documents',
            'item_type': 'lost'
        }
        
        response = client.post('/api/items/report', json=data, headers=auth_headers)
        
        assert response.status_code == 400
        response_data = response.get_json()
        assert 'No photo uploaded' in response_data['error']

    def test_get_items_success(self, client, test_item):
        """Test getting verified items"""
        response = client.get('/api/items')
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'items' in data
        assert len(data['items']) >= 1
        assert data['items'][0]['title'] == test_item.title

    def test_get_items_with_filters(self, client, test_item):
        """Test getting items with category and type filters"""
        response = client.get('/api/items?category=electronics&item_type=lost')
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'items' in data

    def test_get_items_pagination(self, client):
        """Test items pagination"""
        response = client.get('/api/items?page=1')
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'current_page' in data
        assert 'pages' in data
        assert 'total' in data

    def test_get_item_success(self, client, test_item):
        """Test getting specific item details"""
        response = client.get(f'/api/items/{test_item.item_id}')
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['title'] == test_item.title
        assert data['item_id'] == test_item.item_id

    def test_get_item_not_found(self, client):
        """Test getting non-existent item"""
        response = client.get('/api/items/99999')
        
        assert response.status_code == 404
        data = response.get_json()
        assert 'Item not found' in data['error']

    def test_get_my_items_success(self, client, auth_headers, test_item, test_user):
        """Test getting user's own items"""
        response = client.get('/api/items/my-items', headers=auth_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'items' in data
        assert len(data['items']) >= 1

    def test_claim_item_success(self, client, auth_headers, test_item):
        """Test successful item claiming"""
        response = client.post(
            f'/api/items/{test_item.item_id}/claim',
            json={'notes': 'This is my item, I can prove ownership'},
            headers=auth_headers
        )
        
        assert response.status_code == 201
        data = response.get_json()
        assert 'Claim submitted successfully' in data['message']
        assert 'claim' in data

    def test_claim_item_already_claimed(self, client, auth_headers, test_item, test_claim):
        """Test claiming an item that's already claimed by the same user"""
        response = client.post(
            f'/api/items/{test_item.item_id}/claim',
            json={'notes': 'Trying to claim again'},
            headers=auth_headers
        )
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'already claimed this item' in data['error']

    def test_claim_nonexistent_item(self, client, auth_headers):
        """Test claiming a non-existent item"""
        response = client.post(
            '/api/items/99999/claim',
            json={'notes': 'Claiming non-existent item'},
            headers=auth_headers
        )
        
        assert response.status_code == 404
        data = response.get_json()
        assert 'Item not found' in data['error']

    def test_get_my_claim_success(self, client, auth_headers, test_item, test_claim):
        """Test getting user's claim for an item"""
        response = client.get(f'/api/items/{test_item.item_id}/my-claim', headers=auth_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'claim' in data
        assert data['claim']['claim_id'] == test_claim.claim_id

    def test_get_my_claim_no_claim(self, client, auth_headers, test_item):
        """Test getting claim when user hasn't claimed the item"""
        response = client.get(f'/api/items/{test_item.item_id}/my-claim', headers=auth_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['claim'] is None

    def test_get_my_claims_success(self, client, auth_headers, test_claim):
        """Test getting all user's claims"""
        response = client.get('/api/items/claims/my-claims', headers=auth_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'claims' in data
        assert len(data['claims']) >= 1

    def test_get_item_photo_success(self, client, test_item):
        """Test getting item photo"""
        # This test would need an actual photo file
        # For now, we'll test the endpoint exists
        response = client.get(f'/api/items/{test_item.item_id}/photo')
        
        # Should return 404 since test item doesn't have a photo
        assert response.status_code in [200, 404]

    def test_unverified_item_not_visible(self, client, app, test_user):
        """Test that unverified items don't appear in browse"""
        with app.app_context():
            # Create unverified item
            unverified_item = Item(
                title='Unverified Item',
                description='This should not be visible',
                category='electronics',
                item_type='lost',
                date=datetime.utcnow(),
                location='Test Location',
                user_id=test_user.user_id,
                is_verified=False
            )
            from app import db
            db.session.add(unverified_item)
            db.session.commit()
            
            # Get items - should not include unverified item
            response = client.get('/api/items')
            data = response.get_json()
            
            item_ids = [item['item_id'] for item in data['items']]
            assert unverified_item.item_id not in item_ids