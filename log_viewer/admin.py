from django.contrib import admin
from django.urls import path
from django.http import JsonResponse
from django.template.response import TemplateResponse
from django.contrib.admin import AdminSite
from .utils import get_log_files, read_log_file, format_log_line


class LogViewerAdminMixin:
    """Mixin to add log viewer functionality to admin site."""
    
    def get_urls(self):
        """Add log viewer URLs to admin."""
        urls = super().get_urls()
        log_urls = [
            path('logs/', self.admin_view(self.log_list_view), name='log_viewer_list'),
            path('logs/<str:filename>/', self.admin_view(self.log_detail_view), name='log_viewer_detail'),
            path('logs/<str:filename>/ajax/', self.admin_view(self.log_ajax_view), name='log_viewer_ajax'),
        ]
        return log_urls + urls
    
    def log_list_view(self, request):
        """View to list all available log files."""
        from django.conf import settings
        
        log_files = get_log_files()
        
        context = {
            **self.each_context(request),
            'title': getattr(settings, 'LOG_VIEWER_FILE_LIST_TITLE', 'Log Files'),
            'log_files': log_files,
            'has_permission': True,
            'opts': {
                'app_label': 'log_viewer',
                'model_name': 'logfile',
                'verbose_name': 'Log File',
                'verbose_name_plural': 'Log Files',
            }
        }
        
        return TemplateResponse(request, 'log_viewer/log_list.html', context)
    
    def log_detail_view(self, request, filename):
        """View to display log file content."""
        from django.conf import settings
        
        log_files = get_log_files()
        selected_file = None
        
        for log_file in log_files:
            if log_file['name'] == filename:
                selected_file = log_file
                break
        
        if not selected_file:
            from django.http import Http404
            raise Http404("Log file not found")
        
        # Get pagination parameters
        page = int(request.GET.get('page', 1))
        page_length = getattr(settings, 'LOG_VIEWER_PAGE_LENGTH', 25)
        start_line = (page - 1) * page_length
        
        # Read log content
        log_data = read_log_file(selected_file['path'], page_length, start_line)
        
        # Format log lines
        formatted_lines = []
        for i, line in enumerate(log_data['lines']):
            formatted_line = format_log_line(line, start_line + i + 1)
            formatted_lines.append(formatted_line)
        
        # Calculate pagination info
        total_pages = (log_data['total_lines'] + page_length - 1) // page_length
        
        context = {
            **self.each_context(request),
            'title': f'Log Viewer - {filename}',
            'filename': filename,
            'log_file': selected_file,
            'log_lines': formatted_lines,
            'current_page': page,
            'total_pages': total_pages,
            'total_lines': log_data['total_lines'],
            'start_line': log_data['start_line'] + 1,
            'end_line': log_data['end_line'],
            'page_length': page_length,
            'refresh_interval': getattr(settings, 'LOGVIEWER_REFRESH_INTERVAL', 1000),
            'only_refresh_when_active': getattr(settings, 'LOGVIEWER_ONLY_REFRESH_WHEN_ACTIVE', True),
            'auto_refresh_default': getattr(settings, 'LOGVIEWER_AUTO_REFRESH_DEFAULT', True),
            'auto_scroll_to_bottom': getattr(settings, 'LOGVIEWER_AUTO_SCROLL_TO_BOTTOM', True),
            'has_permission': True,
            'opts': {
                'app_label': 'log_viewer',
                'model_name': 'logfile',
                'verbose_name': 'Log File',
                'verbose_name_plural': 'Log Files',
            }
        }
        
        return TemplateResponse(request, 'log_viewer/log_detail.html', context)
    
    def log_ajax_view(self, request, filename):
        """AJAX endpoint for refreshing log content."""
        from django.conf import settings
        
        log_files = get_log_files()
        selected_file = None
        
        for log_file in log_files:
            if log_file['name'] == filename:
                selected_file = log_file
                break
        
        if not selected_file:
            return JsonResponse({'error': 'Log file not found'}, status=404)
        
        # Get pagination parameters
        page = int(request.GET.get('page', 1))
        page_length = getattr(settings, 'LOG_VIEWER_PAGE_LENGTH', 25)
        start_line = (page - 1) * page_length
        
        # Read log content
        log_data = read_log_file(selected_file['path'], page_length, start_line)
        
        # Format log lines
        formatted_lines = []
        for i, line in enumerate(log_data['lines']):
            formatted_line = format_log_line(line, start_line + i + 1)
            formatted_lines.append(formatted_line)
        
        return JsonResponse({
            'log_lines': formatted_lines,
            'total_lines': log_data['total_lines'],
            'start_line': log_data['start_line'] + 1,
            'end_line': log_data['end_line'],
        })


# Create a custom admin site with log viewer functionality
class LogViewerAdminSite(LogViewerAdminMixin, AdminSite):
    site_header = 'Django Administration with Log Viewer'
    site_title = 'Django Admin'
    index_title = 'Welcome to Django Administration'


# Create an instance of the custom admin site
admin_site = LogViewerAdminSite(name='admin')

# Replace the default admin site
admin.site = admin_site
