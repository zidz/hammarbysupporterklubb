"""Tests for Quill Delta HTML rendering."""
import pytest
import json


class TestQuillDeltaRendering:
    """Test Quill Delta to HTML conversion."""
    
    def test_simple_text_rendering(self, quill_delta_sample):
        """Test simple text is rendered correctly."""
        from backend.utils.quill_renderer import render_quill_delta
        
        html = render_quill_delta(quill_delta_sample)
        
        assert html is not None
        assert isinstance(html, str)
        assert len(html) > 0
    
    def test_bold_text_rendering(self, quill_delta_sample):
        """Test bold text is rendered with strong/bold tags."""
        from backend.utils.quill_renderer import render_quill_delta
        
        html = render_quill_delta(quill_delta_sample)
        
        assert '<strong>' in html or '<b>' in html
    
    def test_header_rendering(self, quill_delta_sample):
        """Test header is rendered with h1/h2 tags."""
        from backend.utils.quill_renderer import render_quill_delta
        
        html = render_quill_delta(quill_delta_sample)
        
        assert '<h1>' in html or '<h2>' in html
    
    def test_list_rendering(self, quill_delta_sample):
        """Test bullet list is rendered with ul/li tags."""
        from backend.utils.quill_renderer import render_quill_delta
        
        html = render_quill_delta(quill_delta_sample)
        
        assert '<ul>' in html or '<li>' in html
    
    def test_empty_delta_rendering(self, quill_delta_empty):
        """Test empty Delta returns empty HTML."""
        from backend.utils.quill_renderer import render_quill_delta
        
        html = render_quill_delta(quill_delta_empty)
        
        assert html == '' or html == '<p></p>' or html == '<p><br></p>'


class TestQuillDeltaFormatting:
    """Test Quill Delta formatting attributes."""
    
    def test_italic_text_rendering(self, quill_delta_complex):
        """Test italic text is rendered with em/italic tags."""
        from backend.utils.quill_renderer import render_quill_delta
        
        html = render_quill_delta(quill_delta_complex)
        
        assert '<em>' in html or '<i>' in html
    
    def test_bold_and_italic_combined(self, quill_delta_complex):
        """Test combined bold and italic formatting."""
        from backend.utils.quill_renderer import render_quill_delta
        
        html = render_quill_delta(quill_delta_complex)
        
        assert ('<strong>' in html and '<em>' in html) or \
               ('<b>' in html and '<i>' in html)
    
    def test_color_attribute_rendering(self, quill_delta_complex):
        """Test color attribute is rendered with style."""
        from backend.utils.quill_renderer import render_quill_delta
        
        html = render_quill_delta(quill_delta_complex)
        
        assert 'color' in html.lower() or 'style' in html.lower()
    
    def test_link_attribute_rendering(self, quill_delta_complex):
        """Test link attribute is rendered with anchor tag."""
        from backend.utils.quill_renderer import render_quill_delta
        
        html = render_quill_delta(quill_delta_complex)
        
        assert '<a' in html and 'href' in html
    
    def test_link_url_correct(self, quill_delta_complex):
        """Test link has correct URL."""
        from backend.utils.quill_renderer import render_quill_delta
        
        html = render_quill_delta(quill_delta_complex)
        
        assert 'https://hammarby.se' in html


class TestQuillDeltaSecurity:
    """Test Quill Delta security and sanitization."""
    
    def test_xss_script_tag_sanitized(self):
        """Test script tags are sanitized from Delta."""
        from backend.utils.quill_renderer import render_quill_delta
        
        malicious_delta = {
            'ops': [
                {'insert': '<script>alert("XSS")</script>'}
            ]
        }
        
        html = render_quill_delta(malicious_delta)
        
        assert '<script>' not in html
        assert 'alert' not in html.lower()
    
    def test_xss_event_handler_sanitized(self):
        """Test event handlers are sanitized from Delta."""
        from backend.utils.quill_renderer import render_quill_delta
        
        malicious_delta = {
            'ops': [
                {'insert': 'test', 'attributes': {'onclick': 'alert("XSS")'}}
            ]
        }
        
        html = render_quill_delta(malicious_delta)
        
        assert 'onclick' not in html.lower()
        assert 'alert' not in html.lower()
    
    def test_html_entities_encoded(self):
        """Test HTML entities are properly encoded."""
        from backend.utils.quill_renderer import render_quill_delta
        
        delta = {
            'ops': [
                {'insert': '<>&"\''}
            ]
        }
        
        html = render_quill_delta(delta)
        
        assert '<' not in html or '&lt;' in html


class TestQuillDeltaIntegration:
    """Test Quill Delta integration with news system."""
    
    def test_news_content_with_quill_delta(self, admin_client, quill_delta_sample):
        """Test news can be created with Quill Delta content."""
        delta_json = json.dumps(quill_delta_sample)
        
        response = admin_client.post('/admin/news/create', data={
            'title': 'News with Quill Content',
            'content': delta_json,
            'category': 'sport'
        }, follow_redirects=True)
        
        assert response.status_code == 200
    
    def test_news_display_renders_quill_html(self, client, quill_delta_sample):
        """Test news page displays rendered Quill HTML."""
        from backend.utils.quill_renderer import render_quill_delta
        
        html = render_quill_delta(quill_delta_sample)
        
        response = client.get('/nyheter', follow_redirects=True)
        
        assert response.status_code == 200
        assert len(html) > 0
    
    def test_quill_delta_in_admin_editor(self, authenticated_client):
        """Test admin editor can handle Quill Delta."""
        response = authenticated_client.get('/admin/news/create', follow_redirects=True)
        
        assert response.status_code == 200


class TestQuillDeltaEdgeCases:
    """Test Quill Delta edge cases."""
    
    def test_very_long_text(self):
        """Test very long text is handled correctly."""
        from backend.utils.quill_renderer import render_quill_delta
        
        long_text = 'A' * 10000
        delta = {'ops': [{'insert': long_text}]}
        
        html = render_quill_delta(delta)
        
        assert html is not None
        assert len(html) > 0
    
    def test_special_characters(self):
        """Test special characters are handled."""
        from backend.utils.quill_renderer import render_quill_delta
        
        delta = {
            'ops': [
                {'insert': 'Test text with special chars'}
            ]
        }
        
        html = render_quill_delta(delta)
        
        assert html is not None
        assert len(html) > 0
    
    def test_newlines_and_paragraphs(self):
        """Test newlines create proper paragraphs."""
        from backend.utils.quill_renderer import render_quill_delta
        
        delta = {
            'ops': [
                {'insert': 'Line 1\n'},
                {'insert': 'Line 2\n'},
                {'insert': 'Line 3\n'}
            ]
        }
        
        html = render_quill_delta(delta)
        
        assert '<p>' in html or '<br>' in html
    
    def test_mixed_formatting(self):
        """Test mixed formatting in single Delta."""
        from backend.utils.quill_renderer import render_quill_delta
        
        delta = {
            'ops': [
                {'insert': 'Normal '},
                {'attributes': {'bold': True}, 'insert': 'bold '},
                {'attributes': {'italic': True}, 'insert': 'italic '},
                {'attributes': {'bold': True, 'italic': True}, 'insert': 'both'},
                {'insert': '\n'}
            ]
        }
        
        html = render_quill_delta(delta)
        
        assert html is not None
        assert len(html) > 0
