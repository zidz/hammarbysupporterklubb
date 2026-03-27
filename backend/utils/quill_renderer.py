"""Quill Delta to HTML renderer with XSS sanitization."""
import re
from html import escape


class QuillRenderer:
    """Render Quill Delta JSON to sanitized HTML."""
    
    @staticmethod
    def render(delta):
        """Render Quill Delta to HTML.
        
        Args:
            delta: Quill Delta dict or JSON string
            
        Returns:
            Sanitized HTML string
        """
        if not delta:
            return ''
        
        # Parse if string
        if isinstance(delta, str):
            try:
                import json
                delta = json.loads(delta)
            except (json.JSONDecodeError, TypeError):
                # Sanitize string input
                delta = QuillRenderer._sanitize_text(delta)
                return delta
        
        if not isinstance(delta, dict) or 'ops' not in delta:
            return ''
        
        html_parts = []
        current_line = []
        current_attrs = {}
        
        for op in delta.get('ops', []):
            if 'insert' not in op:
                continue
                
            insert = op['insert']
            attrs = op.get('attributes', {})
            
            # Sanitize insert text - remove dangerous content
            insert = QuillRenderer._sanitize_text(insert)
            
            # Handle newlines
            if insert == '\n':
                if current_line:
                    line_html = QuillRenderer._render_line(''.join(current_line), current_attrs)
                    html_parts.append(line_html)
                    current_line = []
                current_attrs = {}
                continue
            
            # Update attributes
            current_attrs = attrs.copy()
            current_line.append(insert)
        
        # Render remaining content
        if current_line:
            line_html = QuillRenderer._render_line(''.join(current_line), current_attrs)
            html_parts.append(line_html)
        
        return '\n'.join(html_parts)
    
    @staticmethod
    def _sanitize_text(text):
        """Sanitize text to remove XSS vulnerabilities."""
        if not text:
            return ''
        
        # Remove script tags and their content completely
        text = re.sub(r'<script[^>]*>.*?</script>', '', text, flags=re.IGNORECASE | re.DOTALL)
        text = re.sub(r'<script[^>]*/?>', '', text, flags=re.IGNORECASE)
        
        # Remove event handlers
        text = re.sub(r'on\w+\s*=\s*["\'][^"\']*["\']', '', text, flags=re.IGNORECASE)
        text = re.sub(r'on\w+\s*=\s*[^\s>]+', '', text, flags=re.IGNORECASE)
        
        # Remove javascript: URLs
        text = re.sub(r'javascript:', '', text, flags=re.IGNORECASE)
        text = re.sub(r'data:', '', text, flags=re.IGNORECASE)
        text = re.sub(r'vbscript:', '', text, flags=re.IGNORECASE)
        
        # Remove style tags with expressions
        text = re.sub(r'<style[^>]*>.*?</style>', '', text, flags=re.IGNORECASE | re.DOTALL)
        
        # Remove iframe, object, embed, form tags
        text = re.sub(r'<(iframe|object|embed|form)[^>]*>.*?</\1>', '', text, flags=re.IGNORECASE | re.DOTALL)
        text = re.sub(r'<(iframe|object|embed|form)[^>]*/?>', '', text, flags=re.IGNORECASE)
        
        # Escape remaining HTML
        text = escape(text)
        
        return text
    
    @staticmethod
    def _render_line(text, attrs):
        """Render a line of text with attributes."""
        if not text:
            return '<p></p>'
        
        # Apply formatting
        if attrs.get('bold'):
            text = f'<strong>{text}</strong>'
        if attrs.get('italic'):
            text = f'<em>{text}</em>'
        if attrs.get('underline'):
            text = f'<u>{text}</u>'
        
        # Headers
        header = attrs.get('header')
        if header:
            return f'<h{header}>{text}</h{header}>'
        
        # Lists
        if attrs.get('list') == 'bullet':
            return f'<li>{text}</li>'
        if attrs.get('list') == 'ordered':
            return f'<li>{text}</li>'
        
        # Links
        link = attrs.get('link')
        if link:
            link = QuillRenderer._sanitize_url(link)
            return f'<a href="{link}" target="_blank" rel="noopener">{text}</a>'
        
        # Images
        image = attrs.get('image')
        if image:
            image = QuillRenderer._sanitize_url(image)
            return f'<img src="{image}" alt="" class="quill-image">'
        
        # Colors
        color = attrs.get('color')
        if color:
            color = QuillRenderer._sanitize_color(color)
            text = f'<span style="color: {color}">{text}</span>'
        
        # Background
        background = attrs.get('background')
        if background:
            background = QuillRenderer._sanitize_color(background)
            text = f'<span style="background-color: {background}">{text}</span>'
        
        # Alignment
        align = attrs.get('align')
        if align:
            text = f'<span style="text-align: {align}">{text}</span>'
        
        # Default paragraph
        return f'<p>{text}</p>'
    
    @staticmethod
    def _sanitize_url(url):
        """Sanitize URL to prevent XSS."""
        if not url:
            return '#'
        
        # Remove javascript: and data: protocols
        url = re.sub(r'^javascript:', '', url, flags=re.IGNORECASE)
        url = re.sub(r'^data:', '', url, flags=re.IGNORECASE)
        url = re.sub(r'^vbscript:', '', url, flags=re.IGNORECASE)
        
        # Only allow http, https, mailto
        if not re.match(r'^(https?://|mailto:)', url, re.IGNORECASE):
            url = f'https://{url}'
        
        return url[:500]  # Limit length
    
    @staticmethod
    def _sanitize_color(color):
        """Sanitize color value."""
        if not color:
            return '#000000'
        
        # Only allow hex colors
        if re.match(r'^#[0-9a-fA-F]{3,6}$', color):
            return color[:7]
        
        # Allow named colors (limited set)
        safe_colors = ['red', 'green', 'blue', 'yellow', 'orange', 'purple', 'black', 'white']
        if color.lower() in safe_colors:
            return color.lower()
        
        return '#000000'


def render_quill_delta(delta):
    """Convenience function to render Quill Delta.
    
    Args:
        delta: Quill Delta dict or JSON string
        
    Returns:
        Sanitized HTML string
    """
    return QuillRenderer.render(delta)
