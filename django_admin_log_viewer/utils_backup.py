import os
import re
import glob
from datetime import datetime
from django.conf import settings


def get_log_files():
    """Get list of log files from settings, including rotational files."""
    log_files = getattr(settings, 'LOG_VIEWER_FILES', [])
    log_dir = getattr(settings, 'LOG_VIEWER_FILES_DIR', '')
    
    available_files = []
    processed_base_names = set()
    
    for log_file in log_files:
        base_name = log_file
        base_path = os.path.join(log_dir, log_file)
        
        # Skip if we've already processed this base name
        if base_name in processed_base_names:
            continue
        processed_base_names.add(base_name)
        
        # Find all rotational files for this log
        rotational_files = find_rotational_files(log_dir, log_file)
        
        if rotational_files:
            # Group rotational files under the base name
            available_files.append({
                'name': base_name,
                'path': base_path,
                'type': 'rotational_group',
                'rotational_files': rotational_files,
                'size': sum(f['size'] for f in rotational_files),
                'modified': max(f['modified'] for f in rotational_files),
                'file_count': len(rotational_files)
            })
        elif os.path.exists(base_path):
            # Single file (no rotational files found)
            file_info = os.stat(base_path)
            available_files.append({
                'name': base_name,
                'path': base_path,
                'type': 'single',
                'size': file_info.st_size,
                'modified': datetime.fromtimestamp(file_info.st_mtime),
            })
    
    return available_files


def find_rotational_files(log_dir, base_filename):
    """Find all rotational files for a given base filename."""
    rotational_files = []
    base_path = os.path.join(log_dir, base_filename)
    
    # Check if the main file exists
    if os.path.exists(base_path):
        file_info = os.stat(base_path)
        rotational_files.append({
            'name': base_filename,
            'path': base_path,
            'rotation_index': 0,
            'size': file_info.st_size,
            'modified': datetime.fromtimestamp(file_info.st_mtime),
            'is_current': True
        })
    
    # Look for numbered rotational files (e.g., django.log.1, django.log.2)
    pattern1 = os.path.join(log_dir, f"{base_filename}.[0-9]*")
    numbered_files = glob.glob(pattern1)
    
    # Look for dated rotational files (e.g., django.log.2025-01-15)
    pattern2 = os.path.join(log_dir, f"{base_filename}.[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]*")
    dated_files = glob.glob(pattern2)
    
    # Look for gzipped rotational files
    pattern3 = os.path.join(log_dir, f"{base_filename}.[0-9]*.gz")
    gzipped_files = glob.glob(pattern3)
    
    all_rotational = set(numbered_files + dated_files + gzipped_files)
    
    for file_path in all_rotational:
        if os.path.exists(file_path):
            filename = os.path.basename(file_path)
            file_info = os.stat(file_path)
            
            # Extract rotation index for sorting
            rotation_index = extract_rotation_index(filename, base_filename)
            
            rotational_files.append({
                'name': filename,
                'path': file_path,
                'rotation_index': rotation_index,
                'size': file_info.st_size,
                'modified': datetime.fromtimestamp(file_info.st_mtime),
                'is_current': False
            })
    
    # Sort by rotation index (0 = current, 1 = most recent backup, etc.)
    rotational_files.sort(key=lambda x: x['rotation_index'])
    
    return rotational_files if rotational_files else []


def extract_rotation_index(filename, base_filename):
    """Extract rotation index from filename for proper sorting."""
    # Remove base filename to get the suffix
    suffix = filename[len(base_filename):]
    
    if not suffix:
        return 0  # Main file
    
    # Handle numbered rotations (.1, .2, .3, etc.)
    if re.match(r'^\.\d+$', suffix):
        return int(suffix[1:])
    
    # Handle numbered rotations with .gz (.1.gz, .2.gz, etc.)
    match = re.match(r'^\.(\d+)\.gz$', suffix)
    if match:
        return int(match.group(1))
    
    # Handle dated rotations (assign higher numbers for older dates)
    if re.match(r'^\.\d{4}-\d{2}-\d{2}', suffix):
        # Use timestamp as index (older files get higher numbers)
        try:
            date_part = suffix.split('.gz')[0][1:]  # Remove leading dot and .gz if present
            date_obj = datetime.strptime(date_part[:10], '%Y-%m-%d')
            # Convert to negative timestamp so older files sort later
            return int((datetime.now() - date_obj).days) + 1000
        except (ValueError, IndexError):
            return 9999
    
    # Default for unknown formats
    return 9999


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
                # Orphan line at the beginning - create a single line entry
                current_entry_lines = [line_num]
    
    # Don't forget the last entry
    if current_entry_lines:
        grouped_entries.append({
            'original_line_numbers': current_entry_lines,
            'content': ''.join([lines[i-1] for i in current_entry_lines]),
            'is_multiline': len(current_entry_lines) > 1,
            'line_count': len(current_entry_lines)
        })
    
    return grouped_entries


def read_log_file(file_path, lines_per_page=25, start_line=0):
    """Read log file with pagination support."""
    try:
        # Handle gzipped files
        if file_path.endswith('.gz'):
            import gzip
            with gzip.open(file_path, 'rt', encoding='utf-8', errors='replace') as f:
                all_lines = f.readlines()
        else:
            with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                all_lines = f.readlines()
    except (IOError, OSError) as e:
        return {
            'lines': [f'Error reading file: {str(e)}'],
            'total_lines': 1,
            'start_line': 0,
            'end_line': 1
        }
    
    total_lines = len(all_lines)
    end_line = min(start_line + lines_per_page, total_lines)
    
    # Get the requested slice of lines
    selected_lines = all_lines[start_line:end_line]
    
    return {
        'lines': selected_lines,
        'total_lines': total_lines,
        'start_line': start_line,
        'end_line': end_line
    }


def format_log_line(line, line_number):
    """Format a single log line for display."""
    line = line.strip()
    
    # Parse log line to extract components
    log_pattern = re.compile(r'^(DEBUG|INFO|WARNING|ERROR|CRITICAL|WARN)\s+(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2}[,\.]\d+)\s+(.+?):\s+(.+)$')
    
    match = log_pattern.match(line)
    
    if match:
        level = match.group(1)
        timestamp = match.group(2)
        logger_name = match.group(3)
        message = match.group(4)
        
        # Truncate long messages for preview
        max_length = 200
        is_long = len(message) > max_length
        content = message[:max_length] + ('...' if is_long else '')
        
        return {
            'number': line_number,
            'level': level,
            'timestamp': timestamp,
            'logger': logger_name,
            'content': content,
            'full_content': message,
            'is_long': is_long,
            'is_multiline': False,
            'line_count': 1,
            'line_range': str(line_number)
        }
    else:
        # If it doesn't match the expected pattern, treat as raw text
        max_length = 200
        is_long = len(line) > max_length
        content = line[:max_length] + ('...' if is_long else '')
        
        return {
            'number': line_number,
            'level': 'INFO',  # Default level
            'timestamp': '',
            'logger': '',
            'content': content,
            'full_content': line,
            'is_long': is_long,
            'is_multiline': False,
            'line_count': 1,
            'line_range': str(line_number)
        }
