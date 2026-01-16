# ⚡ Quick Start Guide

Get the Strathmore Lost & Found application up and running in 5 minutes!

## Prerequisites
- Python 3.8+
- Git
- ~500MB disk space

## Installation

### Step 1: Clone Repository
```bash
git clone https://github.com/YOUR_REPO_URL/lostnfound.git
cd lostnfound
```

### Step 2: Run Setup Script

**Windows:**
```bash
setup.bat
```

**Linux/Mac:**
```bash
bash setup.sh
```

This will:
- Create virtual environment
- Install dependencies
- Initialize database
- Create admin user

### Step 3: Start Backend Server

**Windows:**
```bash
cd backend
python run.py
```

**Linux/Mac:**
```bash
cd backend
python run.py
```

You should see:
```
🚀 Starting Strathmore Lost & Found Backend...
📝 API running at http://localhost:5000/api
🔗 Frontend at http://localhost:5000
```

### Step 4: Open Application
Navigate to: **http://localhost:5000**

## First Steps

### 1. Create Your Account
- Click "Register"
- Use your Strathmore email: `your.name@strathmore.ac.ke`
- Set a password
- Click "Register"

### 2. Login
- Use your email and password
- You'll be redirected to your dashboard

### 3. Report an Item
- Click "Report Item"
- Fill in item details
- Upload a photo
- Submit
- Your item will appear in "My Dashboard" (admin must verify before it shows in browse)

### 4. Browse Items
- Click "Browse Items" or category links
- Click on items to view details
- Click "Claim" to claim an item if you own it

### 5. View Admin Dashboard (Admin Only)
- Login with: `admin@strathmore.ac.ke` / `admin123`
- You'll be redirected to admin dashboard
- Verify pending items
- Approve/reject claims

## Key Credentials

**Admin Account:**
```
Email: admin@strathmore.ac.ke
Password: admin123
```

Create your own regular account with a Strathmore email.

## Troubleshooting

### Port 5000 in use?
```bash
# Check what's using port 5000
# Windows
netstat -ano | findstr :5000

# Linux/Mac
lsof -i :5000

# Kill the process and run setup again
```

### Database error?
```bash
cd backend
python init_db.py
python run.py
```

### Virtual environment issues?
```bash
# Remove old environment
rm -r .venv venv

# Run setup again
bash setup.sh  # or setup.bat on Windows
```

## Project Features

✅ User authentication with Strathmore email only  
✅ Report lost/found items with photos  
✅ Browse and search functionality  
✅ Claim system with admin verification  
✅ User dashboard to track items/claims  
✅ Admin dashboard for verification  
✅ Responsive design (mobile & desktop)  

## File Structure

```
backend/              # Flask API server
├── app/             # Application code
├── run.py           # Start the server
└── requirements.txt # Dependencies

README.md            # Full documentation
CONTRIBUTING.md      # Contribution guidelines
.gitignore          # Git ignore rules
database/           # Database schema
```

## Common Commands

```bash
# Start backend
cd backend
python run.py

# Initialize database
python init_db.py

# Test API (requires requests library)
python test_api.py

# View logs
# Check browser console: F12 → Console
```

## Need Help?

1. Check [README.md](README.md) for detailed documentation
2. See [backend/API_DOCUMENTATION.md](backend/API_DOCUMENTATION.md) for API reference
3. Read [CONTRIBUTING.md](CONTRIBUTING.md) to contribute
4. Open an issue on GitHub

## Next Steps

1. ✅ Application is running
2. 📝 Explore the features
3. 🐛 Report bugs if found
4. 💡 Suggest improvements
5. 🤝 Contribute code!

---

**Happy coding!** 🚀
