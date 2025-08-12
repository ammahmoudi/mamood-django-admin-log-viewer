"""
Middleware to exclude log viewer AJAX requests from Django logging.
This prevents the log spam caused by auto-refresh requests.
"""
import logging
from django.conf import settings


class LogViewerLoggingMiddleware:
    """Middleware to suppress logging for log viewer AJAX requests."""
    
    def __init__(self, get_response):
        self.get_response = get_response
        self.disable_access_logs = getattr(settings, 'LOGVIEWER_DISABLE_ACCESS_LOGS', True)
        
    def __call__(self, request):
        # Check if this is a log viewer AJAX request
        is_log_viewer_ajax = (
            self.disable_access_logs and
            '/admin/logs/' in request.path and
            request.path.endswith('/ajax/')
        )
        
        if is_log_viewer_ajax:
            # Temporarily disable Django's request logging
            loggers_to_suppress = [
                logging.getLogger('django.server'),
                logging.getLogger('django.request'), 
                logging.getLogger('basehttp')  # This handles the HTTP request logging
            ]
            original_levels = {}
            
            # Store original levels and set to ERROR
            for logger in loggers_to_suppress:
                original_levels[logger] = logger.level
                logger.setLevel(logging.ERROR)
            
            try:
                response = self.get_response(request)
            finally:
                # Restore original logging levels
                for logger in loggers_to_suppress:
                    logger.setLevel(original_levels[logger])
        else:
            response = self.get_response(request)
        
        return response
