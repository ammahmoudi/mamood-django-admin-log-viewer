#!/usr/bin/env python
"""Test script to verify multi-line aware pagination."""

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
        SECRET_KEY='test-key-for-pagination-testing',
        INSTALLED_APPS=[
            'django_admin_log_viewer',
        ],
        LOG_VIEWER_FILES=['celery_beat.log'],
        LOG_VIEWER_FILES_DIR=PROJECT_ROOT / 'myproject' / 'logs',
        LOG_VIEWER_PAGE_LENGTH=25,
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
from django_admin_log_viewer.utils import read_log_file_multiline_aware

def test_pagination():
    """Test multi-line aware pagination."""
    log_file_path = PROJECT_ROOT / 'myproject' / 'logs' / 'celery_beat.log'
    
    print(f"Testing pagination with: {log_file_path}")
    print(f"File exists: {log_file_path.exists()}")
    
    if not log_file_path.exists():
        print("ERROR: Test log file not found!")
        return
    
    print("\n" + "="*60)
    print("PAGINATION TEST - Multi-line Aware")
    print("="*60)
    
    # Test pagination for multiple pages
    entries_per_page = 25
    pages_to_test = [1, 2, 3]
    
    for page in pages_to_test:
        start_entry = (page - 1) * entries_per_page
        
        print(f"\n📄 PAGE {page} (entries {start_entry + 1}-{start_entry + entries_per_page}):")
        print("-" * 40)
        
        # Get page data
        page_data = read_log_file_multiline_aware(
            str(log_file_path), 
            entries_per_page, 
            start_entry,
            'celery_beat.log'
        )
        
        print(f"Entries on this page: {len(page_data['entries'])}")
        print(f"Total entries in file: {page_data['total_entries']}")
        print(f"Total lines in file: {page_data['total_lines']}")
        print(f"This page covers lines: {page_data['actual_start_line']}-{page_data['actual_end_line']}")
        
        # Show first few and last few entries on this page
        entries = page_data['entries']
        
        if entries:
            print(f"\nFirst entry on page:")
            first = entries[0]
            print(f"  Line range: {first['line_range']}")
            print(f"  Level: {first['level']}")
            print(f"  Multi-line: {first['is_multiline']}")
            print(f"  Content: {first['content'][:80]}...")
            
            if len(entries) > 1:
                print(f"\nLast entry on page:")
                last = entries[-1]
                print(f"  Line range: {last['line_range']}")
                print(f"  Level: {last['level']}")
                print(f"  Multi-line: {last['is_multiline']}")
                print(f"  Content: {last['content'][:80]}...")
            
            # Look for the big multi-line entry (around lines 48-133)
            big_multiline = None
            for entry in entries:
                if entry.get('is_multiline') and entry.get('line_count', 0) > 50:
                    big_multiline = entry
                    break
            
            if big_multiline:
                print(f"\n🔍 FOUND BIG MULTI-LINE ENTRY:")
                print(f"  Line range: {big_multiline['line_range']}")
                print(f"  Level: {big_multiline['level']}")
                print(f"  Line count: {big_multiline['line_count']}")
                print(f"  Module: {big_multiline.get('module', 'unknown')}")
                print(f"  Content preview: {big_multiline['content'][:100]}...")
        
        print(f"\n📊 Page {page} Summary:")
        multiline_count = sum(1 for entry in entries if entry.get('is_multiline'))
        print(f"  - Single-line entries: {len(entries) - multiline_count}")
        print(f"  - Multi-line entries: {multiline_count}")
        if entries:
            total_lines_in_page = sum(entry.get('line_count', 1) for entry in entries)
            print(f"  - Total lines covered: {total_lines_in_page}")

def test_specific_multiline_entry():
    """Test the specific problematic multi-line entry."""
    log_file_path = PROJECT_ROOT / 'myproject' / 'logs' / 'celery_beat.log'
    
    print("\n" + "="*60)
    print("SPECIFIC MULTI-LINE ENTRY TEST")
    print("="*60)
    
    # Find the page that contains the big multi-line entry (around line 48)
    entries_per_page = 25
    
    # Test different starting points to find the multi-line entry
    for start_entry in [20, 22, 23, 24, 25]:
        page_data = read_log_file_multiline_aware(
            str(log_file_path), 
            entries_per_page, 
            start_entry,
            'celery_beat.log'
        )
        
        # Look for multi-line entries with high line count
        for entry in page_data['entries']:
            if entry.get('is_multiline') and entry.get('line_count', 0) > 50:
                print(f"\n🎯 FOUND THE BIG STACK TRACE (starting from entry {start_entry + 1}):")
                print(f"   Line range: {entry['line_range']}")
                print(f"   Level: {entry['level']}")
                print(f"   Timestamp: {entry.get('timestamp', 'unknown')}")
                print(f"   Module: {entry.get('module', 'unknown')}")
                print(f"   Line count: {entry['line_count']}")
                print(f"   Is long: {entry.get('is_long', False)}")
                print(f"   Content preview: {entry['content'][:150]}...")
                
                # Verify the line range
                line_parts = entry['line_range'].split('-')
                if len(line_parts) == 2:
                    start_line, end_line = map(int, line_parts)
                    expected_count = end_line - start_line + 1
                    print(f"   ✅ Line count verification: {entry['line_count']} == {expected_count} ✓" if entry['line_count'] == expected_count else f"   ❌ Line count mismatch!")
                
                return True
    
    print("❌ Could not find the big multi-line entry!")
    return False

if __name__ == "__main__":
    test_pagination()
    test_specific_multiline_entry()
