from flask import Flask
from flask_cors import CORS
import os
import secrets

def create_app(test_config=None):
    """Flask application factory"""
    app = Flask(__name__, instance_relative_config=True)
    
    # Configure the app
    app.config.from_mapping(
        # Set a default secret key that will be overridden in production
        SECRET_KEY=os.environ.get('SECRET_KEY', secrets.token_hex(16)),
    )
    
    # Enable CORS
    CORS(app)
    
    if test_config is None:
        app.config.from_pyfile('config.py', silent=True)
    else:
        app.config.from_mapping(test_config)
    
    # Ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass
    
            # Register blueprints
        from app.routes import api, auth, main, questionnaire
        app.register_blueprint(api.bp)
        app.register_blueprint(auth.bp)
        app.register_blueprint(main.bp)
        app.register_blueprint(questionnaire.bp)
    
    return app