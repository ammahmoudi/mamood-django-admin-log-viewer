import os
import re
from datetime import datetime
from django.conf import settings


def get_log_files():
    """Get list of log files from settings."""
    log_files = getattr(settings, 'LOG_VIEWER_FILES', [])
    log_dir = getattr(settings, 'LOG_VIEWER_FILES_DIR', '')
    
    available_files = []
    for log_file in log_files:
        file_path = os.path.join(log_dir, log_file)
        if os.path.exists(file_path):
            file_info = os.stat(file_path)
            available_files.append({
                'name': log_file,
                'path': file_path,
                'size': file_info.st_size,
                'modified': datetime.fromtimestamp(file_info.st_mtime),
            })
    return available_files


def read_log_file(file_path, max_lines=None, start_line=0):
    """Read log file content with pagination."""
    if not os.path.exists(file_path):
        return []
    
    max_read_lines = getattr(settings, 'LOG_VIEWER_MAX_READ_LINES', 1000)
    if max_lines is None:
        max_lines = max_read_lines
    
    lines = []
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            all_lines = f.readlines()
            
        # Apply exclusion pattern if set
        exclude_pattern = getattr(settings, 'LOG_VIEWER_EXCLUDE_TEXT_PATTERN', None)
        if exclude_pattern:
            pattern = re.compile(exclude_pattern)
            all_lines = [line for line in all_lines if not pattern.search(line)]
        
        # Get the requested slice
        end_line = start_line + max_lines
        lines = all_lines[start_line:end_line]
        
        return {
            'lines': lines,
            'total_lines': len(all_lines),
            'start_line': start_line,
            'end_line': min(end_line, len(all_lines))
        }
    except Exception as e:
        return {
            'lines': [f'Error reading file: {str(e)}'],
            'total_lines': 0,
            'start_line': 0,
            'end_line': 0
        }


def parse_log_level(line):
    """Extract log level from log line."""
    patterns = [
        r'(DEBUG|INFO|WARNING|ERROR|CRITICAL)',
        r'(WARN)',  # Some logs use WARN instead of WARNING
    ]
    
    for pattern in patterns:
        match = re.search(pattern, line.upper())
        if match:
            level = match.group(1)
            if level == 'WARN':
                return 'WARNING'
            return level
    return 'INFO'  # Default level


def format_log_line(line, line_number):
    """Format a single log line for display."""
    level = parse_log_level(line)
    timestamp_match = re.search(r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}', line)
    timestamp = timestamp_match.group(0) if timestamp_match else ''
    
    return {
        'number': line_number,
        'level': level,
        'timestamp': timestamp,
        'content': line.strip(),
        'raw': line
    }
