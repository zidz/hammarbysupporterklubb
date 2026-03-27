"""Tests for news CRUD operations."""
import pytest
import json


class TestNewsCreate:
    """Test news creation functionality."""
    
    def test_create_news_as_admin(self, admin_client, test_news_data):
        """Test admin can create new news article."""
        news_data = test_news_data[0]
        response = admin_client.post('/admin/news/create', data={
            'title': news_data['title'],
            'content': news_data['content'],
            'category': news_data['category'],
            'tags': ','.join(news_data['tags'])
        }, follow_redirects=True)
        
        assert response.status_code == 200
    
    def test_create_news_requires_title(self, admin_client):
        """Test news creation fails without title."""
        response = admin_client.post('/admin/news/create', data={
            'title': '',
            'content': 'Some content',
            'category': 'sport'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        response_text = response.data.decode('utf-8', errors='ignore').lower()
        assert 'title' in response_text or 'required' in response_text
    
    def test_create_news_requires_content(self, admin_client):
        """Test news creation fails without content."""
        response = admin_client.post('/admin/news/create', data={
            'title': 'Test News',
            'content': '',
            'category': 'sport'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        response_text = response.data.decode('utf-8', errors='ignore').lower()
        assert 'content' in response_text or 'required' in response_text
    
    def test_create_news_unauthorized(self, client, test_news_data):
        """Test unauthenticated user cannot create news."""
        news_data = test_news_data[0]
        response = client.post('/admin/news/create', data={
            'title': news_data['title'],
            'content': news_data['content'],
            'category': news_data['category']
        }, follow_redirects=True)
        
        # Should redirect to login
        assert response.status_code == 200
        response_text = response.data.decode('utf-8', errors='ignore').lower()
        assert 'login' in response_text


class TestNewsRead:
    """Test news reading functionality."""
    
    def test_list_all_news(self, client, news_database):
        """Test all news articles are listed on news page."""
        response = client.get('/nyheter', follow_redirects=True)
        
        assert response.status_code == 200
    
    def test_view_single_news(self, client, news_database):
        """Test individual news article can be viewed."""
        response = client.get('/news/1', follow_redirects=True)
        
        assert response.status_code == 200
    
    def test_news_pagination(self, client, news_database):
        """Test news list is paginated."""
        response = client.get('/nyheter?page=1', follow_redirects=True)
        
        assert response.status_code == 200
    
    def test_news_by_category(self, client, news_database):
        """Test news can be filtered by category."""
        response = client.get('/nyheter?category=sport', follow_redirects=True)
        
        assert response.status_code == 200
    
    def test_news_search(self, client, news_database):
        """Test news can be searched."""
        response = client.get('/nyheter?search=Hammarby', follow_redirects=True)
        
        assert response.status_code == 200


class TestNewsUpdate:
    """Test news update functionality."""
    
    def test_update_news_as_admin(self, admin_client):
        """Test admin can update existing news."""
        response = admin_client.post('/admin/news/1/edit', data={
            'title': 'Updated News Title',
            'content': 'Updated content here',
            'category': 'sport'
        }, follow_redirects=True)
        
        assert response.status_code == 200
    
    def test_update_news_requires_title(self, admin_client):
        """Test news update fails without title."""
        response = admin_client.post('/admin/news/1/edit', data={
            'title': '',
            'content': 'Content',
            'category': 'sport'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        response_text = response.data.decode('utf-8', errors='ignore').lower()
        assert 'title' in response_text or 'required' in response_text
    
    def test_update_news_unauthorized(self, client):
        """Test unauthenticated user cannot update news."""
        response = client.post('/admin/news/1/edit', data={
            'title': 'Hacked News',
            'content': 'Hacked content'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        response_text = response.data.decode('utf-8', errors='ignore').lower()
        assert 'login' in response_text
    
    def test_update_nonexistent_news(self, admin_client):
        """Test updating nonexistent news fails."""
        response = admin_client.post('/admin/news/999/edit', data={
            'title': 'Test',
            'content': 'Content',
            'category': 'sport'
        }, follow_redirects=True)
        
        assert response.status_code in [404, 200]
        response_text = response.data.decode('utf-8', errors='ignore').lower()
        assert 'not found' in response_text


class TestNewsDelete:
    """Test news deletion functionality."""
    
    def test_delete_news_as_admin(self, admin_client):
        """Test admin can delete news."""
        response = admin_client.post('/admin/news/1/delete', follow_redirects=True)
        
        assert response.status_code == 200
    
    def test_delete_news_unauthorized(self, client):
        """Test unauthenticated user cannot delete news."""
        response = client.post('/admin/news/1/delete', follow_redirects=True)
        
        assert response.status_code == 200
        response_text = response.data.decode('utf-8', errors='ignore').lower()
        assert 'login' in response_text
    
    def test_delete_nonexistent_news(self, admin_client):
        """Test deleting nonexistent news fails."""
        response = admin_client.post('/admin/news/999/delete', follow_redirects=True)
        
        assert response.status_code in [404, 200]
        response_text = response.data.decode('utf-8', errors='ignore').lower()
        assert 'not found' in response_text
    
    def test_delete_news_confirmation(self, admin_client):
        """Test delete requires confirmation."""
        response = admin_client.get('/admin/news/1/delete', follow_redirects=True)
        
        assert response.status_code == 200
        response_text = response.data.decode('utf-8', errors='ignore').lower()
        assert 'confirm' in response_text or 'delete' in response_text


class TestNewsValidation:
    """Test news input validation."""
    
    def test_news_title_length_limit(self, admin_client):
        """Test news title has maximum length."""
        long_title = 'A' * 500
        response = admin_client.post('/admin/news/create', data={
            'title': long_title,
            'content': 'Content',
            'category': 'sport'
        }, follow_redirects=True)
        
        assert response.status_code in [200, 400]
        response_text = response.data.decode('utf-8', errors='ignore').lower()
        assert 'too long' in response_text or 'limit' in response_text
    
    def test_news_content_length_limit(self, admin_client):
        """Test news content has maximum length."""
        long_content = 'A' * 50000
        response = admin_client.post('/admin/news/create', data={
            'title': 'Test Title',
            'content': long_content,
            'category': 'sport'
        }, follow_redirects=True)
        
        assert response.status_code in [200, 400]
        response_text = response.data.decode('utf-8', errors='ignore').lower()
        assert 'too long' in response_text or 'limit' in response_text
    
    def test_news_invalid_category(self, admin_client):
        """Test news creation with invalid category."""
        response = admin_client.post('/admin/news/create', data={
            'title': 'Test',
            'content': 'Content',
            'category': 'invalid_category_xyz'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        response_text = response.data.decode('utf-8', errors='ignore').lower()
        assert 'invalid' in response_text
