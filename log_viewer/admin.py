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
            path('logs/<str:filename>/download/', self.admin_view(self.log_download_view), name='log_viewer_download'),
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
        
        # First, try to find exact match
        for log_file in log_files:
            if log_file['name'] == filename:
                selected_file = log_file
                break
            # If it's a rotational group, check individual files
            if log_file.get('type') == 'rotational_group':
                for rot_file in log_file['rotational_files']:
                    if rot_file['name'] == filename:
                        selected_file = {
                            'name': filename,
                            'path': rot_file['path'],
                            'size': rot_file['size'],
                            'modified': rot_file['modified'],
                            'is_rotational': True,
                            'parent_group': log_file['name']
                        }
                        break
                if selected_file:
                    break
        
        if not selected_file:
            from django.http import Http404
            raise Http404("Log file not found")
        
        # Check if we're in live mode or specific page mode
        # If page parameter exists, it should override live mode to false
        if 'page' in request.GET:
            live_mode = False
            page = int(request.GET.get('page', 1))
        else:
            live_mode = request.GET.get('live', 'true').lower() == 'true'
            page = 1
        
        # Disable live mode for rotational files (they don't change)
        if selected_file.get('is_rotational'):
            live_mode = False
        
        page_length = getattr(settings, 'LOG_VIEWER_PAGE_LENGTH', 25)
        
        if live_mode and not selected_file.get('is_rotational'):
            # In live mode, always show the latest logs (last page)
            # First get total lines to calculate the last page
            temp_log_data = read_log_file(selected_file['path'], page_length, 0)
            total_pages = max(1, (temp_log_data['total_lines'] + page_length - 1) // page_length)
            page = total_pages
            start_line = (page - 1) * page_length
            log_data = read_log_file(selected_file['path'], page_length, start_line)
        else:
            # In manual mode, show specific page
            # First get total lines to validate page number
            temp_log_data = read_log_file(selected_file['path'], page_length, 0)
            total_pages = max(1, (temp_log_data['total_lines'] + page_length - 1) // page_length)
            # Ensure page is within valid range
            page = max(1, min(page, total_pages))
            start_line = (page - 1) * page_length
            log_data = read_log_file(selected_file['path'], page_length, start_line)
        
        # Format log lines
        formatted_lines = []
        for i, line in enumerate(log_data['lines']):
            formatted_line = format_log_line(line, start_line + i + 1)
            formatted_lines.append(formatted_line)
        
        # Calculate pagination info
        # Use the actual total_lines from the final log_data, not temp_log_data
        total_pages = max(1, (log_data['total_lines'] + page_length - 1) // page_length)
        
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
            'live_mode': live_mode,
            'is_rotational': selected_file.get('is_rotational', False),
            'refresh_interval': getattr(settings, 'LOGVIEWER_REFRESH_INTERVAL', 10000),
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
        
        # First, try to find exact match
        for log_file in log_files:
            if log_file['name'] == filename:
                selected_file = log_file
                break
            # If it's a rotational group, check individual files
            if log_file.get('type') == 'rotational_group':
                for rot_file in log_file['rotational_files']:
                    if rot_file['name'] == filename:
                        selected_file = {
                            'name': filename,
                            'path': rot_file['path'],
                            'size': rot_file['size'],
                            'modified': rot_file['modified'],
                            'is_rotational': True,
                            'parent_group': log_file['name']
                        }
                        break
                if selected_file:
                    break
        
        if not selected_file:
            return JsonResponse({'error': 'Log file not found'}, status=404)
        
        page_length = getattr(settings, 'LOG_VIEWER_PAGE_LENGTH', 25)
        
        # Check if we're in live mode or specific page mode
        # If page parameter exists, it should override live mode to false
        if 'page' in request.GET:
            live_mode = False
            page = int(request.GET.get('page', 1))
        else:
            live_mode = request.GET.get('live', 'true').lower() == 'true'
            page = 1
        
        if live_mode:
            # In live mode, always get the latest logs (last page)
            # First get total lines to calculate the last page
            temp_log_data = read_log_file(selected_file['path'], page_length, 0)
            total_pages = max(1, (temp_log_data['total_lines'] + page_length - 1) // page_length)
            page = total_pages
            start_line = (page - 1) * page_length
            log_data = read_log_file(selected_file['path'], page_length, start_line)
        else:
            # In normal mode, get specific page
            # First get total lines to validate page number
            temp_log_data = read_log_file(selected_file['path'], page_length, 0)
            total_pages = max(1, (temp_log_data['total_lines'] + page_length - 1) // page_length)
            # Ensure page is within valid range
            page = max(1, min(page, total_pages))
            start_line = (page - 1) * page_length
            log_data = read_log_file(selected_file['path'], page_length, start_line)
        
        # Format log lines
        formatted_lines = []
        for i, line in enumerate(log_data['lines']):
            formatted_line = format_log_line(line, start_line + i + 1)
            formatted_lines.append(formatted_line)
        
        # Calculate total pages
        total_pages = max(1, (log_data['total_lines'] + page_length - 1) // page_length)
        
        return JsonResponse({
            'log_lines': formatted_lines,
            'total_lines': log_data['total_lines'],
            'start_line': log_data['start_line'] + 1,
            'end_line': log_data['end_line'],
            'current_page': page,
            'total_pages': total_pages,
            'live_mode': live_mode,
        })
    
    def log_download_view(self, request, filename):
        """Download log file."""
        import os
        from django.http import HttpResponse, Http404
        
        log_files = get_log_files()
        selected_file = None
        
        # First, try to find exact match
        for log_file in log_files:
            if log_file['name'] == filename:
                selected_file = log_file
                break
            # If it's a rotational group, check individual files
            if log_file.get('type') == 'rotational_group':
                for rot_file in log_file['rotational_files']:
                    if rot_file['name'] == filename:
                        selected_file = {
                            'name': filename,
                            'path': rot_file['path'],
                            'size': rot_file['size'],
                            'modified': rot_file['modified'],
                            'is_rotational': True,
                            'parent_group': log_file['name']
                        }
                        break
                if selected_file:
                    break
        
        if not selected_file or not os.path.exists(selected_file['path']):
            raise Http404("Log file not found")
        
        try:
            # Handle compressed files
            if selected_file['path'].endswith('.gz'):
                import gzip
                with gzip.open(selected_file['path'], 'rt', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                content_type = 'application/gzip'
                filename_with_ext = filename
            else:
                with open(selected_file['path'], 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                content_type = 'text/plain'
                filename_with_ext = filename + '.log' if not filename.endswith('.log') else filename
            
            response = HttpResponse(content, content_type=content_type)
            response['Content-Disposition'] = f'attachment; filename="{filename_with_ext}"'
            response['Content-Length'] = len(content.encode('utf-8'))
            
            return response
            
        except Exception as e:
            return HttpResponse(f'Error reading file: {str(e)}', status=500)


# Create a custom admin site with log viewer functionality
class LogViewerAdminSite(LogViewerAdminMixin, AdminSite):
    site_header = 'Django Administration with Log Viewer'
    site_title = 'Django Admin'
    index_title = 'Welcome to Django Administration'


# Create an instance of the custom admin site
admin_site = LogViewerAdminSite(name='admin')

# Replace the default admin site
admin.site = admin_site
