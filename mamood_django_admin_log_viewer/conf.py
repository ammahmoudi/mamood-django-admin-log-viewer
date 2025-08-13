"""
Configuration management for django-admin-log-viewer.

This module handles loading default settings and allowing user overrides.
"""

from django.conf import settings
from . import defaults


def get_setting(setting_name, default_value=None):
    """
    Get a setting value, first checking user's Django settings,
    then falling back to app defaults, then to provided default.
    
    Args:
        setting_name: Name of the setting to get
        default_value: Fallback value if not found in defaults or user settings
        
    Returns:
        The setting value
    """
    # First try user's Django settings
    if hasattr(settings, setting_name):
        return getattr(settings, setting_name)
    
    # Then try app defaults
    if hasattr(defaults, setting_name):
        return getattr(defaults, setting_name)
    
    # Finally use provided default
    return default_value


def get_log_files():
    """Get the list of log files to monitor."""
    return get_setting('LOG_VIEWER_FILES', [])


def get_log_files_dir():
    """Get the directory containing log files."""
    return get_setting('LOG_VIEWER_FILES_DIR', '')


def get_page_length():
    """Get the number of log entries per page."""
    return get_setting('LOG_VIEWER_PAGE_LENGTH', 25)


def get_max_read_lines():
    """Get the maximum number of lines to read per request."""
    return get_setting('LOG_VIEWER_MAX_READ_LINES', 1000)


def get_file_list_title():
    """Get the title for the log file list page."""
    return get_setting('LOG_VIEWER_FILE_LIST_TITLE', 'Log Files')


def get_refresh_interval():
    """Get the auto-refresh interval in milliseconds."""
    return get_setting('LOGVIEWER_REFRESH_INTERVAL', 10000)


def get_auto_refresh_default():
    """Get whether auto-refresh is enabled by default."""
    return get_setting('LOGVIEWER_AUTO_REFRESH_DEFAULT', True)


def get_auto_scroll_to_bottom():
    """Get whether to auto-scroll to bottom."""
    return get_setting('LOGVIEWER_AUTO_SCROLL_TO_BOTTOM', True)


def get_only_refresh_when_active():
    """Get whether to only refresh when tab is active."""
    return get_setting('LOGVIEWER_ONLY_REFRESH_WHEN_ACTIVE', True)


def get_disable_access_logs():
    """Get whether to disable access logging for AJAX requests."""
    return get_setting('LOGVIEWER_DISABLE_ACCESS_LOGS', True)


def get_log_formats():
    """Get the dictionary of log format configurations."""
    return get_setting('LOG_VIEWER_FORMATS', {})


def get_default_format():
    """Get the name of the default log format."""
    return get_setting('LOG_VIEWER_DEFAULT_FORMAT', 'django_default')


def get_file_formats():
    """Get the per-file format assignments."""
    return get_setting('LOG_VIEWER_FILE_FORMATS', {})


def get_level_colors():
    """Get the log level color mappings."""
    return get_setting('LOG_VIEWER_LEVEL_COLORS', {})


def get_exclude_pattern():
    """Get the regex pattern for excluding log lines."""
    return get_setting('LOG_VIEWER_EXCLUDE_TEXT_PATTERN', None)


def get_disable_access_logs():
    """Get whether access logs should be disabled in middleware."""
    return get_setting('LOGVIEWER_DISABLE_ACCESS_LOGS', True)
