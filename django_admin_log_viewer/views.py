from django.shortcuts import render
from django.http import JsonResponse, Http404
from django.contrib.admin.views.decorators import staff_member_required
from django.conf import settings
from .utils import get_log_files, read_log_file, format_log_line
from .conf import get_file_list_title, get_page_length, get_refresh_interval


@staff_member_required
def log_list_view(request):
    """View to list all available log files."""
    log_files = get_log_files()
    
    context = {
        'title': get_file_list_title(),
        'log_files': log_files,
    }
    
    return render(request, 'django_admin_log_viewer/log_list.html', context)


@staff_member_required
def log_detail_view(request, filename):
    """View to display log file content."""
    log_files = get_log_files()
    selected_file = None
    
    for log_file in log_files:
        if log_file['name'] == filename:
            selected_file = log_file
            break
    
    if not selected_file:
        raise Http404("Log file not found")
    
    # Get pagination parameters
    page = int(request.GET.get('page', 1))
    page_length = get_page_length()
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
        'refresh_interval': get_refresh_interval(),
    }
    
    return render(request, 'django_admin_log_viewer/log_detail.html', context)


@staff_member_required
def log_ajax_view(request, filename):
    """AJAX endpoint for refreshing log content."""
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
    page_length = get_page_length()
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
