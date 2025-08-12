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
