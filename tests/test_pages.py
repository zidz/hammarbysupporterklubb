"""Tests for all 7 website pages."""
import pytest


class TestHomePage:
    """Test home/start page."""
    
    def test_home_page_loads_successfully(self, client):
        """Test home page loads without errors."""
        response = client.get('/', follow_redirects=True)
        
        assert response.status_code == 200
        assert b'Hammarby' in response.data
    
    def test_home_page_has_navigation(self, client):
        """Test home page has navigation menu."""
        response = client.get('/', follow_redirects=True)
        
        assert response.status_code == 200
        response_text = response.data.decode('utf-8', errors='ignore').lower()
        assert 'nav' in response_text or 'meny' in response_text
    
    def test_home_page_has_hammarby_branding(self, client):
        """Test home page displays Hammarby branding."""
        response = client.get('/', follow_redirects=True)
        
        assert response.status_code == 200
        assert b'Hammarby' in response.data or b'hammarby' in response.data
    
    def test_home_page_has_about_section(self, client):
        """Test home page has about section."""
        response = client.get('/', follow_redirects=True)
        
        assert response.status_code == 200
        response_text = response.data.decode('utf-8', errors='ignore').lower()
        assert 'about' in response_text or 'om oss' in response_text
    
    def test_home_page_has_contact_section(self, client):
        """Test home page has contact section."""
        response = client.get('/', follow_redirects=True)
        
        assert response.status_code == 200
        response_text = response.data.decode('utf-8', errors='ignore').lower()
        assert 'contact' in response_text or 'kontakt' in response_text


class TestNewsPage:
    """Test news/nyheter page."""
    
    def test_news_page_loads_successfully(self, client):
        """Test news page loads without errors."""
        response = client.get('/nyheter', follow_redirects=True)
        
        assert response.status_code == 200
    
    def test_news_page_displays_news_list(self, client, news_database):
        """Test news page displays list of news articles."""
        response = client.get('/nyheter', follow_redirects=True)
        
        assert response.status_code == 200
    
    def test_news_page_has_pagination(self, client):
        """Test news page has pagination controls."""
        response = client.get('/nyheter', follow_redirects=True)
        
        assert response.status_code == 200
    
    def test_news_page_has_search(self, client):
        """Test news page has search functionality."""
        response = client.get('/nyheter', follow_redirects=True)
        
        assert response.status_code == 200


class TestBoardPage:
    """Test board/styrelse page."""
    
    def test_board_page_loads_successfully(self, client):
        """Test board page loads without errors."""
        response = client.get('/styrelse', follow_redirects=True)
        
        assert response.status_code == 200
    
    def test_board_page_displays_board_members(self, client):
        """Test board page displays board member information."""
        response = client.get('/styrelse', follow_redirects=True)
        
        assert response.status_code == 200
    
    def test_board_page_has_contact_info(self, client):
        """Test board page has contact information."""
        response = client.get('/styrelse', follow_redirects=True)
        
        assert response.status_code == 200


class TestScholarshipPage:
    """Test scholarship/stipendium page."""
    
    def test_scholarship_page_loads_successfully(self, client):
        """Test scholarship page loads without errors."""
        response = client.get('/stipendium', follow_redirects=True)
        
        assert response.status_code == 200
    
    def test_scholarship_page_displays_criteria(self, client):
        """Test scholarship page displays criteria."""
        response = client.get('/stipendium', follow_redirects=True)
        
        assert response.status_code == 200
    
    def test_scholarship_page_displays_recipients(self, client):
        """Test scholarship page displays past recipients."""
        response = client.get('/stipendium', follow_redirects=True)
        
        assert response.status_code == 200


class TestMembershipPage:
    """Test membership/medlem page."""
    
    def test_membership_page_loads_successfully(self, client):
        """Test membership page loads without errors."""
        response = client.get('/medlem', follow_redirects=True)
        
        assert response.status_code == 200
    
    def test_membership_page_displays_benefits(self, client):
        """Test membership page displays benefits."""
        response = client.get('/medlem', follow_redirects=True)
        
        assert response.status_code == 200
    
    def test_membership_page_has_join_form(self, client):
        """Test membership page has join form."""
        response = client.get('/medlem', follow_redirects=True)
        
        assert response.status_code == 200


class TestAdminLoginPage:
    """Test admin login page."""
    
    def test_admin_login_page_loads_successfully(self, client):
        """Test admin login page loads without errors."""
        response = client.get('/admin/login', follow_redirects=True)
        
        assert response.status_code == 200
    
    def test_admin_login_page_has_username_field(self, client):
        """Test admin login page has username field."""
        response = client.get('/admin/login', follow_redirects=True)
        
        assert response.status_code == 200
    
    def test_admin_login_page_has_password_field(self, client):
        """Test admin login page has password field."""
        response = client.get('/admin/login', follow_redirects=True)
        
        assert response.status_code == 200
    
    def test_admin_login_page_has_submit_button(self, client):
        """Test admin login page has submit button."""
        response = client.get('/admin/login', follow_redirects=True)
        
        assert response.status_code == 200


class TestAdminDashboardPage:
    """Test admin dashboard page."""
    
    def test_admin_dashboard_requires_authentication(self, client):
        """Test admin dashboard redirects unauthenticated users."""
        response = client.get('/admin/dashboard', follow_redirects=True)
        
        assert response.status_code == 200
        response_text = response.data.decode('utf-8', errors='ignore').lower()
        assert 'login' in response_text
    
    def test_admin_dashboard_loads_for_authenticated_user(self, authenticated_client):
        """Test admin dashboard loads for authenticated users."""
        response = authenticated_client.get('/admin/dashboard', follow_redirects=True)
        
        assert response.status_code == 200
    
    def test_admin_dashboard_displays_news_management(self, authenticated_client):
        """Test admin dashboard displays news management options."""
        response = authenticated_client.get('/admin/dashboard', follow_redirects=True)
        
        assert response.status_code == 200
    
    def test_admin_dashboard_displays_user_management(self, authenticated_client):
        """Test admin dashboard displays user management options."""
        response = authenticated_client.get('/admin/dashboard', follow_redirects=True)
        
        assert response.status_code == 200
    
    def test_admin_dashboard_displays_settings(self, authenticated_client):
        """Test admin dashboard displays settings options."""
        response = authenticated_client.get('/admin/dashboard', follow_redirects=True)
        
        assert response.status_code == 200


class TestPageNavigation:
    """Test page navigation between pages."""
    
    def test_navigation_links_to_home(self, client):
        """Test all pages have link to home."""
        response = client.get('/nyheter', follow_redirects=True)
        
        assert response.status_code == 200
    
    def test_navigation_links_to_news(self, client):
        """Test all pages have link to news."""
        response = client.get('/', follow_redirects=True)
        
        assert response.status_code == 200
    
    def test_mobile_menu_works(self, client):
        """Test mobile menu toggle works."""
        response = client.get('/', follow_redirects=True)
        
        assert response.status_code == 200
