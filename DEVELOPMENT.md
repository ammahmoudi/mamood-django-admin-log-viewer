# Development Guide

## Development Setup

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install development dependencies:
```bash
pip install -r requirements.txt
```

3. Run tests:
```bash
python -m pytest log_viewer/tests.py
```

## Testing the App

To test the log viewer in a Django project:

1. Create a test Django project:
```bash
django-admin startproject testproject
cd testproject
```

2. Copy the `log_viewer` app into the project

3. Update `settings.py` with the configuration from `example_settings.py`

4. Create some log files in the configured directory

5. Run the development server:
```bash
python manage.py runserver
```

6. Visit `http://localhost:8000/admin/logs/` to view the log files

## Project Structure

```
log_viewer/
├── __init__.py
├── apps.py                 # Django app configuration
├── admin.py                # Admin integration
├── models.py              # No models (file-based)
├── views.py               # Django views
├── urls.py                # URL patterns
├── utils.py               # Utility functions
├── tests.py               # Test cases
├── static/
│   └── log_viewer/
│       ├── css/
│       │   └── log_viewer.css
│       └── js/
│           └── log_viewer.js
└── templates/
    └── log_viewer/
        ├── log_list.html
        └── log_detail.html
```

## Key Features

- **File-based**: No database required
- **Admin integration**: Works with Django admin
- **Pagination**: Handles large log files efficiently
- **Real-time updates**: AJAX-based refresh
- **Filtering**: Filter by log levels
- **Responsive**: Mobile-friendly interface
- **Configurable**: Extensive settings options

## Configuration Options

All settings are optional and have sensible defaults:

- `LOG_VIEWER_FILES`: List of log file names
- `LOG_VIEWER_FILES_DIR`: Directory containing log files
- `LOG_VIEWER_PAGE_LENGTH`: Lines per page
- `LOG_VIEWER_MAX_READ_LINES`: Maximum lines to read
- `LOG_VIEWER_FILE_LIST_MAX_ITEMS_PER_PAGE`: Files per page
- `LOG_VIEWER_EXCLUDE_TEXT_PATTERN`: Regex to exclude lines
- `LOG_VIEWER_FILE_LIST_TITLE`: Custom page title
- `LOGVIEWER_REFRESH_INTERVAL`: Auto-refresh interval
- `LOGVIEWER_INITIAL_NUMBER_OF_CHARS`: Initial character limit
