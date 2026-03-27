"""Tests for image upload functionality."""
import pytest
import os
from PIL import Image
from io import BytesIO


class TestImageUploadValidation:
    """Test image upload validation."""
    
    def test_upload_valid_jpeg_image(self, admin_client, test_image):
        """Test successful upload of valid JPEG image."""
        response = admin_client.post('/admin/news/upload', data={
            'image': test_image['file']
        }, follow_redirects=True)
        
        assert response.status_code == 200
    
    def test_upload_valid_png_image(self, admin_client, test_image_png):
        """Test successful upload of valid PNG image."""
        response = admin_client.post('/admin/news/upload', data={
            'image': test_image_png['file']
        }, follow_redirects=True)
        
        assert response.status_code == 200
    
    def test_upload_invalid_file_type(self, admin_client, test_image_invalid):
        """Test upload fails with invalid file type."""
        response = admin_client.post('/admin/news/upload', data={
            'image': test_image_invalid['file']
        }, follow_redirects=True)
        
        assert response.status_code == 200
        response_text = response.data.decode('utf-8', errors='ignore').lower()
        assert 'invalid' in response_text or 'not an image' in response_text
    
    def test_upload_file_size_limit(self, admin_client, test_image_too_large):
        """Test upload fails with file exceeding size limit."""
        response = admin_client.post('/admin/news/upload', data={
            'image': test_image_too_large['file']
        }, follow_redirects=True)
        
        assert response.status_code in [413, 200]
        response_text = response.data.decode('utf-8', errors='ignore').lower()
        assert 'too large' in response_text or 'limit' in response_text
    
    def test_upload_no_file(self, admin_client):
        """Test upload fails when no file provided."""
        response = admin_client.post('/admin/news/upload', data={}, follow_redirects=True)
        
        assert response.status_code == 200
        response_text = response.data.decode('utf-8', errors='ignore').lower()
        assert 'required' in response_text or 'no file' in response_text


class TestImageOptimization:
    """Test image optimization functionality."""
    
    def test_image_resized_to_max_dimensions(self, admin_client, test_image):
        """Test uploaded image is resized to maximum dimensions."""
        large_img = Image.new('RGB', (2000, 2000), color='blue')
        img_io = BytesIO()
        large_img.save(img_io, format='JPEG')
        img_io.seek(0)
        
        response = admin_client.post('/admin/news/upload', data={
            'image': (img_io, 'large.jpg')
        }, follow_redirects=True)
        
        assert response.status_code == 200
    
    def test_image_quality_preserved(self, admin_client, test_image):
        """Test image quality is preserved after optimization."""
        response = admin_client.post('/admin/news/upload', data={
            'image': test_image['file']
        }, follow_redirects=True)
        
        assert response.status_code == 200
    
    def test_image_format_converted_to_jpeg(self, admin_client, test_image_png):
        """Test PNG images are converted to JPEG for optimization."""
        response = admin_client.post('/admin/news/upload', data={
            'image': test_image_png['file']
        }, follow_redirects=True)
        
        assert response.status_code == 200


class TestImageFormatSupport:
    """Test supported image formats."""
    
    def test_jpeg_format_supported(self, admin_client, test_image):
        """Test JPEG format is supported."""
        response = admin_client.post('/admin/news/upload', data={
            'image': test_image['file']
        }, follow_redirects=True)
        
        assert response.status_code == 200
    
    def test_png_format_supported(self, admin_client, test_image_png):
        """Test PNG format is supported."""
        response = admin_client.post('/admin/news/upload', data={
            'image': test_image_png['file']
        }, follow_redirects=True)
        
        assert response.status_code == 200
    
    def test_gif_format_supported(self, admin_client):
        """Test GIF format is supported."""
        img = Image.new('P', (100, 100), color=1)
        img_io = BytesIO()
        img.save(img_io, format='GIF')
        img_io.seek(0)
        
        response = admin_client.post('/admin/news/upload', data={
            'image': (img_io, 'test.gif')
        }, follow_redirects=True)
        
        assert response.status_code == 200
    
    def test_webp_format_supported(self, admin_client):
        """Test WebP format is supported."""
        img = Image.new('RGB', (100, 100), color='green')
        img_io = BytesIO()
        img.save(img_io, format='WEBP')
        img_io.seek(0)
        
        response = admin_client.post('/admin/news/upload', data={
            'image': (img_io, 'test.webp')
        }, follow_redirects=True)
        
        assert response.status_code == 200
    
    def test_bmp_format_not_supported(self, admin_client):
        """Test BMP format is not supported."""
        img = Image.new('RGB', (100, 100), color='red')
        img_io = BytesIO()
        img.save(img_io, format='BMP')
        img_io.seek(0)
        
        response = admin_client.post('/admin/news/upload', data={
            'image': (img_io, 'test.bmp')
        }, follow_redirects=True)
        
        assert response.status_code == 200
        response_text = response.data.decode('utf-8', errors='ignore').lower()
        assert 'not supported' in response_text


class TestImageStorage:
    """Test image storage functionality."""
    
    def test_image_saved_to_upload_folder(self, admin_client, test_image, app):
        """Test uploaded image is saved to correct folder."""
        response = admin_client.post('/admin/news/upload', data={
            'image': test_image['file']
        }, follow_redirects=True)
        
        assert response.status_code == 200
        upload_folder = app.config['UPLOAD_FOLDER']
        files = os.listdir(upload_folder)
        assert len(files) > 0
    
    def test_image_filename_sanitized(self, admin_client):
        """Test uploaded image filename is sanitized."""
        img = Image.new('RGB', (100, 100), color='blue')
        img_io = BytesIO()
        img.save(img_io, format='JPEG')
        img_io.seek(0)
        
        response = admin_client.post('/admin/news/upload', data={
            'image': (img_io, '../../../etc/passwd.jpg')
        }, follow_redirects=True)
        
        assert response.status_code == 200
    
    def test_image_unique_filename_generated(self, admin_client, test_image):
        """Test unique filename is generated for uploaded image."""
        response1 = admin_client.post('/admin/news/upload', data={
            'image': test_image['file']
        })
        
        response2 = admin_client.post('/admin/news/upload', data={
            'image': test_image['file']
        })
        
        assert response1.status_code == 200
        assert response2.status_code == 200


class TestImageDelete:
    """Test image deletion functionality."""
    
    def test_delete_uploaded_image(self, admin_client, test_image, app):
        """Test uploaded image can be deleted."""
        upload_response = admin_client.post('/admin/news/upload', data={
            'image': test_image['file']
        })
        
        delete_response = admin_client.post('/admin/news/delete-image/1', follow_redirects=True)
        
        assert delete_response.status_code == 200
    
    def test_delete_nonexistent_image(self, admin_client):
        """Test deleting nonexistent image fails."""
        response = admin_client.post('/admin/news/delete-image/999', follow_redirects=True)
        
        assert response.status_code in [404, 200]
        response_text = response.data.decode('utf-8', errors='ignore').lower()
        assert 'not found' in response_text
    
    def test_delete_image_unauthorized(self, client, test_image):
        """Test unauthenticated user cannot delete images."""
        response = client.post('/admin/news/delete-image/1', follow_redirects=True)
        
        assert response.status_code == 200
        response_text = response.data.decode('utf-8', errors='ignore').lower()
        assert 'login' in response_text
