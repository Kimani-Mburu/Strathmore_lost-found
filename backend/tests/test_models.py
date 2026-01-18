"""
Test models and database functionality
"""

import pytest
from datetime import datetime, timedelta
from app.models import User, Item, Claim
from app import db


class TestUserModel:
    """Test User model functionality"""

    def test_create_user(self, app):
        """Test creating a new user"""
        with app.app_context():
            user = User(
                name='Test User',
                email='test@strathmore.ac.ke'
            )
            user.set_password('password123')
            
            db.session.add(user)
            db.session.commit()
            
            assert user.user_id is not None
            assert user.email == 'test@strathmore.ac.ke'
            assert user.role == 'user'  # Default role

    def test_user_password_hashing(self, app):
        """Test password hashing and verification"""
        with app.app_context():
            user = User(
                name='Test User',
                email='test@strathmore.ac.ke'
            )
            user.set_password('plaintext')
            
            assert user.password_hash != 'plaintext'
            assert user.check_password('plaintext')
            assert not user.check_password('wrong')

    def test_user_to_dict(self, app):
        """Test user serialization to dictionary"""
        with app.app_context():
            user = User(
                name='Test User',
                email='test@strathmore.ac.ke',
                role='admin'
            )
            user.set_password('password123')
            
            db.session.add(user)
            db.session.commit()
            
            user_dict = user.to_dict()
            assert user_dict['name'] == 'Test User'
            assert user_dict['email'] == 'test@strathmore.ac.ke'
            assert user_dict['role'] == 'admin'
            assert 'password_hash' not in user_dict  # Should not include password

    def test_user_relationships(self, app, test_user):
        """Test user relationships with items and claims"""
        with app.app_context():
            # User should have relationships defined
            assert hasattr(test_user, 'items')
            assert hasattr(test_user, 'claims')
            
            # Initially empty
            assert len(test_user.items) == 0
            assert len(test_user.claims) == 0


class TestItemModel:
    """Test Item model functionality"""

    def test_create_item(self, app, test_user):
        """Test creating a new item"""
        with app.app_context():
            item = Item(
                title='Lost Phone',
                description='Samsung Galaxy S21',
                category='electronics',
                item_type='lost',
                date=datetime.utcnow(),
                location='Library',
                user_id=test_user.user_id
            )
            
            db.session.add(item)
            db.session.commit()
            
            assert item.item_id is not None
            assert item.title == 'Lost Phone'
            assert item.is_verified is False  # Default value
            assert item.status == 'pending'  # Default value

    def test_item_to_dict(self, app, test_item):
        """Test item serialization to dictionary"""
        item_dict = test_item.to_dict()
        
        assert item_dict['title'] == test_item.title
        assert item_dict['category'] == test_item.category
        assert item_dict['item_type'] == test_item.item_type
        assert 'created_at' in item_dict

    def test_item_relationships(self, app, test_item):
        """Test item relationships with user and claims"""
        with app.app_context():
            # Item should have relationships defined
            assert hasattr(test_item, 'reporter')
            assert hasattr(test_item, 'claims')
            
            # Should have a reporter
            assert test_item.reporter is not None
            assert test_item.reporter.name == 'Test User'

    def test_item_verification(self, app, test_user):
        """Test item verification functionality"""
        with app.app_context():
            # Create unverified item
            item = Item(
                title='Unverified Item',
                description='Test description',
                category='documents',
                item_type='found',
                date=datetime.utcnow(),
                location='Test Location',
                user_id=test_user.user_id,
                is_verified=False
            )
            
            db.session.add(item)
            db.session.commit()
            
            assert item.is_verified is False
            
            # Verify the item
            item.is_verified = True
            db.session.commit()
            
            assert item.is_verified is True


class TestClaimModel:
    """Test Claim model functionality"""

    def test_create_claim(self, app, test_item, test_user):
        """Test creating a new claim"""
        with app.app_context():
            claim = Claim(
                item_id=test_item.item_id,
                user_id=test_user.user_id,
                status='pending',
                notes='This is my item'
            )
            
            db.session.add(claim)
            db.session.commit()
            
            assert claim.claim_id is not None
            assert claim.status == 'pending'
            assert claim.notes == 'This is my item'

    def test_claim_to_dict(self, app, test_claim):
        """Test claim serialization to dictionary"""
        claim_dict = test_claim.to_dict()
        
        assert claim_dict['claim_id'] == test_claim.claim_id
        assert claim_dict['status'] == test_claim.status
        assert claim_dict['notes'] == test_claim.notes
        assert 'claim_date' in claim_dict

    def test_claim_relationships(self, app, test_claim):
        """Test claim relationships with item and user"""
        with app.app_context():
            # Claim should have relationships defined
            assert hasattr(test_claim, 'item')
            assert hasattr(test_claim, 'user')
            
            # Should have related item and user
            assert test_claim.item is not None
            assert test_claim.user is not None
            assert test_claim.item.title == 'Test Lost Phone'
            assert test_claim.user.name == 'Test User'

    def test_claim_status_transitions(self, app, test_claim):
        """Test claim status transitions"""
        with app.app_context():
            # Initial status should be pending
            assert test_claim.status == 'pending'
            
            # Approve claim
            test_claim.status = 'approved'
            db.session.commit()
            assert test_claim.status == 'approved'
            
            # Reject claim
            test_claim.status = 'rejected'
            db.session.commit()
            assert test_claim.status == 'rejected'

    def test_cascade_delete_item(self, app, test_item, test_claim):
        """Test that deleting an item deletes its claims"""
        with app.app_context():
            item_id = test_item.item_id
            claim_id = test_claim.claim_id
            
            # Delete the item
            db.session.delete(test_item)
            db.session.commit()
            
            # Claim should be deleted too
            deleted_claim = Claim.query.get(claim_id)
            assert deleted_claim is None
            
            # Item should be deleted
            deleted_item = Item.query.get(item_id)
            assert deleted_item is None

    def test_timestamps(self, app, test_user):
        """Test that timestamps are properly set"""
        with app.app_context():
            # Create item and check timestamps
            before_creation = datetime.utcnow()
            item = Item(
                title='Test Item',
                description='Test description',
                category='electronics',
                item_type='lost',
                date=datetime.utcnow(),
                location='Test Location',
                user_id=test_user.user_id
            )
            db.session.add(item)
            db.session.commit()
            after_creation = datetime.utcnow()
            
            assert before_creation <= item.created_at <= after_creation
            assert item.updated_at == item.created_at
            
            # Update item and check updated_at
            before_update = datetime.utcnow()
            item.title = 'Updated Title'
            db.session.commit()
            after_update = datetime.utcnow()
            
            assert before_update <= item.updated_at <= after_update
            assert item.updated_at > item.created_at