# Django Admin Log Viewer

A Django app that provides a web interface to view log files directly in the Django admin panel.

## Features

- View multiple log files in the Django admin
- Configurable through Django settings
- Pagination support for large log files
- Filter by log levels (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- Real-time log refresh
- Custom styling and layout
- Responsive design

## Installation

1. Install the package:
```bash
pip install django-admin-log-viewer
```

2. Add `log_viewer` to your `INSTALLED_APPS` in `settings.py`:
```python
INSTALLED_APPS = [
    # ... other apps
    'log_viewer',
]
```

3. Add the log viewer configuration to your `settings.py`:
```python
import os

# Log viewer settings
LOG_VIEWER_FILES = ['django.log']
LOG_VIEWER_FILES_DIR = '/path/to/your/logs/'  # Use absolute path
LOG_VIEWER_PAGE_LENGTH = 25       # total log lines per-page
LOG_VIEWER_MAX_READ_LINES = 1000  # total log lines will be read
LOG_VIEWER_FILE_LIST_MAX_ITEMS_PER_PAGE = 25 # Max log files loaded in Datatable per page
LOG_VIEWER_EXCLUDE_TEXT_PATTERN = None  # String regex expression to exclude the log from line
LOG_VIEWER_FILE_LIST_TITLE = "Log Viewer"
LOGVIEWER_REFRESH_INTERVAL = 1000
LOGVIEWER_INITIAL_NUMBER_OF_CHARS = 2048

# Construct proper log file paths
LOGVIEWER_LOGS = [os.path.join(LOG_VIEWER_FILES_DIR, file) for file in LOG_VIEWER_FILES]
```

4. Include the log viewer URLs in your main `urls.py`:
```python
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    # The log viewer will be accessible through the admin panel
]
```

## Usage

After installation and configuration, you can access the log viewer through the Django admin panel. Look for "Log Files" in the admin interface.

## Configuration Options

- `LOG_VIEWER_FILES`: List of log file names to display
- `LOG_VIEWER_FILES_DIR`: Directory containing the log files
- `LOG_VIEWER_PAGE_LENGTH`: Number of log lines to display per page
- `LOG_VIEWER_MAX_READ_LINES`: Maximum number of lines to read from each file
- `LOG_VIEWER_FILE_LIST_MAX_ITEMS_PER_PAGE`: Maximum files per page in file list
- `LOG_VIEWER_EXCLUDE_TEXT_PATTERN`: Regex pattern to exclude certain log lines
- `LOG_VIEWER_FILE_LIST_TITLE`: Title for the log viewer page
- `LOGVIEWER_REFRESH_INTERVAL`: Auto-refresh interval in milliseconds
- `LOGVIEWER_INITIAL_NUMBER_OF_CHARS`: Initial number of characters to load

## Requirements

- Python 3.8+
- Django 3.2+

## License

MIT License
