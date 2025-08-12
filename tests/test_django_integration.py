"""
Django tests for log_viewer app.
These tests use Django's TestCase for proper Django testing.
"""

import os
import tempfile
from django.test import TestCase, RequestFactory, override_settings
from django.contrib.auth.models import User
from pathlib import Path

from log_viewer.utils import (
    get_log_files, 
    read_log_file, 
    format_log_line, 
    process_log_lines_with_multiline,
    parse_log_line_with_format,
    get_log_format_for_file
)


class LogViewerUtilsTestCase(TestCase):
    """Test cases for log viewer utility functions."""
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.test_log_content = """WARNING 2025-08-11 11:32:25,079 jazzmin.utils: Could not reverse url from auth.user
INFO 2025-08-11 11:32:26,080 django.server: "GET /admin/ HTTP/1.1" 200 1234
ERROR 2025-08-11 11:32:27,081 django.request: Internal Server Error
DEBUG 2025-08-11 11:32:28,082 myapp.views: Debug message
CRITICAL 2025-08-11 11:32:29,083 myapp.critical: Critical error occurred
INFO 2025-08-11 11:32:30,084 celery.beat: Starting scheduler
CRITICAL 2025-08-11 11:32:31,085 celery.beat: Exception occurred
Traceback (most recent call last):
  File "/path/to/file.py", line 123, in function_name
    some_function_call()
  File "/path/to/other.py", line 456, in other_function
    raise Exception("Something went wrong")
Exception: Something went wrong
INFO 2025-08-11 11:32:32,086 celery.beat: Scheduler recovered"""
        
        self.test_log_file = os.path.join(self.temp_dir, 'test.log')
        with open(self.test_log_file, 'w') as f:
            f.write(self.test_log_content)
    
    def tearDown(self):
        if os.path.exists(self.test_log_file):
            os.unlink(self.test_log_file)
        os.rmdir(self.temp_dir)
    
    def test_format_log_line(self):
        """Test log line formatting."""
        test_line = "INFO 2025-08-11 11:32:26,080 django.server: GET /admin/ HTTP/1.1"
        formatted = format_log_line(test_line, 1, 'django.log')
        
        self.assertEqual(formatted['level'], 'INFO')
        self.assertEqual(formatted['module'], 'django.server')
        self.assertIn('GET /admin/', formatted['content'])
        self.assertEqual(formatted['number'], 1)
        self.assertFalse(formatted['is_multiline'])
    
    def test_parse_log_line_with_format(self):
        """Test log line parsing with format configuration."""
        format_config = {
            'pattern': r'(?P<level>\w+)\s+(?P<timestamp>\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2},\d+)\s+(?P<module>[\w\.]+):\s*(?P<message>.*)',
            'timestamp_format': '%Y-%m-%d %H:%M:%S,%f',
            'description': 'Django format'
        }
        
        test_line = "ERROR 2025-08-11 11:32:27,081 django.request: Internal Server Error"
        parsed = parse_log_line_with_format(test_line, format_config)
        
        self.assertIsNotNone(parsed)
        self.assertEqual(parsed['level'], 'ERROR')
        self.assertEqual(parsed['module'], 'django.request')
        self.assertEqual(parsed['message'], 'Internal Server Error')
        self.assertIsNotNone(parsed['parsed_timestamp'])
    
    def test_process_multiline_logs(self):
        """Test multi-line log processing."""
        lines = self.test_log_content.strip().split('\n')
        processed = process_log_lines_with_multiline(lines, 1, 'test.log')
        
        # Should group the multi-line exception into a single entry
        multiline_entries = [entry for entry in processed if entry.get('is_multiline')]
        self.assertGreater(len(multiline_entries), 0)
        
        # Find the exception entry
        exception_entry = None
        for entry in processed:
            if 'Traceback' in entry.get('full_content', ''):
                exception_entry = entry
                break
        
        self.assertIsNotNone(exception_entry)
        self.assertTrue(exception_entry['is_multiline'])
        self.assertGreater(exception_entry['line_count'], 1)
        self.assertIn('-', exception_entry['line_range'])  # Should be a range like "7-12"
    
    @override_settings(
        LOG_VIEWER_FILES=['test.log'],
        LOG_VIEWER_FILES_DIR=None  # Will be set dynamically
    )
    def test_read_log_file(self):
        """Test log file reading functionality."""
        # Update settings with our temp directory
        with self.settings(LOG_VIEWER_FILES_DIR=self.temp_dir):
            log_data = read_log_file(self.test_log_file, 5, 0)
            
            self.assertIn('lines', log_data)
            self.assertIn('total_lines', log_data)
            self.assertGreater(log_data['total_lines'], 0)
            self.assertLessEqual(len(log_data['lines']), 5)  # Should respect pagination
    
    @override_settings(
        LOG_VIEWER_FORMATS={
            'test_format': {
                'pattern': r'(?P<level>\w+)\s+(?P<timestamp>\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2},\d+)\s+(?P<module>[\w\.]+):\s*(?P<message>.*)',
                'timestamp_format': '%Y-%m-%d %H:%M:%S,%f',
                'description': 'Test format'
            }
        },
        LOG_VIEWER_FILE_FORMATS={
            'test.log': 'test_format'
        }
    )
    def test_get_log_format_for_file(self):
        """Test log format configuration retrieval."""
        format_config = get_log_format_for_file('test.log')
        
        self.assertEqual(format_config['description'], 'Test format')
        self.assertIn('pattern', format_config)
        self.assertIn('timestamp_format', format_config)


