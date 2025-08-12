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


def group_multiline_entries(lines):
    """Group multi-line log entries together."""
    grouped_entries = []
    current_entry_lines = []
    
    # Pattern to detect the start of a new log entry
    log_start_pattern = re.compile(r'^(DEBUG|INFO|WARNING|ERROR|CRITICAL|WARN)\s+\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2}')
    
    for line_num, line in enumerate(lines, 1):
        # Check if this line starts a new log entry
        if log_start_pattern.match(line.strip()):
            # Save the previous entry if it exists
            if current_entry_lines:
                grouped_entries.append({
                    'original_line_numbers': current_entry_lines,
                    'content': ''.join([lines[i-1] for i in current_entry_lines]),
                    'is_multiline': len(current_entry_lines) > 1,
                    'line_count': len(current_entry_lines)
                })
            # Start a new entry
            current_entry_lines = [line_num]
        else:
            # This line is part of the current entry (continuation line)
            if current_entry_lines:
                current_entry_lines.append(line_num)
            else:
                # Orphaned line (shouldn't happen, but handle gracefully)
                grouped_entries.append({
                    'original_line_numbers': [line_num],
                    'content': line,
                    'is_multiline': False,
                    'line_count': 1
                })
    
    # Don't forget the last entry
    if current_entry_lines:
        grouped_entries.append({
            'original_line_numbers': current_entry_lines,
            'content': ''.join([lines[i-1] for i in current_entry_lines]),
            'is_multiline': len(current_entry_lines) > 1,
            'line_count': len(current_entry_lines)
        })
    
    return grouped_entries


def read_log_file(file_path, max_lines=None, start_line=0):
    """Read log file content with pagination and multi-line entry handling."""
    if not os.path.exists(file_path):
        return []
    
    max_read_lines = getattr(settings, 'LOG_VIEWER_MAX_READ_LINES', 1000)
    if max_lines is None:
        max_lines = max_read_lines
    
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            all_lines = f.readlines()
            
        # Apply exclusion pattern if set
        exclude_pattern = getattr(settings, 'LOG_VIEWER_EXCLUDE_TEXT_PATTERN', None)
        if exclude_pattern:
            pattern = re.compile(exclude_pattern)
            all_lines = [line for line in all_lines if not pattern.search(line)]
        
        # Group multi-line log entries
        grouped_entries = group_multiline_entries(all_lines)
        
        # Get the requested slice
        end_line = start_line + max_lines
        entries = grouped_entries[start_line:end_line]
        
        return {
            'lines': entries,
            'total_lines': len(grouped_entries),
            'start_line': start_line,
            'end_line': min(end_line, len(grouped_entries))
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


def format_log_line(entry, entry_number):
    """Format a log entry (which may be multi-line) for display."""
    content = entry if isinstance(entry, str) else entry.get('content', '')
    
    # Extract log level from the first line
    level = parse_log_level(content)
    
    # Extract timestamp from the first line
    timestamp_match = re.search(r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}', content)
    timestamp = timestamp_match.group(0) if timestamp_match else ''
    
    # Determine if this is a long entry that should be truncated
    lines = content.strip().split('\n')
    is_long = len(lines) > 3 or len(content) > 500
    
    # Create preview (first line + indication of more content)
    if is_long:
        preview = lines[0].strip()
        if len(lines) > 1:
            preview += f" ... (+{len(lines)-1} more lines)"
    else:
        preview = content.strip()
    
    # Handle grouped entry info
    if isinstance(entry, dict):
        line_numbers = entry.get('original_line_numbers', [entry_number])
        is_multiline = entry.get('is_multiline', False)
        line_count = entry.get('line_count', 1)
    else:
        line_numbers = [entry_number]
        is_multiline = len(lines) > 1
        line_count = len(lines)
    
    return {
        'number': line_numbers[0] if line_numbers else entry_number,
        'line_range': f"{line_numbers[0]}-{line_numbers[-1]}" if len(line_numbers) > 1 else str(line_numbers[0] if line_numbers else entry_number),
        'level': level,
        'timestamp': timestamp,
        'content': preview,
        'full_content': content.strip(),
        'is_multiline': is_multiline,
        'is_long': is_long,
        'line_count': line_count,
        'raw': content
    }
