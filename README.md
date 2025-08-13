# Django Admin Log Viewer

A powerful Django app that provides a comprehensive web interface to view and monitor log files directly in the Django admin panel.

## 🌟 Features

### Core Features
- **Multi-Log File Support**: View multiple log files with automatic detection and grouping
- **Configurable Log Formats**: Support for Django, Celery, Nginx, and custom log formats
- **Multi-line Log Processing**: Properly handles stack traces and multi-line log entries
- **Smart Pagination**: Multi-line aware pagination that never splits log entries across pages
- **Real-time Monitoring**: Live mode with auto-refresh for real-time log monitoring
- **Log Rotation Support**: Automatic detection and handling of rotated log files (.1, .2, .gz, etc.)

### User Experience
- **Responsive Design**: Works perfectly on desktop, tablet, and mobile devices
- **Dark Mode Support**: Built-in dark theme for comfortable viewing
- **Advanced Filtering**: Filter by log levels (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- **Download Functionality**: Download individual log files directly from the interface
- **Sidebar Navigation**: Easy navigation between multiple log files
- **Search & Filtering**: Quick search through log content

### Technical Features
- **Memory Efficient**: Streaming file reading for large log files
- **Security Focused**: Staff-only access with proper file path validation
- **Performance Optimized**: AJAX-based updates for smooth user experience
- **No Database Required**: Reads files directly from disk
- **Configurable UI**: Customizable colors, refresh intervals, and display options

## 📦 Installation

### Production Installation

```bash
pip install django-admin-log-viewer
```

### Development Installation (Editable Mode)

For development or contributing:

```bash
# Clone the repository
git clone https://github.com/ammahmoudi/django-admin-log-viewer.git
cd django-admin-log-viewer

# Install in editable mode
pip install -e .

# Or with development dependencies
pip install -e .[dev]
```

The editable install (`-e` flag) allows you to modify the source code and see changes immediately without reinstalling.

### 2. Add to Django Settings

Add `django_admin_log_viewer` to your `INSTALLED_APPS`:

```python
INSTALLED_APPS = [
    # ... other apps
    'django.contrib.admin',  # Required
    'django.contrib.auth',   # Required  
    'django.contrib.contenttypes',  # Required
    'django_admin_log_viewer',
]
```

### 3. Basic Configuration

Add to your `settings.py`:

```python
import os
from pathlib import Path

# Basic log viewer settings
LOG_VIEWER_FILES = ['django.log', 'application.log']
LOG_VIEWER_FILES_DIR = BASE_DIR / 'logs'  # or '/path/to/your/logs/'
LOG_VIEWER_PAGE_LENGTH = 25
```

### 4. URL Configuration

The log viewer integrates automatically with Django admin - no URL configuration needed!

## ⚙️ Configuration

The Django Admin Log Viewer comes with comprehensive default settings that work out of the box. You only need to specify the log files you want to monitor - all other settings are optional and have sensible defaults.

### Required Settings

```python
# Required: List of log files to monitor
LOG_VIEWER_FILES = ['django.log', 'application.log', 'celery_beat.log']

# Required: Directory containing log files
LOG_VIEWER_FILES_DIR = BASE_DIR / 'logs'
```

### Optional Settings (with defaults)

All the settings below are optional. The app provides comprehensive defaults that work well for most use cases:

```python
# Display settings (defaults shown)
LOG_VIEWER_PAGE_LENGTH = 25                    # Log entries per page
LOG_VIEWER_MAX_READ_LINES = 1000              # Max lines to read per request
LOG_VIEWER_FILE_LIST_MAX_ITEMS_PER_PAGE = 25  # Files per page in file list
LOG_VIEWER_FILE_LIST_TITLE = "Log Files"      # Title for file list page

# Real-time monitoring (defaults shown)
LOGVIEWER_REFRESH_INTERVAL = 10000            # Auto-refresh interval (10 seconds)
LOGVIEWER_AUTO_REFRESH_DEFAULT = True         # Enable auto-refresh by default
LOGVIEWER_AUTO_SCROLL_TO_BOTTOM = True        # Auto-scroll to latest logs
LOGVIEWER_ONLY_REFRESH_WHEN_ACTIVE = True     # Only refresh when tab is active

# Performance settings (defaults shown)
LOGVIEWER_INITIAL_NUMBER_OF_CHARS = 2048      # Initial load size
LOGVIEWER_DISABLE_ACCESS_LOGS = True          # Don't log AJAX requests
```

> **💡 Pro Tip**: You only need to specify settings that you want to change from the defaults. The app will automatically use sensible defaults for any unspecified settings.

### 🎯 Quick Start Summary

For most users, you only need these two settings to get started:

```python
# Minimal configuration - just specify your log files!
LOG_VIEWER_FILES = ['django.log', 'application.log'] 
LOG_VIEWER_FILES_DIR = BASE_DIR / 'logs'

# Everything else uses intelligent defaults:
# ✅ 8 built-in log format patterns (Django, Celery, Nginx, Apache, etc.)
# ✅ Beautiful color scheme for all log levels  
# ✅ Real-time monitoring with 10-second refresh
# ✅ 25 entries per page with smart multi-line pagination
# ✅ Performance optimizations enabled by default
```

### Advanced Log Format Configuration

The app comes with **8 built-in log format patterns** that handle most common log formats out of the box:

#### Built-in Log Formats

- **`django_default`** - Django standard format: `LEVEL YYYY-MM-DD HH:MM:SS,mmm module: message`
- **`simple`** - Simple format: `LEVEL: message`  
- **`celery_beat`** - Celery Beat scheduler logs
- **`celery_worker`** - Celery Worker task logs
- **`nginx_access`** - Nginx access log format
- **`nginx_error`** - Nginx error log format
- **`apache_common`** - Apache Common Log Format
- **`syslog`** - Standard syslog format

#### Custom Log Format Configuration

If you need custom log parsing, you can override or extend the default formats:

```python
# Custom log format configuration (optional)
LOG_VIEWER_FORMATS = {
    # Use any of the built-in formats, or define your own
    'my_custom_format': {
        'pattern': r'(?P<level>\w+)\s+(?P<timestamp>\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2})\s+(?P<message>.*)',
        'timestamp_format': '%Y-%m-%d %H:%M:%S',
        'description': 'My custom format'
    }
}

# Per-file format assignment
LOG_VIEWER_FILE_FORMATS = {
    'django.log': 'django_default',
    'application.log': 'simple', 
    'celery_beat.log': 'celery_beat',
    'access.log': 'nginx_access',
}

# Default format for unspecified files
LOG_VIEWER_DEFAULT_FORMAT = 'django_default'
```

### Styling and Colors

The app comes with a comprehensive **default color scheme** for all log levels. You only need to customize colors if you want to override the defaults:

#### Default Color Scheme

- **DEBUG**: `#6c757d` (Gray) - Low-priority debug information
- **INFO**: `#0dcaf0` (Cyan) - General informational messages  
- **WARNING/WARN**: `#ffc107` (Yellow) - Warning messages
- **ERROR**: `#dc3545` (Red) - Error conditions
- **CRITICAL/FATAL**: `#6f42c1` (Purple) - Critical system errors
- **NOTICE**: `#17a2b8` (Teal) - Important notices
- **ALERT**: `#fd7e14` (Orange) - Alert conditions

#### Custom Color Configuration (Optional)

```python
# Override default colors only if needed
LOG_VIEWER_LEVEL_COLORS = {
    'ERROR': '#ff0000',    # Custom red for errors
    'DEBUG': '#888888',    # Custom gray for debug
    # ... other custom colors
}

# Optional: Exclude certain log patterns  
LOG_VIEWER_EXCLUDE_TEXT_PATTERN = r'healthcheck|ping'  # Regex pattern
```

## 🚀 Usage

### Accessing the Log Viewer

1. Login to Django Admin as a staff user
2. Look for **"Log Files"** in the admin interface, or navigate directly to `admin/logs/`
3. Click to view the list of available log files
4. Select any log file to view its contents

**Direct URL Access**: You can also access logs directly at `http://your-domain.com/admin/logs/` after logging in as a staff user.

### Features in Action

- **Real-time Monitoring**: Toggle "Live Mode" to auto-refresh logs
- **Multi-line Support**: Stack traces and exceptions are properly grouped
- **Download Logs**: Click the download button to save log files locally
- **Pagination**: Navigate through large log files with smart pagination
- **Filtering**: Filter by log levels using the dropdown menu
- **Search**: Use browser search (Ctrl+F) to find specific content

## 🔧 Advanced Usage

### Custom Log Formats

Create custom regex patterns for your specific log formats:

```python
LOG_VIEWER_FORMATS = {
    'my_custom_format': {
        'pattern': r'(?P<timestamp>\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2})\s+(?P<level>\w+)\s+(?P<message>.*)',
        'timestamp_format': '%Y-%m-%dT%H:%M:%S',
        'description': 'Custom ISO timestamp format'
    }
}
```

### Log Rotation Support

The viewer automatically detects rotated log files:

- `application.log` (current)
- `application.log.1` (yesterday)
- `application.log.2.gz` (compressed older logs)
- `application.log.2023-12-01` (dated logs)

### Multi-line Processing

Perfect handling of:

- Python stack traces
- Java exceptions  
- SQL query logs
- JSON formatted logs
- Any multi-line log entry

## 🛡️ Security

- **Staff Only Access**: Only Django staff users can access log files
- **Path Validation**: Prevents directory traversal attacks
- **File Size Limits**: Configurable limits prevent memory exhaustion
- **Error Handling**: Graceful handling of missing or corrupt files

## 📋 Requirements

- **Python**: 3.8+
- **Django**: 4.2+
- **Permissions**: Staff access to Django admin

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

MIT License - see LICENSE file for details.

## 🐛 Troubleshooting

### Log Files Not Showing

- Check `LOG_VIEWER_FILES_DIR` path exists
- Verify file permissions
- Ensure files are listed in `LOG_VIEWER_FILES`

### Performance Issues

- Reduce `LOG_VIEWER_PAGE_LENGTH` for large files
- Increase `LOGVIEWER_REFRESH_INTERVAL`
- Set `LOGVIEWER_DISABLE_ACCESS_LOGS = True`

### Multi-line Logs Not Grouping

- Check your log format regex pattern
- Ensure the pattern matches the first line of log entries
- Verify timestamp format matches your logs

## 🎯 Changelog

### v2.0.0 (Latest)

- ✅ Multi-line log processing with smart pagination
- ✅ Configurable log format parsing
- ✅ Log rotation support
- ✅ Dark mode theme
- ✅ Real-time monitoring with live mode
- ✅ Module/logger name display
- ✅ Download functionality
- ✅ Responsive sidebar navigation
- ✅ Memory-efficient streaming

---

⭐ **Star this repo if you find it useful!**
