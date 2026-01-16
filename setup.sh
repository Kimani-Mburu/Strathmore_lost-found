#!/bin/bash
# Installation and Setup Script for Development

echo "Setting up Strathmore Digital Lost & Found Application..."

# Create virtual environment
python -m venv venv

# Activate virtual environment
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r backend/requirements.txt

# Initialize database
python backend/init_db.py

echo "Setup complete!"
echo "To start the backend server, run:"
echo "  source venv/bin/activate"
echo "  cd backend"
echo "  python run.py"
echo ""
echo "Then open frontend/index.html in your browser"
