#!/usr/bin/env python
import os
import sys
import django

# Add the project path
sys.path.insert(0, 'd:\\projects\\django-admin-log-viewer')
sys.path.insert(0, 'd:\\projects\\django-admin-log-viewer\\myproject')

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

# Now test the function
from mamood_django_admin_log_viewer.utils import get_log_files
import json

print("Testing get_log_files() function...")
print("=" * 50)

try:
    log_files = get_log_files()
    print(f"Found {len(log_files)} log file groups:")
    print()
    
    for i, log_file in enumerate(log_files, 1):
        print(f"{i}. {log_file['name']}")
        print(f"   Type: {log_file['type']}")
        print(f"   Path: {log_file['path']}")
        
        if log_file['type'] == 'rotational_group':
            print(f"   File count: {log_file['file_count']}")
            print(f"   Rotational files:")
            for j, rot_file in enumerate(log_file['rotational_files'], 1):
                print(f"      {j}. {rot_file['name']} (index: {rot_file['rotation_index']}, current: {rot_file['is_current']})")
        print()
        
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