class LogViewerViewsTestCase(TestCase):
    """Test cases for log viewer views."""
    
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_superuser(
            username='testuser',
            email='test@example.com',
            password='testpass'
        )
        
        self.temp_dir = tempfile.mkdtemp()
        self.test_log_file = os.path.join(self.temp_dir, 'django.log')
        with open(self.test_log_file, 'w') as f:
            f.write("INFO 2025-08-11 11:32:26,080 django.server: Test log entry\n")
    
    def tearDown(self):
        if os.path.exists(self.test_log_file):
            os.unlink(self.test_log_file)
        os.rmdir(self.temp_dir)
    
    @override_settings(
        LOG_VIEWER_FILES=['django.log'],
        LOG_VIEWER_FILES_DIR=None  # Will be set dynamically
    )
    def test_log_views_require_staff(self):
        """Test that log views require staff permissions."""
        with self.settings(LOG_VIEWER_FILES_DIR=self.temp_dir):
            from log_viewer.views import log_list_view, log_detail_view
            
            # Test with non-staff user
            regular_user = User.objects.create_user('regular', 'regular@test.com', 'pass')
            request = self.factory.get('/admin/log_viewer/')
            request.user = regular_user
            
            # Views should handle non-staff users appropriately
            # (The actual behavior depends on your implementation)
            response = log_list_view(request)
            # Add appropriate assertions based on your view behavior


class LogRotationTestCase(TestCase):
    """Test cases for log rotation functionality."""
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        
        # Create main log file
        self.main_log = os.path.join(self.temp_dir, 'app.log')
        with open(self.main_log, 'w') as f:
            f.write("INFO 2025-08-11 12:00:00,000 app: Current log\n")
        
        # Create rotated files
        self.rotated_1 = os.path.join(self.temp_dir, 'app.log.1')
        with open(self.rotated_1, 'w') as f:
            f.write("INFO 2025-08-10 12:00:00,000 app: Yesterday log\n")
        
        self.rotated_2 = os.path.join(self.temp_dir, 'app.log.2')
        with open(self.rotated_2, 'w') as f:
            f.write("INFO 2025-08-09 12:00:00,000 app: Day before log\n")
    
    def tearDown(self):
        for file_path in [self.main_log, self.rotated_1, self.rotated_2]:
            if os.path.exists(file_path):
                os.unlink(file_path)
        os.rmdir(self.temp_dir)
    
    @override_settings(
        LOG_VIEWER_FILES=['app.log'],
        LOG_VIEWER_FILES_DIR=None  # Will be set dynamically
    )
    def test_rotational_file_detection(self):
        """Test that rotational files are detected properly."""
        with self.settings(LOG_VIEWER_FILES_DIR=self.temp_dir):
            log_files = get_log_files()
            
            # Should find the rotational group
            self.assertEqual(len(log_files), 1)
            log_group = log_files[0]
            
            self.assertEqual(log_group['type'], 'rotational_group')
            self.assertEqual(log_group['name'], 'app.log')
            self.assertGreaterEqual(len(log_group['rotational_files']), 3)  # main + 2 rotated
