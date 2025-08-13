import os
import re
import glob
from datetime import datetime
from django.conf import settings
from .conf import get_log_files, get_log_files_dir, get_log_formats, get_default_format, get_file_formats


def get_log_files():
    """Get list of log files from settings, including rotational files."""
    from .conf import get_log_files as get_configured_files, get_log_files_dir
    
    log_files = get_configured_files()
    log_dir = get_log_files_dir()
    
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


def group_multiline_entries(lines, filename=None):
    """Group multi-line log entries together using configurable format detection."""
    grouped_entries = []
    current_entry_lines = []
    
    # Get format configuration for this file
    if filename:
        format_config = get_log_format_for_file(filename)
    else:
        # Use default format if filename not provided
        format_config = {
            'pattern': r'(?P<level>\w+)\s+(?P<timestamp>\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2},\d+)\s+(?P<module>[\w\.]+):\s*(?P<message>.*)',
            'timestamp_format': '%Y-%m-%d %H:%M:%S,%f',
            'description': 'Default Django format'
        }
    
    # Compile the pattern to detect the start of a new log entry
    try:
        log_start_pattern = re.compile(format_config['pattern'])
    except re.error:
        # Fallback to basic pattern if regex compilation fails
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


def read_log_file_multiline_aware(file_path, entries_per_page=25, start_entry=0, filename=None):
    """Read log file with multi-line aware pagination support."""
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
            'entries': [format_log_line(f'Error reading file: {str(e)}', 1, filename)],
            'total_entries': 1,
            'total_lines': 1,
            'start_entry': 0,
            'end_entry': 1,
            'actual_start_line': 1,
            'actual_end_line': 1
        }
    
    total_lines = len(all_lines)
    
    # First, group all lines into multi-line entries
    all_entries = process_log_lines_with_multiline(all_lines, 1, filename)
    total_entries = len(all_entries)
    
    # Calculate pagination for entries (not lines)
    end_entry = min(start_entry + entries_per_page, total_entries)
    selected_entries = all_entries[start_entry:end_entry]
    
    # Calculate actual line ranges covered by selected entries
    if selected_entries:
        # Find the actual line numbers covered
        first_entry_line = int(selected_entries[0]['line_range'].split('-')[0]) if '-' in selected_entries[0]['line_range'] else int(selected_entries[0]['line_range'])
        last_entry = selected_entries[-1]
        last_entry_line = int(last_entry['line_range'].split('-')[-1]) if '-' in last_entry['line_range'] else int(last_entry['line_range'])
        
        actual_start_line = first_entry_line
        actual_end_line = last_entry_line
    else:
        actual_start_line = 1
        actual_end_line = 1
    
    return {
        'entries': selected_entries,
        'total_entries': total_entries,
        'total_lines': total_lines,
        'start_entry': start_entry,
        'end_entry': end_entry,
        'actual_start_line': actual_start_line,
        'actual_end_line': actual_end_line
    }


def read_log_file(file_path, lines_per_page=25, start_line=0):
    """Read log file with pagination support (legacy function for backward compatibility)."""
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


def get_log_format_for_file(filename):
    """Get the log format configuration for a specific file."""
    
    # Get file-specific format if configured
    file_formats = get_file_formats()
    format_name = file_formats.get(filename)
    
    # Fall back to default format
    if not format_name:
        format_name = get_default_format()
    
    # Get format configuration
    formats = get_log_formats()
    format_config = formats.get(format_name, {
        'pattern': r'(?P<level>\w+)\s+(?P<timestamp>\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2},\d+)\s+(?P<module>[\w\.]+):\s*(?P<message>.*)',
        'timestamp_format': '%Y-%m-%d %H:%M:%S,%f',
        'description': 'Default Django format'
    })
    
    return format_config


def parse_log_line_with_format(line, format_config):
    """Parse a log line using the provided format configuration."""
    import datetime as dt
    
    pattern = format_config.get('pattern')
    timestamp_format = format_config.get('timestamp_format')
    
    if not pattern:
        return None
        
    try:
        match = re.match(pattern, line.strip())
        if match:
            groups = match.groupdict()
            
            # Parse timestamp if format is provided
            parsed_timestamp = None
            timestamp_str = groups.get('timestamp', '')
            if timestamp_str and timestamp_format:
                try:
                    # Handle milliseconds in Django format
                    if ',%f' in timestamp_format and ',' in timestamp_str:
                        timestamp_str = timestamp_str.replace(',', '.')
                    elif '.%f' in timestamp_format and ',' in timestamp_str:
                        timestamp_str = timestamp_str.replace(',', '.')
                    
                    parsed_timestamp = dt.datetime.strptime(timestamp_str, timestamp_format)
                except ValueError:
                    parsed_timestamp = None
            
            return {
                'level': groups.get('level', '').upper(),
                'timestamp': timestamp_str,
                'parsed_timestamp': parsed_timestamp,
                'module': groups.get('module', groups.get('logger', '')),
                'message': groups.get('message', ''),
                'ip': groups.get('ip', ''),
                'method': groups.get('method', ''),
                'url': groups.get('url', ''),
                'status': groups.get('status', ''),
                'size': groups.get('size', ''),
                'host': groups.get('host', ''),
                'service': groups.get('service', ''),
                'pid': groups.get('pid', ''),
                'tid': groups.get('tid', ''),
                'worker': groups.get('worker', ''),
                'all_groups': groups
            }
    except Exception:
        pass
    
    return None


