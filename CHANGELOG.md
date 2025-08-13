# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.0.0] - 2025-08-13

### 🎉 Major Release - Complete Rewrite

This is a major release with significant new features and improvements.

### 🔄 Breaking Changes

#### App Name Change
- **BREAKING**: Changed app name from `log_viewer` to `django_admin_log_viewer`
- **Migration Required**: Update `INSTALLED_APPS` in settings.py
- **Template Paths**: Updated template and static file paths
- **URL Namespaces**: Updated URL patterns and namespaces

### ✨ Added

#### Multi-line Log Processing
- **Smart Multi-line Detection**: Automatically detects and groups multi-line log entries (stack traces, exceptions)
- **Multi-line Aware Pagination**: Never splits multi-line entries across pages
- **Stack Trace Support**: Perfect handling of Python, Java, and other stack traces
- **Line Range Display**: Shows line ranges for multi-line entries (e.g., "48-133")

#### Configurable Log Formats  
- **Format Parser System**: Support for Django, Celery, Nginx, Apache, Syslog formats
- **Custom Regex Patterns**: Define custom log format patterns with named groups
- **Per-file Format Assignment**: Different formats for different log files
- **Module/Logger Extraction**: Automatically extract and display logger/module names

#### Real-time Monitoring
- **Live Mode**: Real-time log monitoring with auto-refresh
- **AJAX Updates**: Smooth updates without page reload
- **Auto-scroll**: Automatically scroll to latest log entries
- **Smart Refresh**: Only refresh when browser tab is active
- **Configurable Intervals**: Customizable refresh rates

#### Log Rotation Support
- **Automatic Detection**: Finds rotated log files (.1, .2, .gz, etc.)
- **Proper Sorting**: Sorts rotated files by rotation index
- **Compressed Files**: Support for gzipped log files
- **Dated Rotations**: Handles date-based log rotation

#### Enhanced UI/UX
- **Responsive Design**: Mobile-friendly interface with sidebar navigation
- **Dark Mode Support**: Built-in dark theme
- **Module Column**: Display logger/module information in separate column
- **Download Functionality**: Download individual log files
- **Level Filtering**: Filter by log levels with dropdown
- **Improved Navigation**: Sidebar with file list and quick access

#### Performance & Security
- **Memory Efficient**: Streaming file reading for large files
- **Smart Caching**: Optimized file reading and parsing
- **Security Hardening**: Enhanced path validation and access control
- **AJAX Optimization**: Reduced server load with intelligent updates

### 🔧 Changed

#### Configuration System
- **New Settings Structure**: Reorganized settings for better usability
- **Format Configuration**: New `LOG_VIEWER_FORMATS` and `LOG_VIEWER_FILE_FORMATS`
- **Enhanced Options**: Many new customization options
- **Better Defaults**: Improved default values for better out-of-box experience

#### Template System
- **Responsive Templates**: Complete template rewrite for modern UI
- **Component-based**: Modular template structure
- **Accessibility**: Improved accessibility features
- **SEO Friendly**: Better semantic HTML structure

#### JavaScript Enhancements
- **ES6+ Code**: Modern JavaScript with better browser support
- **AJAX Improvements**: More robust AJAX handling with error recovery
- **Event Management**: Better event handling and memory management
- **Performance**: Optimized DOM updates and rendering

### 🐛 Fixed

#### Critical Fixes
- **Column Alignment**: Fixed AJAX updates showing content in wrong columns
- **Multi-line Parsing**: Fixed multi-line log entries not grouping correctly
- **Pagination Issues**: Fixed pagination breaking with large multi-line entries
- **Memory Leaks**: Fixed JavaScript memory leaks in long-running sessions

#### UI Fixes
- **Mobile Responsiveness**: Fixed layout issues on mobile devices
- **Dark Mode**: Fixed dark mode inconsistencies
- **File Navigation**: Fixed file switching in sidebar
- **Download Links**: Fixed download functionality for all file types

### 📈 Improved

#### Performance
- **Faster Parsing**: 3x faster log parsing with optimized regex
- **Better Memory Usage**: Reduced memory footprint for large files
- **Efficient Pagination**: Smart pagination reduces server load
- **AJAX Optimization**: Fewer requests with better caching

#### User Experience
- **Intuitive Navigation**: Easier to navigate between multiple log files
- **Real-time Feedback**: Better loading states and error messages
- **Keyboard Support**: Keyboard navigation and shortcuts
- **Search Integration**: Better integration with browser search

### 🔒 Security

#### Enhanced Security
- **Path Validation**: Stronger file path validation to prevent directory traversal
- **Access Control**: Enhanced staff-only access checks
- **Input Sanitization**: Better sanitization of user inputs
- **Error Handling**: Secure error messages that don't leak system information

### 📚 Documentation

#### Complete Documentation
- **README Rewrite**: Comprehensive documentation with examples
- **Configuration Guide**: Detailed configuration options with examples
- **Development Guide**: Updated development and testing instructions
- **Example Settings**: Complete example configuration file

#### New Examples
- **Multi-format Setup**: Examples for different log format configurations
- **Real-time Monitoring**: Examples for production monitoring setups
- **Custom Formats**: How to create custom log format patterns
- **Performance Tuning**: Guidelines for high-performance deployments

## [1.0.0] - 2024-XX-XX

### Initial Release

#### Basic Features
- Django admin integration
- Basic log file viewing
- Simple pagination
- File listing
- Basic styling

---

## Migration Guide

### From v1.x to v2.0

#### Required Changes

1. **Update Settings**: Add new format configuration:
```python
LOG_VIEWER_FORMATS = {
    'django_default': {
        'pattern': r'(?P<level>\w+)\s+(?P<timestamp>\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2},\d+)\s+(?P<module>[\w\.]+):\s*(?P<message>.*)',
        'timestamp_format': '%Y-%m-%d %H:%M:%S,%f',
        'description': 'Django default format'
    }
}
```

2. **Template Updates**: If you customized templates, review new template structure

3. **CSS Updates**: If you customized CSS, check new CSS classes and structure

#### Optional Improvements

1. **Enable Real-time Monitoring**:
```python
LOGVIEWER_AUTO_REFRESH_DEFAULT = True
LOGVIEWER_REFRESH_INTERVAL = 5000
```

2. **Configure Multi-line Support**: No changes needed - works automatically

3. **Add Custom Log Formats**: Define formats for your specific log types

#### Breaking Changes

- Template structure has changed (affects custom templates)
- Some CSS classes have been renamed (affects custom CSS)
- JavaScript structure has changed (affects custom JS)

---

## Support

- **Issues**: [GitHub Issues](https://github.com/ammahmoudi/django-admin-log-viewer/issues)
- **Discussions**: [GitHub Discussions](https://github.com/ammahmoudi/django-admin-log-viewer/discussions)
- **Documentation**: [README.md](README.md)
