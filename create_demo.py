#!/usr/bin/env python3
"""
Demo script for Django Admin Log Viewer

This script creates a minimal Django project to demonstrate the log viewer.
"""

import os
import sys
import tempfile
from pathlib import Path


def create_demo_project():
    """Create a minimal Django project to demo the log viewer."""
    
    # Create temporary directory for demo
    demo_dir = Path(tempfile.mkdtemp(prefix='log_viewer_demo_'))
    print(f"Creating demo project in: {demo_dir}")
    
    # Create logs directory and sample log file
    logs_dir = demo_dir / 'logs'
    logs_dir.mkdir()
    
    sample_log_content = """INFO 2025-08-12 10:00:01,123 django.server: "GET /admin/ HTTP/1.1" 200 1024
WARNING 2025-08-12 10:00:02,456 jazzmin.utils: Could not reverse url from auth.user
ERROR 2025-08-12 10:00:03,789 django.request: Internal Server Error: /api/test/
INFO 2025-08-12 10:00:04,012 myapp.views: User logged in: admin
DEBUG 2025-08-12 10:00:05,345 django.db.backends: SELECT * FROM auth_user WHERE username = 'admin'
WARNING 2025-08-12 10:00:06,678 django.security: Suspicious operation: Invalid HTTP_HOST header
CRITICAL 2025-08-12 10:00:07,901 myapp.payments: Payment gateway connection failed
INFO 2025-08-12 10:00:08,234 django.server: "POST /admin/login/ HTTP/1.1" 302 0
ERROR 2025-08-12 10:00:09,567 django.request: ValueError at /api/data/: Invalid data format
DEBUG 2025-08-12 10:00:10,890 myapp.tasks: Background task started: process_emails
"""
    
    log_file = logs_dir / 'django.log'
    log_file.write_text(sample_log_content)
    
    # Create Django project structure
    project_dir = demo_dir / 'logviewer_demo'
    project_dir.mkdir()
    
    # Create manage.py
    manage_py = project_dir / 'manage.py'
    manage_py.write_text(f"""#!/usr/bin/env python
import os
import sys

if __name__ == '__main__':
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'logviewer_demo.settings')
    
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    
    execute_from_command_line(sys.argv)
""")
    
    # Create project package
    package_dir = project_dir / 'logviewer_demo'
    package_dir.mkdir()
    
    # Create __init__.py
    (package_dir / '__init__.py').write_text('')
    
    # Create settings.py
    settings_py = package_dir / 'settings.py'
    settings_py.write_text(f"""
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'demo-secret-key-not-for-production'
DEBUG = True
ALLOWED_HOSTS = ['localhost', '127.0.0.1']

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'log_viewer',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'logviewer_demo.urls'

TEMPLATES = [
    {{
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {{
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        }},
    }},
]

DATABASES = {{
    'default': {{
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }}
}}

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Log viewer configuration
LOG_DIR = r'{logs_dir}'
LOG_VIEWER_FILES = ['django.log']
LOG_VIEWER_FILES_DIR = LOG_DIR
LOG_VIEWER_PAGE_LENGTH = 25
LOG_VIEWER_MAX_READ_LINES = 1000
LOG_VIEWER_FILE_LIST_TITLE = "Demo Log Viewer"
LOGVIEWER_REFRESH_INTERVAL = 5000  # 5 seconds for demo
""")
    
    # Create urls.py
    urls_py = package_dir / 'urls.py'
    urls_py.write_text("""
from django.contrib import admin
from django.urls import path

urlpatterns = [
    path('admin/', admin.site.urls),
]
""")
    
    # Copy log_viewer app to project
    import shutil
    current_dir = Path(__file__).parent
    log_viewer_source = current_dir / 'log_viewer'
    log_viewer_dest = project_dir / 'log_viewer'
    
    if log_viewer_source.exists():
        shutil.copytree(log_viewer_source, log_viewer_dest)
    else:
        print("Warning: log_viewer app not found in current directory")
    
    # Create instructions
    readme = demo_dir / 'DEMO_README.md'
    readme.write_text(f"""# Django Admin Log Viewer Demo

This is a demo project showing the Django Admin Log Viewer in action.

## Setup

1. Navigate to the project directory:
   ```
   cd {project_dir}
   ```

2. Create and activate a virtual environment:
   ```
   python -m venv venv
   venv\\Scripts\\activate  # On Windows
   source venv/bin/activate  # On Unix/Mac
   ```

3. Install Django:
   ```
   pip install Django
   ```

4. Run migrations:
   ```
   python manage.py migrate
   ```

5. Create a superuser:
   ```
   python manage.py createsuperuser
   ```

6. Start the development server:
   ```
   python manage.py runserver
   ```

7. Open your browser and go to:
   - Admin: http://127.0.0.1:8000/admin/
   - Log Viewer: http://127.0.0.1:8000/admin/logs/

## Features Demonstrated

- View log files in Django admin
- Pagination for large files
- Log level filtering (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- Real-time refresh functionality
- Mobile-responsive interface

## Log Files

The demo includes a sample log file at:
{log_file}

You can add more log files to the logs directory and update the LOG_VIEWER_FILES setting in settings.py.
""")
    
    print(f"Demo project created successfully!")
    print(f"Project location: {project_dir}")
    print(f"Log files location: {logs_dir}")
    print(f"Follow the instructions in: {readme}")
    
    return str(project_dir)


if __name__ == '__main__':
    create_demo_project()
