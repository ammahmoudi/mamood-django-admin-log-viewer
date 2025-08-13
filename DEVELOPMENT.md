# Development Guide

## Development Setup

### Option 1: Editable Install (Recommended for Development)

1. **Clone the repository:**
```bash
git clone <repository-url>
cd django-admin-log-viewer
```

2. **Create a virtual environment:**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install in editable mode:**
```bash
pip install -e .
```

This installs the package in "editable" mode, meaning changes to the source code are immediately reflected without reinstalling.

4. **Install development dependencies:**
```bash
pip install -r myproject/requirements.txt
```

### Option 2: Direct Development Setup

1. **Clone and setup:**
```bash
git clone <repository-url>
cd django-admin-log-viewer
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r myproject/requirements.txt
```

2. **Add to Python path (for testing):**
Add the project root directory to your Python path when testing.

## Running Tests

### Unit Tests
```bash
# Run basic app tests
cd myproject
python manage.py test django_admin_log_viewer

# Run comprehensive test suite
python -m pytest tests/ -v
```

### Integration Tests
```bash
# Run all Django integration tests
cd myproject  
python manage.py test
```

## Testing the App

The project includes a complete test Django project in `myproject/`:

1. **Navigate to test project:**
```bash
cd myproject
```

2. **Run the development server:**
```bash
python manage.py runserver
```

3. **Create a superuser:**
```bash
python manage.py createsuperuser
```

4. **Access the log viewer:**
   - Visit `http://localhost:8000/admin/`
   - Login with superuser credentials
   - Look for **"Log Files"** in the admin interface

## Project Structure

```
django-admin-log-viewer/
├── django_admin_log_viewer/           # Main app (renamed for consistency)
│   ├── __init__.py
│   ├── apps.py                       # Django app configuration
│   ├── admin.py                      # Admin integration with multi-line support
│   ├── models.py                     # No models (file-based)
│   ├── views.py                      # Django views
│   ├── urls.py                       # URL patterns
│   ├── utils.py                      # Core utilities with format parsing
│   ├── tests.py                      # Test cases
│   ├── static/django_admin_log_viewer/
│   │   ├── css/
│   │   │   ├── log_viewer.css        # Main styles
│   │   │   └── live_mode.css         # Real-time mode styles
│   │   └── js/
│   │       └── log_viewer.js         # AJAX and interactivity
│   ├── templates/django_admin_log_viewer/
│   │   ├── log_list.html             # File list with sidebar
│   │   └── log_detail.html           # Log content viewer
│   └── templatetags/
│       └── log_extras.py             # Custom template tags
├── myproject/                         # Test Django project
│   ├── manage.py
│   ├── requirements.txt              # Development dependencies
│   ├── myproject/
│   │   └── settings.py               # Complete example settings
│   └── logs/                         # Sample log files
│       ├── django.log
│       ├── application.log
│       ├── celery_beat.log           # With multi-line stack traces
│       └── *.log.*                   # Rotated log files
├── tests/                            # Test suite
├── README.md                         # Complete documentation
├── CHANGELOG.md                      # Version history
├── example_settings.py               # All configuration options
├── DEVELOPMENT.md                    # This file
└── setup.py                         # Package configuration
```

## Key Features Implemented

### 🔍 **Multi-line Log Processing**
- Detects and groups stack traces, exceptions, and multi-line entries
- Smart pagination that never splits multi-line entries across pages
- Handles very long stack traces (e.g., 86-line Celery Beat errors)

### ⚙️ **Configurable Log Formats** 
- Support for Django, Celery, Nginx, Apache, Syslog formats
- Custom regex patterns for any log format
- Per-file format assignment
- Automatic module/logger name extraction

### 🔄 **Real-time Monitoring**
- Live mode with auto-refresh
- AJAX-based updates without page reload
- Configurable refresh intervals
- Auto-scroll to latest logs

### 🗂️ **Log Rotation Support**
- Automatic detection of rotated files (.1, .2, .gz, etc.)
- Proper sorting by rotation index
- Support for dated and compressed rotations

