# 🔍 Strathmore University Digital Lost & Found Web Application

A modern, responsive web application for the Strathmore University community to report, browse, and claim lost or found items. Built with Flask backend and vanilla JavaScript frontend.

## 🎯 Features

### Core Features
- ✅ **User Authentication** - Secure registration and login with Strathmore email validation
- ✅ **Report Items** - Post lost/found items with photos and detailed descriptions
- ✅ **Browse & Search** - Filter items by category, location, or search keywords
- ✅ **Claim System** - Submit evidence-based claims for found items
- ✅ **Admin Dashboard** - Verify items and approve/reject claims
- ✅ **User Dashboard** - Track your reported items and claims
- ✅ **Real Image Upload** - Store and serve photos via backend API
- ✅ **Responsive Design** - Works perfectly on mobile, tablet, and desktop

### Business Rules
- 📧 **Strathmore Email Only** - Users must register with `@strathmore.ac.ke` email
- ⏳ **Claim Verification** - Claims require admin approval before items are marked as claimed
- ✓ **Item Verification** - All reported items must be verified by admin before appearing in browse
- 👤 **Role-Based Access** - Admin-only functions protected by role-based authorization

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- pip (Python package manager)
- Git

### Installation

#### Windows
```bash
# Clone repository
git clone <repository-url>
cd lostnfound

# Run setup script
setup.bat

# Start backend (in new terminal)
cd backend
python run.py
```

#### Linux/Mac
```bash
# Clone repository
git clone <repository-url>
cd lostnfound

# Run setup script
bash setup.sh

# Start backend (in new terminal)
cd backend
python run.py
```

### Access the Application
- **Frontend**: http://localhost:5000
- **API Base**: http://localhost:5000/api

## 📚 Default Credentials

**Admin Account:**
- Email: `admin@strathmore.ac.ke`
- Password: `admin123`

## 🏗️ Project Structure

```
lostnfound/
├── backend/
│   ├── app/
│   │   ├── __init__.py              # Flask app factory & routes
│   │   ├── models/                  # Database models
│   │   │   ├── user.py
│   │   │   ├── item.py
│   │   │   └── claim.py
│   │   ├── routes/                  # API endpoints
│   │   │   ├── auth_routes.py       # Authentication
│   │   │   ├── item_routes.py       # Items & claims
│   │   │   └── admin_routes.py      # Admin functions
│   │   ├── utils/                   # Utilities
│   │   │   ├── auth.py              # Token generation & verification
│   │   │   └── validators.py        # Email & file validation
│   │   ├── static/                  # Frontend files
│   │   │   ├── html files
│   │   │   ├── css/
│   │   │   └── js/
│   │   ├── uploads/                 # User-uploaded images
│   │   └── instance/                # Database file (git-ignored)
│   ├── run.py                       # Application entry point
│   ├── config.py                    # Configuration
│   ├── requirements.txt             # Python dependencies
│   └── API_DOCUMENTATION.md         # API reference
├── database/
│   └── SCHEMA.md                    # Database schema
├── .gitignore
├── README.md
├── setup.bat                        # Windows setup
├── setup.sh                         # Linux/Mac setup
└── digital_lost_found_web_app_technical_design_document.md
```

## 🔌 API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login user
- `GET /api/auth/profile` - Get current user profile

### Items
- `POST /api/items/report` - Report new item (requires auth)
- `GET /api/items` - Browse items
- `GET /api/items/my-items` - Get user's reported items (requires auth)
- `GET /api/items/{id}/photo` - Download item photo

### Claims
- `POST /api/items/{id}/claim` - Submit claim (requires auth)
- `GET /api/items/{id}/my-claim` - Check user's claim status
- `GET /api/items/claims/my-claims` - Get user's claims

### Admin (requires admin role)
- `GET /api/admin/claims/pending` - List pending claims
- `GET /api/admin/claims/all` - List all claims
- `PUT /api/admin/claims/{id}/approve` - Approve claim
- `PUT /api/admin/claims/{id}/reject` - Reject claim
- `PUT /api/admin/claims/{id}/notes` - Add notes to claim

See [API_DOCUMENTATION.md](backend/API_DOCUMENTATION.md) for detailed endpoint reference.

## 💻 Technology Stack

| Component | Technology |
|-----------|-----------|
| **Backend Framework** | Flask 2.3.3 |
| **Database ORM** | SQLAlchemy |
| **Database** | SQLite (dev), MySQL (production) |
| **Authentication** | Token-based (secure token store) |
| **Frontend** | HTML5, CSS3, Vanilla JavaScript |
| **File Upload** | Server-side file system |
| **API Style** | RESTful JSON |

## 🔐 Authentication & Security

- **Token-Based Auth**: Secure token generation and validation
- **Email Validation**: Only @strathmore.ac.ke emails allowed
- **Password Hashing**: SHA-256 hashing for stored passwords
- **CORS Support**: Cross-origin requests handled
- **Role-Based Access**: Admin vs regular user permissions

## 📋 Testing the Application

### Create a Test Account
```
Email: your.name@strathmore.ac.ke
Password: Your secure password
```

### Test Flow
1. **Register** with Strathmore email
2. **Login** with credentials
3. **Report Item** with photo
4. **Browse** to see other items
5. **Claim Item** if you own it
6. **Admin Dashboard** (if admin) to verify items/claims

## ⚙️ Configuration

Create `.env` file in `backend/` folder:
```
FLASK_ENV=development
FLASK_APP=run.py
DEBUG=True
```

## 📦 Dependencies

Backend dependencies listed in `backend/requirements.txt`:
- Flask
- Flask-SQLAlchemy
- Flask-CORS
- Werkzeug

Install with:
```bash
cd backend
pip install -r requirements.txt
```

## 🐛 Troubleshooting

### Port 5000 already in use
```bash
# Linux/Mac: Kill process on port 5000
lsof -ti:5000 | xargs kill -9

# Windows: Use different port
python run.py --port=5001
```

### Database issues
```bash
# Reinitialize database
cd backend
python init_db.py
```

### Login not working
- Verify Strathmore email format: `user@strathmore.ac.ke`
- Check database exists: `backend/instance/lostnfound.db`
- Check console logs for errors (F12 → Console)

## 🚀 Deployment

### Production Considerations
- Use HTTPS (SSL/TLS certificates)
- Switch to MySQL database
- Use cloud storage (AWS S3, Google Cloud Storage) for images
- Implement rate limiting
- Add email notifications
- Use environment variables for secrets
- Enable CORS only for trusted domains
- Set `DEBUG=False` in production

### Deployment Steps
1. Configure production database (MySQL)
2. Set environment variables
3. Use production WSGI server (Gunicorn)
4. Configure reverse proxy (Nginx)
5. Enable SSL/TLS
6. Set up automated backups

## 📝 Database Schema

See [database/SCHEMA.md](database/SCHEMA.md) for complete schema documentation.

**Main Tables:**
- `users` - User accounts and roles
- `items` - Lost/found items
- `claims` - Item claims

## 👥 Contributing

For contributions:
1. Create a feature branch
2. Make changes with clear commits
3. Test thoroughly
4. Submit pull request

## 📄 License

This project is created for Strathmore University.

## 📞 Support

For issues, questions, or suggestions, contact the development team.

---

**Last Updated**: January 2026  
**Version**: 1.0.0
