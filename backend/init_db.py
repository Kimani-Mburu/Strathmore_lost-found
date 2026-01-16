"""
Database Schema and Initialization Script
Run this to set up the database structure
"""

from app import create_app, db
from app.models import User, Item, Claim

def init_db():
    """Initialize database"""
    app = create_app()
    
    with app.app_context():
        # Create all tables
        db.create_all()
        
        # Create default admin user (optional)
        admin = User.query.filter_by(email='admin@strathmore.ac.ke').first()
        if not admin:
            admin = User(
                name='Administrator',
                email='admin@strathmore.ac.ke',
                role='admin'
            )
            admin.set_password('admin123')
            db.session.add(admin)
            db.session.commit()
            print("Admin user created: admin@strathmore.ac.ke / admin123")
        
        print("Database initialized successfully!")

if __name__ == '__main__':
    init_db()
