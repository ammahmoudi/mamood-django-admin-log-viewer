"""
Basic tests for mamood_django_admin_log_viewer app.
For comprehensive tests, see the tests/ directory.
"""

from django.test import TestCase
from .utils import format_log_line, parse_log_line_with_format


class BasicLogViewerTestCase(TestCase):
    """Basic test cases for log viewer functionality."""
    
    def test_format_log_line_basic(self):
        """Test basic log line formatting."""
        test_line = "INFO 2025-08-11 11:32:26,080 django.server: Test message"
        formatted = format_log_line(test_line, 1, 'test.log')
        
        self.assertEqual(formatted['level'], 'INFO')
        self.assertEqual(formatted['number'], 1)
        self.assertFalse(formatted['is_multiline'])
        self.assertIn('Test message', formatted['content'])
    
    def test_parse_log_line_with_format_basic(self):
        """Test basic log line parsing."""
        format_config = {
            'pattern': r'(?P<level>\w+)\s+(?P<timestamp>\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2},\d+)\s+(?P<module>[\w\.]+):\s*(?P<message>.*)',
            'timestamp_format': '%Y-%m-%d %H:%M:%S,%f',
            'description': 'Test format'
        }
        
        test_line = "ERROR 2025-08-11 11:32:27,081 django.request: Test error"
        parsed = parse_log_line_with_format(test_line, format_config)
        
        self.assertIsNotNone(parsed)
        self.assertEqual(parsed['level'], 'ERROR')
        self.assertEqual(parsed['module'], 'django.request')
        self.assertEqual(parsed['message'], 'Test error')
