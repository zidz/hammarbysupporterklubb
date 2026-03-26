"""Hammarby Supporterklubb Flask Application"""
import os
from flask import Flask
from werkzeug.middleware.proxy_fix import ProxyFix


def create_app():
    """Application factory for Flask app."""
    app = Flask(__name__, 
                template_folder='../frontend/templates',
                static_folder='../frontend/static')
    
    # Configure for HAProxy/ProxyFix
    app.wsgi_app = ProxyFix(
        app.wsgi_app,
        x_for=1,
        x_proto=1,
        x_host=1,
        x_prefix=1
    )
    
    # Configuration
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(__file__), 'uploads')
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
    
    # Ensure upload folder exists
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    # Register blueprints (to be added)
    # from backend.routes import main
    # app.register_blueprint(main.bp)
    
    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return 'Page not found', 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return 'Internal server error', 500
    
    return app


if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5000, debug=True)
