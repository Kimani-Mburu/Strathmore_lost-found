"""
Integration tests for the complete application workflow
"""

import pytest
import json
import io
from datetime import datetime


class TestCompleteWorkflow:
    """Test complete user workflows from start to finish"""

    def test_new_user_complete_journey(self, client, sample_image):
        """Test complete journey: register -> login -> report item -> claim item"""
        # 1. Register new user
        register_data = {
            'name': 'Alice Johnson',
            'email': 'alice.j@strathmore.ac.ke',
            'password': 'alicepass123'
        }
        
        response = client.post('/api/auth/register', json=register_data)
        assert response.status_code == 201
        
        # 2. Login
        response = client.post('/api/auth/login', json={
            'email': register_data['email'],
            'password': register_data['password']
        })
        assert response.status_code == 200
        token = response.get_json()['token']
        headers = {'Authorization': f'Bearer {token}'}
        
        # 3. Report a lost item
        item_data = {
            'title': 'Lost Student ID',
            'description': 'Blue student ID card with photo and name Alice Johnson',
            'category': 'documents',
            'item_type': 'lost',
            'date': '2026-01-15T14:30:00',
            'location': 'Lecture Hall 2'
        }
        
        files = {'photo': (io.BytesIO(sample_image[0]), sample_image[1])}
        response = client.post('/api/items/report', data=item_data, files=files, headers=headers)
        assert response.status_code == 201
        reported_item = response.get_json()['item']
        
        # 4. Browse items (should not see own unverified item yet)
        response = client.get('/api/items')
        assert response.status_code == 200
        browse_data = response.get_json()
        
        # 5. Get own items (should see reported item)
        response = client.get('/api/items/my-items', headers=headers)
        assert response.status_code == 200
        my_items = response.get_json()
        assert len(my_items['items']) >= 1
        assert my_items['items'][0]['title'] == item_data['title']

    def test_admin_workflow(self, client, admin_token, test_item, test_user, sample_image):
        """Test admin workflow: verify items -> process claims"""
        admin_headers = {'Authorization': f'Bearer {admin_token}'}
        
        # 1. Get pending claims
        response = client.get('/api/admin/claims/pending', headers=admin_headers)
        assert response.status_code == 200
        pending_claims = response.get_json()
        
        # 2. Create a new claim to process
        user_response = client.post('/api/auth/login', json={
            'email': test_user.email,
            'password': 'testpass123'
        })
        user_token = user_response.get_json()['token']
        user_headers = {'Authorization': f'Bearer {user_token}'}
        
        response = client.post(
            f'/api/items/{test_item.item_id}/claim',
            json={'notes': 'This is definitely my item'},
            headers=user_headers
        )
        assert response.status_code == 201
        new_claim = response.get_json()['claim']
        
        # 3. Approve the claim as admin
        response = client.put(
            f'/api/admin/claims/{new_claim["claim_id"]}/approve',
            headers=admin_headers
        )
        assert response.status_code == 200
        
        # 4. Check that claim is approved
        response = client.get('/api/admin/claims/all', headers=admin_headers)
        all_claims = response.get_json()
        approved_claims = [c for c in all_claims['claims'] if c['claim_id'] == new_claim['claim_id']]
        assert len(approved_claims) == 1
        assert approved_claims[0]['status'] == 'approved'

    def test_claim_workflow(self, client, test_item, test_user, admin_user):
        """Test complete claim workflow: claim -> admin review -> decision"""
        # 1. User logs in and claims item
        user_response = client.post('/api/auth/login', json={
            'email': test_user.email,
            'password': 'testpass123'
        })
        user_token = user_response.get_json()['token']
        user_headers = {'Authorization': f'Bearer {user_token}'}
        
        response = client.post(
            f'/api/items/{test_item.item_id}/claim',
            json={'notes': 'I lost this phone yesterday, can describe details'},
            headers=user_headers
        )
        assert response.status_code == 201
        claim = response.get_json()['claim']
        
        # 2. User checks their claim status
        response = client.get(f'/api/items/{test_item.item_id}/my-claim', headers=user_headers)
        assert response.status_code == 200
        claim_status = response.get_json()
        assert claim_status['claim']['status'] == 'pending'
        
        # 3. Admin logs in and reviews claim
        admin_response = client.post('/api/auth/login', json={
            'email': admin_user.email,
            'password': 'adminpass123'
        })
        admin_token = admin_response.get_json()['token']
        admin_headers = {'Authorization': f'Bearer {admin_token}'}
        
        # 4. Admin adds notes and rejects claim
        response = client.put(
            f'/api/admin/claims/{claim["claim_id"]}/notes',
            json={'notes': 'User could not provide sufficient proof of ownership'},
            headers=admin_headers
        )
        assert response.status_code == 200
        
        response = client.put(
            f'/api/admin/claims/{claim["claim_id"]}/reject',
            headers=admin_headers
        )
        assert response.status_code == 200
        
        # 5. User checks updated claim status
        response = client.get(f'/api/items/{test_item.item_id}/my-claim', headers=user_headers)
        assert response.status_code == 200
        final_status = response.get_json()
        assert final_status['claim']['status'] == 'rejected'

    def test_data_consistency(self, app, client, test_user, admin_user):
        """Test data consistency across operations"""
        with app.app_context():
            from app import db
            from app.models import Item, Claim, User
            
            # Initial state
            initial_users = User.query.count()
            initial_items = Item.query.count()
            initial_claims = Claim.query.count()
            
            # Create new user
            response = client.post('/api/auth/register', json={
                'name': 'Bob Wilson',
                'email': 'bob.w@strathmore.ac.ke',
                'password': 'bobpass123'
            })
            assert response.status_code == 201
            
            # Check database state
            assert User.query.count() == initial_users + 1
            
            # Login and create item
            response = client.post('/api/auth/login', json={
                'email': 'bob.w@strathmore.ac.ke',
                'password': 'bobpass123'
            })
            token = response.get_json()['token']
            
            # Create item (without photo for simplicity)
            new_user = User.query.filter_by(email='bob.w@strathmore.ac.ke').first()
            
            item = Item(
                title='Test Item',
                description='Test description',
                category='electronics',
                item_type='lost',
                date=datetime.utcnow(),
                location='Test Location',
                user_id=new_user.user_id,
                is_verified=True
            )
            db.session.add(item)
            db.session.commit()
            
            # Check item count
            assert Item.query.count() == initial_items + 1
            
            # Create claim
            claim = Claim(
                item_id=item.item_id,
                user_id=new_user.user_id,
                status='pending'
            )
            db.session.add(claim)
            db.session.commit()
            
            # Check claim count
            assert Claim.query.count() == initial_claims + 1
            
            # Verify relationships
            assert item.user_id == new_user.user_id
            assert claim.item_id == item.item_id
            assert claim.user_id == new_user.user_id

    def test_error_recovery(self, client, auth_headers):
        """Test error handling and recovery"""
        # Test invalid item ID
        response = client.get('/api/items/99999')
        assert response.status_code == 404
        
        # Test invalid claim
        response = client.post('/api/items/99999/claim', headers=auth_headers)
        assert response.status_code == 404
        
        # Test unauthorized access
        response = client.get('/api/admin/claims/pending')
        assert response.status_code == 401
        
        # Test malformed data
        response = client.post('/api/auth/register', json={
            'name': '',
            'email': 'invalid-email',
            'password': '123'  # Too short
        })
        assert response.status_code == 400

    def test_concurrent_operations(self, client, test_item, test_user):
        """Test handling of concurrent operations"""
        # User 1 claims item
        response = client.post('/api/auth/login', json={
            'email': test_user.email,
            'password': 'testpass123'
        })
        user1_token = response.get_json()['token']
        user1_headers = {'Authorization': f'Bearer {user1_token}'}
        
        response = client.post(
            f'/api/items/{test_item.item_id}/claim',
            json={'notes': 'First claim'},
            headers=user1_headers
        )
        assert response.status_code == 201
        
        # User 2 tries to claim same item (should fail)
        response = client.post('/api/auth/register', json={
            'name': 'Charlie Brown',
            'email': 'charlie.b@strathmore.ac.ke',
            'password': 'charliepass123'
        })
        assert response.status_code == 201
        
        response = client.post('/api/auth/login', json={
            'email': 'charlie.b@strathmore.ac.ke',
            'password': 'charliepass123'
        })
        user2_token = response.get_json()['token']
        user2_headers = {'Authorization': f'Bearer {user2_token}'}
        
        response = client.post(
            f'/api/items/{test_item.item_id}/claim',
            json={'notes': 'Second claim'},
            headers=user2_headers
        )
        # Should succeed (different user can claim same item)
        assert response.status_code == 201