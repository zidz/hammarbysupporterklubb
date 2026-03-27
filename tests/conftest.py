"""Shared fixtures for Hammarby Supporterklubb test suite."""
import pytest
import os
import tempfile
import json
from io import BytesIO
from PIL import Image


@pytest.fixture(scope='function')
def app():
    """Create and configure a test application instance."""
    from backend.app import create_app
    
    # Create test app with test configuration
    app = create_app()
    app.config.update({
        'TESTING': True,
        'WTF_CSRF_ENABLED': False,
        'SECRET_KEY': 'test-secret-key-for-testing-only',
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'UPLOAD_FOLDER': tempfile.mkdtemp(),
        'MAX_CONTENT_LENGTH': 100 * 1024 * 1024,
        'PERMANENT_SESSION_LIFETIME': __import__('datetime').timedelta(minutes=1),
    })
    
    yield app


@pytest.fixture(scope='function')
def client(app):
    """Create a test client for the application."""
    return app.test_client()


@pytest.fixture(scope='function')
def runner(app):
    """Create a test CLI runner."""
    return app.test_cli_runner()


@pytest.fixture(scope='function')
def test_user():
    """Create test user data."""
    return {
        'username': 'testuser',
        'email': 'test@hammarby.se',
        'password': 'TestPassword123!',
        'role': 'admin'
    }


@pytest.fixture(scope='function')
def test_user_regular():
    """Create test regular user data."""
    return {
        'username': 'regularuser',
        'email': 'regular@hammarby.se',
        'password': 'RegularPass456!',
        'role': 'member'
    }


@pytest.fixture(scope='function')
def test_news_data():
    """Create test news data."""
    return [
        {
            'title': 'Hammarby vinner SM-guld!',
            'content': 'Efter en fantastisk säsong har Hammarby tagit hem SM-guldet!',
            'author': 'testuser',
            'category': 'sport',
            'tags': ['SM-guld', 'fotboll', 'vinst']
        },
        {
            'title': 'Medlemsmöte 2024',
            'content': 'Årsmöte hålls den 15 mars på Södermalm.',
            'author': 'admin',
            'category': 'medlemmar',
            'tags': ['möte', 'årsmöte']
        },
        {
            'title': 'Nya stipendiater utsedda',
            'content': 'Tre lovande unga fotbollsspelare har fått stipendium.',
            'author': 'admin',
            'category': 'stipendium',
            'tags': ['stipendium', 'ungdom']
        }
    ]


@pytest.fixture(scope='function')
def test_image():
    """Create a test image file."""
    img = Image.new('RGB', (100, 100), color='green')
    img_io = BytesIO()
    img.save(img_io, format='JPEG')
    img_io.seek(0)
    
    return {
        'file': (img_io, 'test_image.jpg'),
        'filename': 'test_image.jpg',
        'content_type': 'image/jpeg'
    }


@pytest.fixture(scope='function')
def test_image_png():
    """Create a test PNG image file."""
    img = Image.new('RGB', (100, 100), color='blue')
    img_io = BytesIO()
    img.save(img_io, format='PNG')
    img_io.seek(0)
    
    return {
        'file': (img_io, 'test_image.png'),
        'filename': 'test_image.png',
        'content_type': 'image/png'
    }


@pytest.fixture(scope='function')
def test_image_invalid():
    """Create an invalid test file (not an image)."""
    invalid_io = BytesIO(b'This is not an image file')
    
    return {
        'file': (invalid_io, 'invalid.txt'),
        'filename': 'invalid.txt',
        'content_type': 'text/plain'
    }


@pytest.fixture(scope='function')
def test_image_too_large():
    """Create a test image that exceeds size limit."""
    img = Image.new('RGB', (5000, 5000), color='red')
    img_io = BytesIO()
    img.save(img_io, format='JPEG')
    img_io.seek(0)
    
    return {
        'file': (img_io, 'large_image.jpg'),
        'filename': 'large_image.jpg',
        'content_type': 'image/jpeg'
    }


@pytest.fixture(scope='function')
def quill_delta_sample():
    """Create sample Quill Delta data."""
    return {
        'ops': [
            {'insert': 'Hammarby '},
            {'attributes': {'bold': True}, 'insert': 'vinner!'},
            {'insert': '\n'},
            {'attributes': {'header': 1}, 'insert': 'Rubrik'},
            {'insert': '\n'},
            {'attributes': {'list': 'bullet'}, 'insert': 'Punkt 1\n'},
            {'attributes': {'list': 'bullet'}, 'insert': 'Punkt 2\n'}
        ]
    }


@pytest.fixture(scope='function')
def quill_delta_empty():
    """Create empty Quill Delta data."""
    return {'ops': []}


@pytest.fixture(scope='function')
def quill_delta_complex():
    """Create complex Quill Delta with nested formatting."""
    return {
        'ops': [
            {'insert': 'Normal text '},
            {'attributes': {'bold': True, 'italic': True}, 'insert': 'bold and italic'},
            {'insert': '\n'},
            {'attributes': {'color': '#ff0000'}, 'insert': 'Red text'},
            {'insert': '\n'},
            {'attributes': {'link': 'https://hammarby.se'}, 'insert': 'Hammarby hemsida'},
            {'insert': '\n'}
        ]
    }


@pytest.fixture(scope='function')
def authenticated_client(client, test_user):
    """Create a client with authenticated session."""
    response = client.post('/admin/login', data={
        'username': test_user['username'],
        'password': test_user['password']
    }, follow_redirects=False)
    
    return client


@pytest.fixture(scope='function')
def admin_client(client, test_user):
    """Create a client with admin authenticated session."""
    response = client.post('/admin/login', data={
        'username': test_user['username'],
        'password': test_user['password']
    }, follow_redirects=False)
    
    return client


@pytest.fixture(scope='function')
def news_database(app, test_news_data):
    """Create in-memory news database."""
    return test_news_data
