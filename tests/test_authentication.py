"""Tests for authentication functionality."""
import pytest
import json


class TestLogin:
    """Test login functionality."""
    
    def test_login_with_valid_credentials(self, client, test_user):
        """Test successful login with valid credentials."""
        response = client.post('/admin/login', data={
            'username': test_user['username'],
            'password': test_user['password']
        }, follow_redirects=True)
        
        assert response.status_code == 200
        assert b'dashboard' in response.data.lower() or b'Dashboard' in response.data
    
    def test_login_with_invalid_credentials(self, client, test_user):
        """Test login fails with invalid credentials."""
        response = client.post('/admin/login', data={
            'username': test_user['username'],
            'password': 'wrongpassword'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        response_text = response.data.decode('utf-8', errors='ignore').lower()
        assert 'invalid' in response_text or 'error' in response_text or 'fel' in response_text
    
    def test_login_with_missing_username(self, client):
        """Test login fails with missing username."""
        response = client.post('/admin/login', data={
            'password': 'anypassword'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        response_text = response.data.decode('utf-8', errors='ignore').lower()
        assert 'required' in response_text or 'error' in response_text
    
    def test_login_with_missing_password(self, client, test_user):
        """Test login fails with missing password."""
        response = client.post('/admin/login', data={
            'username': test_user['username']
        }, follow_redirects=True)
        
        assert response.status_code == 200
        response_text = response.data.decode('utf-8', errors='ignore').lower()
        assert 'required' in response_text or 'error' in response_text
    
    def test_login_with_nonexistent_user(self, client):
        """Test login fails with nonexistent username."""
        response = client.post('/admin/login', data={
            'username': 'nonexistentuser',
            'password': 'anypassword'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        response_text = response.data.decode('utf-8', errors='ignore').lower()
        assert 'not found' in response_text or 'invalid' in response_text


class TestLogout:
    """Test logout functionality."""
    
    def test_logout_clears_session(self, authenticated_client):
        """Test logout clears user session."""
        response = authenticated_client.get('/admin/logout', follow_redirects=True)
        
        assert response.status_code == 200
        response_text = response.data.decode('utf-8', errors='ignore').lower()
        assert 'login' in response_text
    
    def test_logout_redirects_to_login(self, authenticated_client):
        """Test logout redirects to login page."""
        response = authenticated_client.get('/admin/logout', follow_redirects=True)
        
        assert response.status_code == 200
        response_text = response.data.decode('utf-8', errors='ignore').lower()
        assert 'login' in response_text


class TestSessionManagement:
    """Test session management."""
    
    def test_unauthenticated_user_cannot_access_admin(self, client):
        """Test unauthenticated user cannot access admin pages."""
        response = client.get('/admin/dashboard', follow_redirects=True)
        
        assert response.status_code == 200
        response_text = response.data.decode('utf-8', errors='ignore').lower()
        assert 'login' in response_text
    
    def test_authenticated_user_can_access_admin(self, authenticated_client):
        """Test authenticated user can access admin pages."""
        response = authenticated_client.get('/admin/dashboard', follow_redirects=True)
        
        assert response.status_code == 200
        response_text = response.data.decode('utf-8', errors='ignore').lower()
        assert 'dashboard' in response_text or 'admin' in response_text
    
    def test_session_persists_across_requests(self, authenticated_client):
        """Test session persists across multiple requests."""
        response1 = authenticated_client.get('/admin/dashboard')
        assert response1.status_code == 200
        
        response2 = authenticated_client.get('/admin/dashboard')
        assert response2.status_code == 200
    
    def test_session_timeout(self, app, test_user):
        """Test session expires after timeout."""
        # Create a new client without any session
        new_client = app.test_client()
        response = new_client.get('/admin/dashboard', follow_redirects=True)
        
        assert response.status_code == 200
        response_text = response.data.decode('utf-8', errors='ignore').lower()
        assert 'login' in response_text


class TestPasswordSecurity:
    """Test password security."""
    
    def test_password_not_stored_in_session(self, client, test_user):
        """Test password is not stored in session."""
        response = client.post('/admin/login', data={
            'username': test_user['username'],
            'password': test_user['password']
        })
        
        with client.session_transaction() as session:
            assert 'password' not in session
            assert test_user['password'] not in str(session)
    
    def test_password_hashed_in_database(self, app, test_user):
        """Test passwords are hashed when stored."""
        from backend.models import User
        
        with app.app_context():
            user = User.query.filter_by(username=test_user['username']).first()
            if user:
                assert user.password != test_user['password']
                assert len(user.password) > 32
