import os
import tempfile
from django.test import TestCase, RequestFactory, override_settings
from django.contrib.auth.models import User
from .utils import get_log_files, read_log_file, format_log_line, parse_log_level
from .views import log_list_view, log_detail_view


class LogViewerUtilsTestCase(TestCase):
    """Test cases for log viewer utility functions."""
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.test_log_content = """WARNING 2025-08-11 11:32:25,079 jazzmin.utils: Could not reverse url from auth.user
INFO 2025-08-11 11:32:26,080 django.server: "GET /admin/ HTTP/1.1" 200 1234
ERROR 2025-08-11 11:32:27,081 django.request: Internal Server Error
DEBUG 2025-08-11 11:32:28,082 myapp.views: Debug message
CRITICAL 2025-08-11 11:32:29,083 myapp.critical: Critical error occurred"""
        
        self.test_log_file = os.path.join(self.temp_dir, 'test.log')
        with open(self.test_log_file, 'w') as f:
            f.write(self.test_log_content)
    
    def tearDown(self):
        if os.path.exists(self.test_log_file):
            os.unlink(self.test_log_file)
        os.rmdir(self.temp_dir)
    
    def test_parse_log_level(self):
        """Test log level parsing."""
        test_cases = [
            ("WARNING 2025-08-11 11:32:25,079 test", "WARNING"),
            ("INFO message here", "INFO"),
            ("ERROR something went wrong", "ERROR"),
            ("DEBUG debug message", "DEBUG"),
            ("CRITICAL critical error", "CRITICAL"),
            ("No level in this line", "INFO"),  # Default
        ]
        
        for line, expected in test_cases:
            with self.subTest(line=line):
                result = parse_log_level(line)
                self.assertEqual(result, expected)
    
    def test_format_log_line(self):
        """Test log line formatting."""
        line = "WARNING 2025-08-11 11:32:25,079 jazzmin.utils: Could not reverse url"
        formatted = format_log_line(line, 1)
        
        self.assertEqual(formatted['number'], 1)
        self.assertEqual(formatted['level'], 'WARNING')
        self.assertEqual(formatted['timestamp'], '2025-08-11 11:32:25')
        self.assertIn('Could not reverse url', formatted['content'])
    
    @override_settings(
        LOG_VIEWER_FILES=['test.log'],
        LOG_VIEWER_FILES_DIR=None  # Will be set in test
    )
    def test_get_log_files(self):
        """Test getting log files list."""
        # Temporarily set the log directory
        with self.settings(LOG_VIEWER_FILES_DIR=self.temp_dir):
            log_files = get_log_files()
            
            self.assertEqual(len(log_files), 1)
            self.assertEqual(log_files[0]['name'], 'test.log')
            self.assertEqual(log_files[0]['path'], self.test_log_file)
            self.assertTrue(log_files[0]['size'] > 0)
    
    def test_read_log_file(self):
        """Test reading log file content."""
        result = read_log_file(self.test_log_file, max_lines=3, start_line=0)
        
        self.assertEqual(len(result['lines']), 3)
        self.assertEqual(result['total_lines'], 5)  # Total lines in test content
        self.assertEqual(result['start_line'], 0)
        self.assertEqual(result['end_line'], 3)
    
    def test_read_log_file_pagination(self):
        """Test log file pagination."""
        # Read second page (lines 2-3)
        result = read_log_file(self.test_log_file, max_lines=2, start_line=2)
        
        self.assertEqual(len(result['lines']), 2)
        self.assertEqual(result['start_line'], 2)
        self.assertEqual(result['end_line'], 4)


class LogViewerViewsTestCase(TestCase):
    """Test cases for log viewer views."""
    
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_superuser(
            username='admin', 
            email='admin@test.com', 
            password='password'
        )
        
        # Create test log file
        self.temp_dir = tempfile.mkdtemp()
        self.test_log_content = "INFO 2025-08-11 11:32:25,079 test: Test message"
        self.test_log_file = os.path.join(self.temp_dir, 'test.log')
        with open(self.test_log_file, 'w') as f:
            f.write(self.test_log_content)
    
    def tearDown(self):
        if os.path.exists(self.test_log_file):
            os.unlink(self.test_log_file)
        os.rmdir(self.temp_dir)
    
    @override_settings(
        LOG_VIEWER_FILES=['test.log'],
        LOG_VIEWER_FILES_DIR=None  # Will be set in test
    )
    def test_log_list_view(self):
        """Test log list view."""
        request = self.factory.get('/admin/logs/')
        request.user = self.user
        
        with self.settings(LOG_VIEWER_FILES_DIR=self.temp_dir):
            response = log_list_view(request)
            
            self.assertEqual(response.status_code, 200)
            self.assertContains(response, 'test.log')
    
    @override_settings(
        LOG_VIEWER_FILES=['test.log'],
        LOG_VIEWER_FILES_DIR=None  # Will be set in test
    )
    def test_log_detail_view(self):
        """Test log detail view."""
        request = self.factory.get('/admin/logs/test.log/')
        request.user = self.user
        
        with self.settings(LOG_VIEWER_FILES_DIR=self.temp_dir):
            response = log_detail_view(request, 'test.log')
            
            self.assertEqual(response.status_code, 200)
            self.assertContains(response, 'Test message')
