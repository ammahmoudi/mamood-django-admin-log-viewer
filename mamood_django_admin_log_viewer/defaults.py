"""
Default settings for django-admin-log-viewer.

This module provides sensible default values for all configuration options.
Users can override these in their Django settings.py file.
"""

from pathlib import Path

# =============================================================================
# BASIC CONFIGURATION DEFAULTS
# =============================================================================

# List of log files to monitor (empty by default - user must specify)
LOG_VIEWER_FILES = []

# Directory containing log files (empty by default - user must specify)
LOG_VIEWER_FILES_DIR = ''

# Display settings
LOG_VIEWER_PAGE_LENGTH = 25                    # Log entries per page
LOG_VIEWER_MAX_READ_LINES = 1000              # Max lines to read per request
LOG_VIEWER_FILE_LIST_MAX_ITEMS_PER_PAGE = 25  # Files per page in file list
LOG_VIEWER_FILE_LIST_TITLE = "Log Files"      # Title for file list page

# =============================================================================
# REAL-TIME MONITORING DEFAULTS
# =============================================================================

# Auto-refresh settings
LOGVIEWER_REFRESH_INTERVAL = 10000             # Auto-refresh interval (10 seconds)
LOGVIEWER_AUTO_REFRESH_DEFAULT = True          # Enable auto-refresh by default
LOGVIEWER_AUTO_SCROLL_TO_BOTTOM = True         # Auto-scroll to latest logs
LOGVIEWER_ONLY_REFRESH_WHEN_ACTIVE = True      # Only refresh when tab is active

# Performance settings
LOGVIEWER_INITIAL_NUMBER_OF_CHARS = 2048       # Initial load size
LOGVIEWER_DISABLE_ACCESS_LOGS = True           # Don't log AJAX requests

# =============================================================================
# LOG FORMAT DEFAULTS
# =============================================================================

# Default log format patterns
LOG_VIEWER_FORMATS = {
    # Django standard format (default)
    'django_default': {
        'pattern': r'(?P<level>\w+)\s+(?P<timestamp>\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2},\d+)\s+(?P<module>[\w\.]+):\s*(?P<message>.*)',
        'timestamp_format': '%Y-%m-%d %H:%M:%S,%f',
        'description': 'Django default: LEVEL YYYY-MM-DD HH:MM:SS,mmm module: message'
    },
    
    # Simple format
    'simple': {
        'pattern': r'(?P<level>\w+):\s*(?P<message>.*)',
        'timestamp_format': None,
        'description': 'Simple format: LEVEL: message'
    },
    
    # Celery Beat logs
    'celery_beat': {
        'pattern': r'(?P<level>\w+)\s+(?P<timestamp>\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2},\d+)\s+(?P<module>[\w\.]+):\s*(?P<message>.*)',
        'timestamp_format': '%Y-%m-%d %H:%M:%S,%f',
        'description': 'Celery Beat: INFO YYYY-MM-DD HH:MM:SS,mmm celery.beat: message'
    },
    
    # Celery Worker logs
    'celery_worker': {
        'pattern': r'\[(?P<timestamp>\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2},\d+):\s+(?P<level>\w+)/(?P<worker>\w+)\]\s*(?P<message>.*)',
        'timestamp_format': '%Y-%m-%d %H:%M:%S,%f',
        'description': 'Celery Worker: [YYYY-MM-DD HH:MM:SS,mmm: LEVEL/worker] message'
    },
    
    # Nginx access logs
    'nginx_access': {
        'pattern': r'(?P<ip>\d+\.\d+\.\d+\.\d+)\s+-\s+-\s+\[(?P<timestamp>[^\]]+)\]\s+"(?P<method>\w+)\s+(?P<url>\S+)\s+HTTP/[\d\.]+"\s+(?P<status>\d+)\s+(?P<size>\d+)',
        'timestamp_format': '%d/%b/%Y:%H:%M:%S %z',
        'description': 'Nginx access logs'
    },
    
    # Nginx error logs
    'nginx_error': {
        'pattern': r'(?P<timestamp>\d{4}/\d{2}/\d{2}\s+\d{2}:\d{2}:\d{2})\s+\[(?P<level>\w+)\]\s+(?P<pid>\d+)#(?P<tid>\d+):\s*(?P<message>.*)',
        'timestamp_format': '%Y/%m/%d %H:%M:%S',
        'description': 'Nginx error log format'
    },
    
    # Apache Common Log Format
    'apache_common': {
        'pattern': r'(?P<ip>\S+)\s+\S+\s+\S+\s+\[(?P<timestamp>[^\]]+)\]\s+"(?P<method>\S+)\s+(?P<url>\S+)\s+(?P<protocol>[^"]+)"\s+(?P<status>\d+)\s+(?P<size>\d+|-)',
        'timestamp_format': '%d/%b/%Y:%H:%M:%S %z',
        'description': 'Apache Common Log Format'
    },
    
    # Syslog format
    'syslog': {
        'pattern': r'(?P<timestamp>\w{3}\s+\d{1,2}\s+\d{2}:\d{2}:\d{2})\s+(?P<host>\S+)\s+(?P<service>\S+):\s*(?P<message>.*)',
        'timestamp_format': '%b %d %H:%M:%S',
        'description': 'Standard syslog format'
    },
}

# Default format for unspecified files
LOG_VIEWER_DEFAULT_FORMAT = 'django_default'

# Per-file format assignment (empty by default)
LOG_VIEWER_FILE_FORMATS = {}

# =============================================================================
# UI CUSTOMIZATION DEFAULTS
# =============================================================================

# Default log level colors
LOG_VIEWER_LEVEL_COLORS = {
    'DEBUG': '#6c757d',    # Gray
    'INFO': '#0dcaf0',     # Cyan
    'WARNING': '#ffc107',  # Yellow
    'WARN': '#ffc107',     # Yellow (alias)
    'ERROR': '#dc3545',    # Red
    'CRITICAL': '#6f42c1', # Purple
    'FATAL': '#6f42c1',    # Purple (alias)
    'NOTICE': '#17a2b8',   # Teal
    'ALERT': '#fd7e14',    # Orange
}

# Optional: Exclude certain log patterns (None by default)
LOG_VIEWER_EXCLUDE_TEXT_PATTERN = None