### 🎨 **Modern UI/UX**
- Responsive design with sidebar navigation
- Dark mode support
- Configurable log level colors  
- Download functionality
- Mobile-friendly interface

### 🚀 **Performance & Security**
- Memory-efficient streaming for large files
- Staff-only access with proper validation
- Configurable file size limits
- AJAX optimization to prevent log spam

## Configuration Categories

### **Basic Settings** (Required)
```python
LOG_VIEWER_FILES = ['django.log', 'application.log']
LOG_VIEWER_FILES_DIR = BASE_DIR / 'logs'
LOG_VIEWER_PAGE_LENGTH = 25
```

### **Real-time Monitoring**
```python
LOGVIEWER_REFRESH_INTERVAL = 5000
LOGVIEWER_AUTO_REFRESH_DEFAULT = True
LOGVIEWER_AUTO_SCROLL_TO_BOTTOM = True
LOGVIEWER_ONLY_REFRESH_WHEN_ACTIVE = True
```

### **Log Format Parsing**
```python
LOG_VIEWER_FORMATS = {
    'django_default': {
        'pattern': r'(?P<level>\w+)\s+(?P<timestamp>\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2},\d+)\s+(?P<module>[\w\.]+):\s*(?P<message>.*)',
        'timestamp_format': '%Y-%m-%d %H:%M:%S,%f',
        'description': 'Django default format'
    }
}
LOG_VIEWER_FILE_FORMATS = {
    'django.log': 'django_default',
    'celery_beat.log': 'celery_beat',
}
```

### **UI Customization**
```python
LOG_VIEWER_LEVEL_COLORS = {
    'DEBUG': '#6c757d', 'INFO': '#0dcaf0', 'ERROR': '#dc3545'
}
LOG_VIEWER_FILE_LIST_TITLE = "Application Logs"
```

## Testing Multi-line Functionality

The included `celery_beat.log` contains real multi-line stack traces for testing:

1. **Run test script:**
```bash
python test_multiline_debug.py
```

2. **Check pagination:**
```bash
python test_pagination_multiline.py
```

3. **Verify in browser:**
   - Start server and navigate to page 2 of celery_beat.log
   - Verify that multi-line entries (lines 48-133) are grouped correctly
   - Check that pagination adapts to include full multi-line entries

## Development Workflow

1. **Make changes** to django_admin_log_viewer app
2. **Test locally** using myproject test environment
3. **Run tests** to verify functionality
4. **Test multi-line parsing** with included sample logs
5. **Verify UI/UX** in browser with different screen sizes
6. **Check performance** with large log files

## Common Development Tasks

### **Adding New Log Format:**
1. Add format definition to `LOG_VIEWER_FORMATS` 
2. Test regex pattern with sample logs
3. Update `LOG_VIEWER_FILE_FORMATS` mapping
4. Test multi-line detection with new format

### **UI Improvements:**
1. Modify CSS in `static/django_admin_log_viewer/css/`
2. Update JavaScript in `static/django_admin_log_viewer/js/`
3. Test responsive design on different devices
4. Verify dark mode compatibility

### **Performance Optimization:**
1. Profile with large log files (>1MB)
2. Test pagination with different page sizes
3. Monitor AJAX request frequency
4. Check memory usage with long multi-line entries

## Publishing Checklist

- [ ] Update version in `setup.py`
- [ ] Update `CHANGELOG.md` with new features
- [ ] Verify all configuration options in `example_settings.py`
- [ ] Test installation from scratch
- [ ] Run all tests successfully
- [ ] Verify README.md has all features documented
- [ ] Check for any security vulnerabilities
- [ ] Test with different Django versions (3.2+)

## Debugging Tips

### **Multi-line Issues:**
- Check regex patterns in debug scripts
- Verify format detection with `test_multiline_debug.py`
- Use browser dev tools to inspect AJAX responses

### **Performance Issues:**
- Monitor file I/O with large logs
- Check JavaScript console for errors
- Profile memory usage with Python profiler

### **UI Issues:**
- Test on different browsers and screen sizes
- Verify CSS grid/flexbox compatibility
- Check AJAX updates don't break layout
