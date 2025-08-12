#!/usr/bin/env python
"""Test script to debug multi-line log processing."""

import os
import sys
import django
from pathlib import Path

# Get the project root directory
PROJECT_ROOT = Path(__file__).parent.parent

# Add the project root to the path
sys.path.insert(0, str(PROJECT_ROOT))

# Configure Django settings
if not django.conf.settings.configured:
    django.conf.settings.configure(
        DEBUG=True,
        SECRET_KEY='test-key-for-debugging',
        INSTALLED_APPS=[
            'log_viewer',
        ],
        LOG_VIEWER_FILES=['celery_beat.log'],
        LOG_VIEWER_FILES_DIR=PROJECT_ROOT / 'myproject' / 'logs',
        LOG_VIEWER_FORMATS={
            'celery_beat': {
                'pattern': r'(?P<level>\w+)\s+(?P<timestamp>\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2},\d+)\s+(?P<module>[\w\.]+):\s*(?P<message>.*)',
                'timestamp_format': '%Y-%m-%d %H:%M:%S,%f',
                'description': 'Celery Beat format'
            },
        },
        LOG_VIEWER_FILE_FORMATS={
            'celery_beat.log': 'celery_beat',
        }
    )

django.setup()

# Import after Django is configured
from log_viewer.utils import process_log_lines_with_multiline, read_log_file

def test_multiline_processing():
    """Test the multi-line processing with the celery_beat.log file."""
    log_file_path = PROJECT_ROOT / 'myproject' / 'logs' / 'celery_beat.log'
    
    print(f"Testing multi-line processing with: {log_file_path}")
    print(f"File exists: {log_file_path.exists()}")
    
    if not log_file_path.exists():
        print("ERROR: Test log file not found!")
        return
    
    # Read lines 40-140 to capture the multi-line entry
    log_data = read_log_file(str(log_file_path), 100, 40)
    print(f"Read {len(log_data['lines'])} lines from log file")
    
    # Process with multi-line support
    formatted_lines = process_log_lines_with_multiline(
        log_data['lines'], 
        41,  # Start from line 41 (1-based)
        'celery_beat.log'
    )
    
    print(f"\nProcessed into {len(formatted_lines)} log entries:")
    
    for i, entry in enumerate(formatted_lines):
        print(f"\n--- Entry {i+1} ---")
        print(f"Line range: {entry.get('line_range', 'unknown')}")
        print(f"Level: {entry.get('level', 'unknown')}")
        print(f"Timestamp: {entry.get('timestamp', 'unknown')}")
        print(f"Module: {entry.get('module', 'unknown')}")
        print(f"Is multiline: {entry.get('is_multiline', False)}")
        print(f"Line count: {entry.get('line_count', 1)}")
        print(f"Content preview: {entry.get('content', '')[:100]}...")
        if entry.get('is_long'):
            print("(Content truncated)")
        print("-" * 50)

if __name__ == "__main__":
    test_multiline_processing()
