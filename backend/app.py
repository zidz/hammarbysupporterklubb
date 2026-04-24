"""Hammarby Supporterklubb Flask Application"""
import os
from datetime import timedelta
from flask import Flask, request, render_template
from werkzeug.middleware.proxy_fix import ProxyFix
from flask_wtf.csrf import CSRFProtect
from backend.routes import bp, init_login

csrf = CSRFProtect()


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
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size (per test requirement)
    
    # Session configuration
    app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=30)
    
    # Session cookie security
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
    # Only enable SECURE in production (HTTPS)
    app.config['SESSION_COOKIE_SECURE'] = os.environ.get('FLASK_ENV') == 'production'
    
    # Ensure upload folder exists
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'news'), exist_ok=True)
    
    # Register blueprint
    app.register_blueprint(bp)
    
    # Initialize Flask-Login
    init_login(app)
    
    # Initialize CSRF protection
    csrf.init_app(app)
    
    # Security headers middleware
    @app.after_request
    def set_security_headers(response):
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'SAMEORIGIN'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        response.headers['Content-Security-Policy'] = "default-src 'self'; script-src 'self' 'unsafe-inline' cdn.quilljs.com; style-src 'self' 'unsafe-inline' fonts.googleapis.com; img-src 'self' data: https:; font-src 'self' fonts.gstatic.com;"
        return response
    
    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return render_template('errors/404.html') if request.accept_mimetypes.accept_html else 'Page not found', 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return render_template('errors/500.html') if request.accept_mimetypes.accept_html else 'Internal server error', 500
    
    return app


if __name__ == '__main__':
    app = create_app()
    port = int(os.environ.get('PORT', 5000))
    app.run(host='::', port=port, debug=True)