def format_log_line(line, line_number, filename=None):
    line = line.strip()
    
    # Get format configuration for this file
    if filename:
        format_config = get_log_format_for_file(filename)
    else:
        # Use default format if filename not provided
        format_config = {
            'pattern': r'(?P<level>\w+)\s+(?P<timestamp>\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2},\d+)\s+(?P<module>[\w\.]+):\s*(?P<message>.*)',
            'timestamp_format': '%Y-%m-%d %H:%M:%S,%f',
            'description': 'Default Django format'
        }
    
    # Parse the line using the format
    parsed = parse_log_line_with_format(line, format_config)
    
    if parsed:
        level = parsed['level'] or 'INFO'
        timestamp = parsed['timestamp'] or ''
        raw_module = parsed['module'] or ''  # Keep original module name
        logger_name = raw_module  # Start with raw module name
        message = parsed['message'] or line
        
        # Handle special log formats for logger display
        if parsed.get('method') and parsed.get('url'):
            # Web access log format
            message = f"{parsed['method']} {parsed['url']} - {parsed.get('status', '')} {parsed.get('size', '')}"
            logger_name = parsed.get('ip', '')
        elif parsed.get('service'):
            # Syslog format
            logger_name = f"{parsed.get('host', '')}/{parsed['service']}"
        elif parsed.get('worker'):
            # Celery format
            logger_name = f"celery/{parsed['worker']}"
        
        # Truncate long messages for preview
        max_length = 200
        is_long = len(message) > max_length
        content = message[:max_length] + ('...' if is_long else '')
        
        return {
            'number': line_number,
            'level': level,
            'timestamp': timestamp,
            'parsed_timestamp': parsed.get('parsed_timestamp'),
            'logger': logger_name,
            'module': raw_module,  # Use original parsed module for display
            'content': content,
            'full_content': message,
            'is_long': is_long,
            'is_multiline': False,
            'line_count': 1,
            'line_range': str(line_number),
            'raw_data': parsed.get('all_groups', {})
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
            'parsed_timestamp': None,
            'logger': '',
            'module': '',  # Add module field for template compatibility
            'content': content,
            'full_content': line,
            'is_long': is_long,
            'is_multiline': False,
            'line_count': 1,
            'line_range': str(line_number),
            'raw_data': {}
        }


def process_log_lines_with_multiline(lines, start_line_number, filename=None):
    """Process log lines to detect and group multi-line entries."""
    if not lines:
        return []
    
    # Get format configuration for this file
    if filename:
        format_config = get_log_format_for_file(filename)
    else:
        # Use default format if filename not provided
        format_config = {
            'pattern': r'(?P<level>\w+)\s+(?P<timestamp>\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2},\d+)\s+(?P<module>[\w\.]+):\s*(?P<message>.*)',
            'timestamp_format': '%Y-%m-%d %H:%M:%S,%f',
            'description': 'Default Django format'
        }
    
    # Compile the pattern to detect the start of a new log entry
    try:
        log_start_pattern = re.compile(format_config['pattern'])
    except re.error:
        # Fallback to basic pattern if regex compilation fails
        log_start_pattern = re.compile(r'^(DEBUG|INFO|WARNING|ERROR|CRITICAL|WARN)\s+\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2}')
    
    grouped_entries = []
    current_entry_lines = []
    current_start_line = start_line_number
    
    for i, line in enumerate(lines):
        line_number = start_line_number + i
        
        # Check if this line starts a new log entry
        if log_start_pattern.match(line.strip()):
            # Save the previous entry if it exists
            if current_entry_lines:
                # Format the grouped entry
                full_content = ''.join(current_entry_lines)
                formatted_entry = format_multiline_log_entry(
                    full_content, 
                    current_start_line, 
                    len(current_entry_lines),
                    filename
                )
                grouped_entries.append(formatted_entry)
            
            # Start a new entry
            current_entry_lines = [line]
            current_start_line = line_number
        else:
            # This line is part of the current entry (continuation line)
            if current_entry_lines:
                current_entry_lines.append(line)
            else:
                # Orphan line at the beginning - treat as single line entry
                current_entry_lines = [line]
                current_start_line = line_number
    
    # Don't forget the last entry
    if current_entry_lines:
        full_content = ''.join(current_entry_lines)
        formatted_entry = format_multiline_log_entry(
            full_content, 
            current_start_line, 
            len(current_entry_lines),
            filename
        )
        grouped_entries.append(formatted_entry)
    
    return grouped_entries


def format_multiline_log_entry(content, start_line_number, line_count, filename=None):
    """Format a multi-line log entry."""
    # Parse the first line to get the main log info
    first_line = content.split('\n')[0] if '\n' in content else content
    parsed = format_log_line(first_line, start_line_number, filename)
    
    # Update the content and multi-line info
    parsed['full_content'] = content.strip()
    parsed['content'] = content.strip()
    parsed['is_multiline'] = line_count > 1
    parsed['line_count'] = line_count
    
    # Create line range display
    if line_count > 1:
        parsed['line_range'] = f"{start_line_number}-{start_line_number + line_count - 1}"
    else:
        parsed['line_range'] = str(start_line_number)
    
    # Truncate content for display if it's too long
    max_length = 200
    is_long = len(parsed['content']) > max_length
    if is_long:
        parsed['content'] = parsed['content'][:max_length] + '...'
    parsed['is_long'] = is_long
    
    return parsed
