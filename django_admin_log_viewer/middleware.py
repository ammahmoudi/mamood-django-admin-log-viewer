"""
Middleware to exclude log viewer AJAX requests from Django logging.
This prevents the log spam caused by auto-refresh requests.
"""
import logging
from django.conf import settings


class LogViewerLoggingFilter(logging.Filter):
    """Custom logging filter to exclude log viewer AJAX requests."""
    
    def filter(self, record):
        # Check if this log record is from a log viewer AJAX request
        if hasattr(record, 'request'):
            request_path = getattr(record.request, 'path', '')
            if '/admin/logs/' in request_path and '/ajax/' in request_path:
                return False  # Don't log this record
        
        # Also check the message content for AJAX requests
        if hasattr(record, 'getMessage'):
            message = record.getMessage()
            if ('admin/logs/' in message and '/ajax/' in message) or \
               ('GET /admin/logs/' in message and 'ajax' in message):
                return False  # Don't log this record
        
        return True  # Log all other records


class LogViewerLoggingMiddleware:
    """Middleware to suppress logging for log viewer AJAX requests."""
    
    def __init__(self, get_response):
        self.get_response = get_response
        self.disable_access_logs = getattr(settings, 'LOGVIEWER_DISABLE_ACCESS_LOGS', True)
        self.filter_installed = False
        
        # Install the filter on relevant loggers
        if self.disable_access_logs and not self.filter_installed:
            self.install_logging_filter()
            self.filter_installed = True
    
    def install_logging_filter(self):
        """Install the custom filter on Django's server loggers."""
        log_filter = LogViewerLoggingFilter()
        
        # Add filter to the loggers that handle HTTP requests
        loggers_to_filter = [
            'django.server',
            'django.server.basehttp',
            'django.request',
        ]
        
        for logger_name in loggers_to_filter:
            logger = logging.getLogger(logger_name)
            logger.addFilter(log_filter)
        
        # Also add to root logger as a fallback
        logging.getLogger().addFilter(log_filter)
        
    def __call__(self, request):
        # The filter handles suppression, so just process the request normally
        response = self.get_response(request)
        return response
