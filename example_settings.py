# Example Django settings for log_viewer app

import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Example settings for log viewer
LOG_DIR = BASE_DIR / 'logs'  # Adjust to your log directory

# Log viewer settings
LOG_VIEWER_FILES = ['django.log', 'application.log']  # Add your log files
LOG_VIEWER_FILES_DIR = LOG_DIR  # Use the absolute LOG_DIR path
LOG_VIEWER_PAGE_LENGTH = 25       # total log lines per-page
LOG_VIEWER_MAX_READ_LINES = 1000  # total log lines will be read
LOG_VIEWER_FILE_LIST_MAX_ITEMS_PER_PAGE = 25 # Max log files loaded per page

# Optional: exclude certain log patterns
LOG_VIEWER_EXCLUDE_TEXT_PATTERN = None  # String regex expression to exclude log lines

# Optional: customize the admin interface
LOG_VIEWER_FILE_LIST_TITLE = "My Application Log Viewer"
# LOG_VIEWER_FILE_LIST_STYLES = "/static/css/my-custom.css"

# Construct proper log file paths
LOGVIEWER_LOGS = [os.path.join(LOG_DIR, file) for file in LOG_VIEWER_FILES]
LOGVIEWER_REFRESH_INTERVAL = 1000  # Auto-refresh interval in milliseconds
LOGVIEWER_INITIAL_NUMBER_OF_CHARS = 2048

# Log format parsing configuration
LOG_VIEWER_FORMATS = {
    'django_default': {
        'pattern': r'(?P<level>\w+)\s+(?P<timestamp>\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2},\d+)\s+(?P<module>[\w\.]+):\s*(?P<message>.*)',
        'timestamp_format': '%Y-%m-%d %H:%M:%S,%f',
        'description': 'Django default format: LEVEL YYYY-MM-DD HH:MM:SS,mmm module: message'
    },
    'apache_common': {
        'pattern': r'(?P<ip>\S+)\s+\S+\s+\S+\s+\[(?P<timestamp>[^\]]+)\]\s+"(?P<method>\S+)\s+(?P<url>\S+)\s+(?P<protocol>[^"]+)"\s+(?P<status>\d+)\s+(?P<size>\d+|-)\s*(?P<message>.*)',
        'timestamp_format': '%d/%b/%Y:%H:%M:%S %z',
        'description': 'Apache Common Log Format'
    },
    'nginx_error': {
        'pattern': r'(?P<timestamp>\d{4}/\d{2}/\d{2}\s+\d{2}:\d{2}:\d{2})\s+\[(?P<level>\w+)\]\s+(?P<pid>\d+)#(?P<tid>\d+):\s*(?P<message>.*)',
        'timestamp_format': '%Y/%m/%d %H:%M:%S',
        'description': 'Nginx error log format'
    },
    'syslog': {
        'pattern': r'(?P<timestamp>\w{3}\s+\d{1,2}\s+\d{2}:\d{2}:\d{2})\s+(?P<host>\S+)\s+(?P<service>\S+):\s*(?P<message>.*)',
        'timestamp_format': '%b %d %H:%M:%S',
        'description': 'Standard syslog format'
    },
    'custom_json': {
        'pattern': r'(?P<timestamp>\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d+Z?)\s+(?P<level>\w+)\s+\[(?P<logger>[^\]]+)\]\s+(?P<message>.*)',
        'timestamp_format': '%Y-%m-%dT%H:%M:%S.%fZ',
        'description': 'JSON-style log format with ISO timestamp'
    },
    'simple': {
        'pattern': r'(?P<level>\w+):\s*(?P<message>.*)',
        'timestamp_format': None,
        'description': 'Simple format: LEVEL: message'
    }
}

# Default log format to use (must be one of the keys in LOG_VIEWER_FORMATS)
LOG_VIEWER_DEFAULT_FORMAT = 'django_default'

# Per-file format overrides (optional)
LOG_VIEWER_FILE_FORMATS = {
    'django.log': 'django_default',
    'access.log': 'apache_common',
    'error.log': 'nginx_error',
    'syslog': 'syslog',
    'application.log': 'custom_json',
}

# Custom log level colors (optional)
LOG_VIEWER_LEVEL_COLORS = {
    'DEBUG': '#6c757d',    # Gray
    'INFO': '#0dcaf0',     # Cyan
    'WARNING': '#ffc107',  # Yellow
    'WARN': '#ffc107',     # Yellow (alias)
    'ERROR': '#dc3545',    # Red
    'CRITICAL': '#6f42c1', # Purple
    'FATAL': '#6f42c1',    # Purple (alias)
}

# Add to INSTALLED_APPS
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'log_viewer',  # Add the log viewer app
]

# Example logging configuration
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module}: {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': LOG_DIR / 'django.log',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['file'],
        'level': 'INFO',
    },
}
