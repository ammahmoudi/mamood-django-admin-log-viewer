#!/usr/bin/env python3
import re

# Test with some problematic lines that might not match
pattern = r'(?P<level>\w+)\s+(?P<timestamp>\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2},\d+)\s+(?P<module>[\w\.]+):\s*(?P<message>.*)'

# Test lines that might be problematic
test_lines = [
    "WARNING 2025-08-11 11:32:25,079 jazzmin.utils: Could not reverse url from auth.user",  # Should work
    "Traceback (most recent call last):",  # Stack trace line - won't match
    "  File \"/path/to/file.py\", line 42, in function_name",  # Stack trace line - won't match
    "    raise ValueError('Something went wrong')",  # Stack trace line - won't match
    "ValueError: Something went wrong",  # Exception line - won't match
    "2025-08-12 10:00:01 [ERROR] Something happened",  # Different format - won't match
    "ERROR: This is a simple error message",  # Different format - won't match
    ""  # Empty line
]

print("Testing lines to see which ones don't match the pattern:")
print("-" * 80)

for line in test_lines:
    if not line.strip():
        continue
        
    print(f"Testing: {line}")
    match = re.match(pattern, line.strip())
    if match:
        groups = match.groupdict()
        print(f"  ✅ MATCHES - Message: '{groups.get('message', '')}'")
    else:
        print(f"  ❌ NO MATCH - Will use full line as message: '{line}'")
    print()
