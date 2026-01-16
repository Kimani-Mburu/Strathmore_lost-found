"""Item model for lost and found items"""

from app import db
from datetime import datetime

class Item(db.Model):
    __tablename__ = 'items'
    
    item_id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(100), nullable=False)
    item_type = db.Column(db.String(50), nullable=False)  # 'lost' or 'found'
    photo_path = db.Column(db.String(500), nullable=True)
    status = db.Column(db.String(50), default='pending')  # 'pending', 'verified', 'claimed', 'rejected'
    date = db.Column(db.DateTime, nullable=False)
    location = db.Column(db.String(255), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    is_verified = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    claims = db.relationship('Claim', backref='item', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'item_id': self.item_id,
            'title': self.title,
            'description': self.description,
            'category': self.category,
            'item_type': self.item_type,
            'photo_path': self.photo_path,
            'status': self.status,
            'date': self.date.isoformat(),
            'location': self.location,
            'user_id': self.user_id,
            'is_verified': self.is_verified,
            'created_at': self.created_at.isoformat()
        }
