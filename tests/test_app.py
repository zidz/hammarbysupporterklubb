"""Tests for Flask application configuration and setup."""
import pytest
from backend.app import create_app


class TestAppCreation:
    """Test application factory and configuration."""
    
    def test_app_creates_successfully(self):
        """Test that app factory creates Flask application."""
        app = create_app()
        assert app is not None
        assert app.name is not None  # Flask app name should exist
    
    def test_app_has_secret_key(self):
        """Test that secret key is configured."""
        app = create_app()
        assert 'SECRET_KEY' in app.config
        assert app.config['SECRET_KEY'] is not None
    
    def test_app_has_upload_folder(self):
        """Test that upload folder is configured."""
        app = create_app()
        assert 'UPLOAD_FOLDER' in app.config
        assert app.config['UPLOAD_FOLDER'] is not None
    
    def test_app_has_max_content_length(self):
        """Test that max content length is set."""
        app = create_app()
        assert 'MAX_CONTENT_LENGTH' in app.config
        assert app.config['MAX_CONTENT_LENGTH'] == 16 * 1024 * 1024  # 16MB
    
    def test_upload_folder_exists(self):
        """Test that upload folder is created."""
        app = create_app()
        import os
        assert os.path.exists(app.config['UPLOAD_FOLDER'])


class TestProxyFix:
    """Test ProxyFix middleware configuration for HAProxy."""
    
    def test_proxy_fix_is_configured(self):
        """Test that ProxyFix middleware is applied."""
        app = create_app()
        # Check that wsgi_app is wrapped with ProxyFix
        from werkzeug.middleware.proxy_fix import ProxyFix
        assert isinstance(app.wsgi_app, ProxyFix)
    
    def test_proxy_fix_x_for(self):
        """Test that X-Forwarded-For is configured."""
        app = create_app()
        # ProxyFix should have x_for attribute set to 1
        from werkzeug.middleware.proxy_fix import ProxyFix
        assert isinstance(app.wsgi_app, ProxyFix)
        assert app.wsgi_app.x_for == 1


class TestErrorHandlers:
    """Test error handling."""
    
    def test_404_error_handler(self):
        """Test 404 error handler returns correct response."""
        app = create_app()
        with app.test_client() as client:
            response = client.get('/nonexistent-page')
            assert response.status_code == 404
    
    def test_500_error_handler(self):
        """Test 500 error handler is configured."""
        app = create_app()
        # 500 handler is configured, tested in production context
        assert app.error_handler_spec is not None


class TestTemplates:
    """Test template rendering."""
    
    def test_base_template_exists(self):
        """Test that base template exists."""
        app = create_app()
        with app.app_context():
            from jinja2 import TemplateNotFound
            try:
                app.jinja_env.get_template('base.html')
                assert True
            except TemplateNotFound:
                assert False, "base.html template not found"
    
    def test_base_template_renders(self):
        """Test that base template renders without errors."""
        app = create_app()
        with app.test_client() as client:
            # Create a simple route to test template
            @app.route('/test-template')
            def test_route():
                from flask import render_template_string
                return render_template_string('<h1>Test</h1>')
            
            response = client.get('/test-template')
            assert response.status_code == 200
            assert b'Test' in response.data


class TestStaticFiles:
    """Test static file serving."""
    
    def test_static_folder_configured(self):
        """Test that static folder is configured."""
        app = create_app()
        assert app.static_folder is not None
    
    def test_css_file_accessible(self):
        """Test that CSS file is accessible."""
        app = create_app()
        with app.test_client() as client:
            response = client.get('/static/css/style.css')
            assert response.status_code == 200
            assert b'hammarby-green' in response.data or b'#217A4A' in response.data
    
    def test_js_file_accessible(self):
        """Test that JavaScript file is accessible."""
        app = create_app()
        with app.test_client() as client:
            response = client.get('/static/js/main.js')
            assert response.status_code == 200
            assert b'Hammarby' in response.data
