#!/usr/bin/env python3
import re

# Test the Django log regex pattern
pattern = r'(?P<level>\w+)\s+(?P<timestamp>\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2},\d+)\s+(?P<module>[\w\.]+):\s*(?P<message>.*)'

test_lines = [
    "WARNING 2025-08-11 11:32:25,079 jazzmin.utils: Could not reverse url from auth.user",
    "INFO 2025-08-12 10:00:01,123 django.server: \"GET /admin/ HTTP/1.1\" 200 1024",
    "ERROR 2025-08-12 10:00:03,789 django.request: Internal Server Error: /api/test/",
    "DEBUG 2025-08-12 10:00:05,345 django.db.backends: SELECT * FROM auth_user WHERE username = \"admin\"",
    "CRITICAL 2025-08-12 10:00:07,901 myapp.payments: Payment gateway connection failed"
]

print("Testing Django log regex pattern:")
print("Pattern:", pattern)
print("-" * 80)

for line in test_lines:
    print(f"Testing line: {line}")
    match = re.match(pattern, line.strip())
    if match:
        groups = match.groupdict()
        print(f"  ✅ MATCH:")
        for key, value in groups.items():
            print(f"    {key}: '{value}'")
        
        # Check if message is clean (no duplicated info)
        message = groups.get('message', '')
        original_level = groups.get('level', '')
        original_timestamp = groups.get('timestamp', '')
        original_module = groups.get('module', '')
        
        if original_level.lower() in message.lower():
            print(f"  ⚠️  WARNING: Level '{original_level}' found in message")
        if original_timestamp in message:
            print(f"  ⚠️  WARNING: Timestamp '{original_timestamp}' found in message")
        if original_module in message:
            print(f"  ⚠️  WARNING: Module '{original_module}' found in message")
            
    else:
        print(f"  ❌ NO MATCH")
    print()
