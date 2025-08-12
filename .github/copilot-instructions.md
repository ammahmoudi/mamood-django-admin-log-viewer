<!-- Use this file to provide workspace-specific custom instructions to Copilot. For more details, visit https://code.visualstudio.com/docs/copilot/copilot-customization#_use-a-githubcopilotinstructionsmd-file -->

# Django Admin Log Viewer Project Instructions

This is a Django app that provides a web interface to view log files directly in the Django admin panel.

## Key Components

1. **Utils Module**: Contains utility functions for reading and parsing log files
2. **Admin Integration**: Custom admin views that integrate with Django admin
3. **Templates**: HTML templates for displaying log files and log content
4. **Static Files**: CSS and JavaScript for styling and interactive features
5. **Views**: Django views for handling HTTP requests

## Development Guidelines

- Follow Django best practices and conventions
- Ensure all code is compatible with Django 3.2+
- Use semantic HTML and accessible design patterns
- Implement proper error handling for file operations
- Make the interface responsive and user-friendly
- Use proper Django template inheritance and static file handling
- Follow Python PEP 8 style guidelines
- Write comprehensive tests for all functionality

## Features

- View multiple log files in Django admin
- Pagination for large log files
- Real-time log refresh with AJAX
- Filter by log levels (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- Responsive design
- Configurable through Django settings
- No database dependencies (reads files directly)

## Security Considerations

- Only allow staff users to access log files
- Validate file paths to prevent directory traversal
- Handle file reading errors gracefully
- Limit the number of lines read to prevent memory issues
