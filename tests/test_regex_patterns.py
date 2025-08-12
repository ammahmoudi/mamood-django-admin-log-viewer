#!/usr/bin/env python
"""Test script to debug regex pattern matching."""

import re

def test_regex_patterns():
    """Test various log format regex patterns."""
    # Test the celery_beat regex pattern
    pattern = r'(?P<level>\w+)\s+(?P<timestamp>\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2},\d+)\s+(?P<module>[\w\.]+):\s*(?P<message>.*)'

    test_line = "CRITICAL 2025-08-11 13:15:21,757 celery.beat: beat raised exception <class 'django.db.utils.ProgrammingError'>: ProgrammingError('relation \"django_celery_beat_crontabschedule\" does not exist\\nLINE 1: ...django_celery_beat_crontabschedule\".\"minute\" FROM \"django_ce...\\n                                                             ^\\n')"

    print("Testing regex pattern:")
    print("Pattern:", pattern)
    print("Test line:", test_line[:100] + "...")
    print()

    compiled_pattern = re.compile(pattern)
    match = compiled_pattern.match(test_line)

    if match:
        print("✅ Match found!")
        groups = match.groupdict()
        for key, value in groups.items():
            print(f"  {key}: '{value[:50]}{'...' if len(value) > 50 else ''}'")
        return True
    else:
        print("❌ No match found!")
        
        # Try a simpler pattern to see what works
        simple_patterns = [
            r'(\w+)\s+(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2},\d+)\s+([\w\.]+):\s*(.*)',
            r'(\w+)\s+(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2},\d+)\s+([^:]+):\s*(.*)',
            r'(\w+)\s+(.+?)\s+([^:]+):\s*(.*)',
        ]
        
        for i, simple_pattern in enumerate(simple_patterns):
            print(f"\nTrying simpler pattern {i+1}: {simple_pattern}")
            simple_match = re.match(simple_pattern, test_line)
            if simple_match:
                print("  ✅ Match found!")
                groups = simple_match.groups()
                print(f"  Groups: {groups[:3]}... (truncated)")
            else:
                print("  ❌ No match")
        return False

def test_multiple_formats():
    """Test multiple log format patterns."""
    test_cases = [
        {
            'name': 'Django Default',
            'pattern': r'(?P<level>\w+)\s+(?P<timestamp>\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2},\d+)\s+(?P<module>[\w\.]+):\s*(?P<message>.*)',
            'line': 'INFO 2025-08-11 13:00:00,017 django.request: GET /admin/ 200'
        },
        {
            'name': 'Celery Beat',
            'pattern': r'(?P<level>\w+)\s+(?P<timestamp>\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2},\d+)\s+(?P<module>[\w\.]+):\s*(?P<message>.*)',
            'line': 'CRITICAL 2025-08-11 13:15:21,757 celery.beat: beat raised exception'
        },
        {
            'name': 'Simple Format',
            'pattern': r'(?P<level>\w+):\s*(?P<message>.*)',
            'line': 'ERROR: Something went wrong'
        }
    ]
    
    print("\n" + "="*60)
    print("Testing multiple log formats:")
    print("="*60)
    
    for test_case in test_cases:
        print(f"\nTesting {test_case['name']}:")
        print(f"Line: {test_case['line']}")
        
        match = re.match(test_case['pattern'], test_case['line'])
        if match:
            print("✅ Pattern matches!")
            groups = match.groupdict()
            for key, value in groups.items():
                if value:  # Only show non-empty groups
                    print(f"  {key}: '{value}'")
        else:
            print("❌ Pattern does not match")

if __name__ == "__main__":
    test_regex_patterns()
    test_multiple_formats()
