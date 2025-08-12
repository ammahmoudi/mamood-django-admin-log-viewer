#!/usr/bin/env python3

import os
import sys
import django

# Add the project directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'myproject'))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from log_viewer.utils import read_log_file_multiline_aware

def test_multiline_pagination():
    """Test multi-line aware pagination to ensure multi-line logs are not split across pages."""
    
    log_file_path = r'd:\projects\django-admin-log-viewer\myproject\logs\celery_beat.log'
    filename = 'celery_beat.log'
    entries_per_page = 25
    
    print("Testing multi-line aware pagination...")
    print("=" * 60)
    
    # Test page 1
    print("\n📄 PAGE 1:")
    page1_data = read_log_file_multiline_aware(log_file_path, entries_per_page, 0, filename)
    print(f"  Total entries: {page1_data['total_entries']}")
    print(f"  Total lines: {page1_data['total_lines']}")
    print(f"  Page 1 entries: {len(page1_data['entries'])}")
    print(f"  Covers lines: {page1_data['actual_start_line']} - {page1_data['actual_end_line']}")
    
    # Show last few entries of page 1
    print("  Last entry on page 1:")
    last_entry = page1_data['entries'][-1]
    print(f"    Line: {last_entry['line_range']}")
    print(f"    Level: {last_entry['level']}")
    print(f"    Module: {last_entry['module']}")
    print(f"    Multi-line: {last_entry.get('is_multiline', False)}")
    if last_entry.get('is_multiline'):
        print(f"    Line count: {last_entry.get('line_count', 1)}")
    print(f"    Message: {last_entry['content'][:100]}...")
    
    # Test page 2
    print("\n📄 PAGE 2:")
    page2_data = read_log_file_multiline_aware(log_file_path, entries_per_page, entries_per_page, filename)
    print(f"  Page 2 entries: {len(page2_data['entries'])}")
    print(f"  Covers lines: {page2_data['actual_start_line']} - {page2_data['actual_end_line']}")
    
    # Show first few entries of page 2
    print("  First entry on page 2:")
    first_entry = page2_data['entries'][0]
    print(f"    Line: {first_entry['line_range']}")
    print(f"    Level: {first_entry['level']}")
    print(f"    Module: {first_entry['module']}")
    print(f"    Multi-line: {first_entry.get('is_multiline', False)}")
    if first_entry.get('is_multiline'):
        print(f"    Line count: {first_entry.get('line_count', 1)}")
    print(f"    Message: {first_entry['content'][:100]}...")
    
    # Check for the problematic multi-line log (lines 48-133)
    print("\n🔍 LOOKING FOR THE PROBLEMATIC MULTI-LINE LOG:")
    for page_num in range(1, 5):  # Check first few pages
        start_entry = (page_num - 1) * entries_per_page
        page_data = read_log_file_multiline_aware(log_file_path, entries_per_page, start_entry, filename)
        
        for i, entry in enumerate(page_data['entries']):
            entry_line = entry['line_range']
            # Check if this entry covers line 48 (start of the problematic log)
            if '-' in entry_line:
                start_line, end_line = map(int, entry_line.split('-'))
                if start_line <= 48 <= end_line:
                    print(f"  ✅ Found multi-line entry covering line 48 on page {page_num}:")
                    print(f"    Entry line range: {entry_line}")
                    print(f"    Entry {i+1} of {len(page_data['entries'])} on page {page_num}")
                    print(f"    Page covers lines: {page_data['actual_start_line']} - {page_data['actual_end_line']}")
                    print(f"    Multi-line: {entry.get('is_multiline', False)}")
                    print(f"    Line count: {entry.get('line_count', 1)}")
                    print(f"    Level: {entry['level']}")
                    print(f"    Module: {entry['module']}")
                    print(f"    Message: {entry['content'][:150]}...")
                    return
            elif int(entry_line) == 48:
                print(f"  ✅ Found single-line entry at line 48 on page {page_num}:")
                print(f"    Entry line: {entry_line}")
                print(f"    Entry {i+1} of {len(page_data['entries'])} on page {page_num}")
                print(f"    Page covers lines: {page_data['actual_start_line']} - {page_data['actual_end_line']}")
                return
    
    print("  ❌ Could not find entry covering line 48 in first few pages!")

if __name__ == '__main__':
    test_multiline_pagination()
