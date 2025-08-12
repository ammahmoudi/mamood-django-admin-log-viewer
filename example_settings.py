# Complete Django settings example for django-admin-log-viewer
# This file demonstrates all available configuration options

from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# =============================================================================
# BASIC DJANGO SETTINGS (required)
# =============================================================================

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'log_viewer',  # Add the log viewer app
]

# ... your other Django settings (SECRET_KEY, DATABASES, etc.) ...

# =============================================================================
# LOG VIEWER BASIC CONFIGURATION (required)
# =============================================================================

# Create logs directory
LOG_DIR = BASE_DIR / 'logs'
LOG_DIR.mkdir(exist_ok=True)

# List of log files to monitor
LOG_VIEWER_FILES = [
    'django.log', 
    'application.log',
    'celery_beat.log',
    'celery_worker.log',
    'nginx_access.log',
    'nginx_error.log'
]

# Directory containing log files
LOG_VIEWER_FILES_DIR = LOG_DIR

# Display settings
LOG_VIEWER_PAGE_LENGTH = 25                    # Log entries per page
LOG_VIEWER_MAX_READ_LINES = 1000              # Max lines to read per request
LOG_VIEWER_FILE_LIST_MAX_ITEMS_PER_PAGE = 25  # Files per page in file list
LOG_VIEWER_FILE_LIST_TITLE = "Application Log Viewer"

# =============================================================================
# REAL-TIME MONITORING SETTINGS
# =============================================================================

# Auto-refresh settings
LOGVIEWER_REFRESH_INTERVAL = 5000             # Auto-refresh interval (ms)
LOGVIEWER_AUTO_REFRESH_DEFAULT = True         # Enable auto-refresh by default
LOGVIEWER_AUTO_SCROLL_TO_BOTTOM = True        # Auto-scroll to latest logs
LOGVIEWER_ONLY_REFRESH_WHEN_ACTIVE = True     # Only refresh when tab is active

# Performance settings
LOGVIEWER_INITIAL_NUMBER_OF_CHARS = 2048      # Initial load size
LOGVIEWER_DISABLE_ACCESS_LOGS = True          # Don't log AJAX requests

# =============================================================================
# ADVANCED LOG FORMAT CONFIGURATION
# =============================================================================

# Define log format patterns
LOG_VIEWER_FORMATS = {
    # Django standard format
    'django_default': {
        'pattern': r'(?P<level>\w+)\s+(?P<timestamp>\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2},\d+)\s+(?P<module>[\w\.]+):\s*(?P<message>.*)',
        'timestamp_format': '%Y-%m-%d %H:%M:%S,%f',
        'description': 'Django default: LEVEL YYYY-MM-DD HH:MM:SS,mmm module: message'
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
        'pattern': r'(?P<ip>\S+)\s+\S+\s+\S+\s+\[(?P<timestamp>[^\]]+)\]\s+"(?P<method>\S+)\s+(?P<url>\S+)\s+(?P<protocol>[^"]+)"\s+(?P<status>\d+)\s+(?P<size>\d+|-)\s*(?P<message>.*)',
        'timestamp_format': '%d/%b/%Y:%H:%M:%S %z',
        'description': 'Apache Common Log Format'
    },
    
    # Syslog format
    'syslog': {
        'pattern': r'(?P<timestamp>\w{3}\s+\d{1,2}\s+\d{2}:\d{2}:\d{2})\s+(?P<host>\S+)\s+(?P<service>\S+):\s*(?P<message>.*)',
        'timestamp_format': '%b %d %H:%M:%S',
        'description': 'Standard syslog format'
    },
    
    # JSON-style logs
    'json_logs': {
        'pattern': r'(?P<timestamp>\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d+Z?)\s+(?P<level>\w+)\s+\[(?P<logger>[^\]]+)\]\s+(?P<message>.*)',
        'timestamp_format': '%Y-%m-%dT%H:%M:%S.%fZ',
        'description': 'JSON-style log format with ISO timestamp'
    },
    
    # Simple format
    'simple': {
        'pattern': r'(?P<level>\w+):\s*(?P<message>.*)',
        'timestamp_format': None,
        'description': 'Simple format: LEVEL: message'
    },
    
    # Custom application format
    'custom_app': {
        'pattern': r'\[(?P<timestamp>\d{2}/\d{2}/\d{4}\s+\d{2}:\d{2}:\d{2})\]\s+(?P<level>\w+)\s+-\s+(?P<module>\S+)\s+-\s+(?P<message>.*)',
        'timestamp_format': '%m/%d/%Y %H:%M:%S',
        'description': 'Custom: [MM/DD/YYYY HH:MM:SS] LEVEL - module - message'
    }
}

# Default format for unspecified files
LOG_VIEWER_DEFAULT_FORMAT = 'django_default'

# Per-file format assignment
LOG_VIEWER_FILE_FORMATS = {
    'django.log': 'django_default',
    'application.log': 'custom_app',
    'celery_beat.log': 'celery_beat', 
    'celery_worker.log': 'celery_worker',
    'nginx_access.log': 'nginx_access',
    'nginx_error.log': 'nginx_error',
    'access.log': 'apache_common',
    'syslog': 'syslog',
    'app.json.log': 'json_logs',
    'simple.log': 'simple',
}

# =============================================================================
# UI CUSTOMIZATION
# =============================================================================

# Custom log level colors
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

# Optional: Exclude certain log patterns
LOG_VIEWER_EXCLUDE_TEXT_PATTERN = None  # String regex expression to exclude log lines
# Example: LOG_VIEWER_EXCLUDE_TEXT_PATTERN = r'.*health.*check.*'

# =============================================================================
# DJANGO LOGGING CONFIGURATION (optional but recommended)
# =============================================================================

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module}: {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname}: {message}',
            'style': '{',
        },
        'custom': {
            'format': '[{asctime}] {levelname} - {name} - {message}',
            'datefmt': '%m/%d/%Y %H:%M:%S',
            'style': '{',
        },
    },
    'handlers': {
        'django_file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': LOG_DIR / 'django.log',
            'formatter': 'verbose',
        },
        'app_file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler', 
            'filename': LOG_DIR / 'application.log',
            'formatter': 'custom',
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
    },
    'root': {
        'handlers': ['console', 'django_file'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['django_file', 'console'],
            'level': 'INFO',
            'propagate': False,
        },
        'myproject': {  # Replace with your app name
            'handlers': ['app_file', 'console'],
            'level': 'DEBUG',
            'propagate': False,
        },
        # Celery loggers (if using Celery)
        'celery': {
            'handlers': ['app_file', 'console'],
            'level': 'INFO',
            'propagate': False,
        },
        'celery.beat': {
            'handlers': ['app_file'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}

# =============================================================================
# DEPLOYMENT NOTES
# =============================================================================

# For production deployments:
# 1. Ensure log directory is writable by web server
# 2. Consider log rotation to prevent files from growing too large
# 3. Set appropriate LOGVIEWER_REFRESH_INTERVAL for your needs
# 4. Use LOGVIEWER_DISABLE_ACCESS_LOGS = True to prevent log spam
# 5. Adjust LOG_VIEWER_PAGE_LENGTH based on your log file sizes
# 6. Consider setting up proper log rotation with logrotate or similar

# Example logrotate configuration (/etc/logrotate.d/django-logs):
# /path/to/your/logs/*.log {
#     daily
#     missingok
#     rotate 52
#     compress
#     delaycompress
#     notifempty
#     create 644 www-data www-data
# }
