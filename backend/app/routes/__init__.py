"""API Routes"""

from flask import Blueprint

# Create blueprints
auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')
items_bp = Blueprint('items', __name__, url_prefix='/api/items')
admin_bp = Blueprint('admin', __name__, url_prefix='/api/admin')

# Import route handlers
from app.routes import auth_routes, item_routes, admin_routes
