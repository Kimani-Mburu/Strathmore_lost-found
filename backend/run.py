"""
Main entry point for Flask application
Strathmore University Digital Lost & Found Web Application
"""

from app import create_app, db
from app.models import User, Item, Claim

app = create_app()

# Initialize database on startup
with app.app_context():
    db.create_all()
    
    # Create default admin user if doesn't exist
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
        print("✓ Admin user created: admin@strathmore.ac.ke / admin123")
    else:
        print("✓ Admin user already exists")

if __name__ == '__main__':
    print("\n🚀 Starting Strathmore Lost & Found Backend...")
    print("📝 API running at http://localhost:5000/api")
    print("🔗 Frontend at http://localhost:5000\n")
    app.run(debug=True, host='0.0.0.0', port=5000)
