import pytest
import json
import os
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

# Test constants
TEST_URL = "https://www.hammarbysupporterklubb.se/nyheter/?ID=381455&NID=1332083"
TEST_UPLOADS_DIR = "/a0/usr/projects/Development/hammarby_website/backend/uploads/news"
TEST_DATA_DIR = "/a0/usr/projects/Development/hammarby_website/backend/data/news"


class TestNewsScraper:
    """Test suite for news scraper functionality"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test environment"""
        os.makedirs(TEST_UPLOADS_DIR, exist_ok=True)
        os.makedirs(TEST_DATA_DIR, exist_ok=True)
        yield
        
    def test_quill_delta_conversion(self):
        """Test conversion of article content to Quill Delta format"""
        from backend.utils.news_scraper import convert_to_quill_delta
        
        # Test basic text
        content = "Hello World"
        delta = convert_to_quill_delta(content)
        assert "ops" in delta
        assert len(delta["ops"]) > 0
        
    def test_image_url_extraction(self):
        """Test extraction of image URLs from HTML content"""
        from backend.utils.news_scraper import extract_image_urls
        
        html = '<div><img src="test.jpg"><p>Content</p><img src="test2.png"></div>'
        urls = extract_image_urls(html)
        assert len(urls) == 2
        assert "test.jpg" in urls
        assert "test2.png" in urls
        
    def test_date_parsing(self):
        """Test date parsing from various formats"""
        from backend.utils.news_scraper import parse_date
        
        # Test different date formats
        date1 = parse_date("2026-03-26")
        assert date1 is not None
        
    def test_filename_generation(self):
        """Test news article filename generation"""
        from backend.utils.news_scraper import generate_filename
        
        title = "Test News Article"
        date = datetime(2026, 3, 26, 10, 30, 0)
        filename = generate_filename(title, date)
        
        assert filename.startswith("nyhet_")
        assert filename.endswith(".json")
        
    def test_metadata_creation(self):
        """Test metadata file creation"""
        from backend.utils.news_scraper import create_metadata
        
        articles = [
            {"title": "Article 1", "date": "2026-03-26", "filename": "file1.json"},
            {"title": "Article 2", "date": "2026-03-25", "filename": "file2.json"}
        ]
        
        metadata = create_metadata(articles)
        assert "articles" in metadata
        assert len(metadata["articles"]) == 2
        assert "scraped_at" in metadata


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
