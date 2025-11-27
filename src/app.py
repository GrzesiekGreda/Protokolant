"""
Flask application factory and configuration
"""

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO
import os

db = SQLAlchemy()
socketio = SocketIO()

def create_app():
    """Create and configure Flask application"""
    app = Flask(__name__, 
                template_folder='../templates',
                static_folder='../static')
    
    # Configuration
    app.config['SECRET_KEY'] = 'dev-secret-key-change-in-production'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///../data/protocols.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Ensure data directory exists
    os.makedirs(os.path.join(os.path.dirname(__file__), '..', 'data'), exist_ok=True)
    
    # Initialize database
    db.init_app(app)
    
    # Initialize SocketIO
    socketio.init_app(app, cors_allowed_origins="*", async_mode='threading')
    
    # Register routes
    with app.app_context():
        from . import routes
        from . import models
        
        # Create database tables
        db.create_all()
        
        # Register blueprints
        app.register_blueprint(routes.bp)
    
    return app
