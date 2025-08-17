## What's New in v2.0.4

### Fixed

- **CSS Conflicts**: Fixed CSS class conflicts with Django admin's built-in `.module` class
- Renamed conflicting CSS classes to more unique names to prevent styling issues with Django admin interface

### Changed

- `.module` class renamed to `.log-module` 
- `.module-name` class renamed to `.log-module-name`
- `.no-module` class renamed to `.no-log-module`
- Updated CSS, HTML templates, and JavaScript files with new class names
- Improved CSS specificity to avoid conflicts with Django admin styling

### Technical Improvements

- Enhanced CSS class naming convention for better compatibility with Django admin
- Maintained all existing functionality while resolving styling conflicts
- Updated both light and dark theme styles with new class names
- Ensured consistent styling across all log viewer components

### Why This Update?

This release addresses CSS conflicts that could occur when the log viewer's `.module` class interfered with Django admin's built-in `.module` class, potentially causing styling issues in the admin interface. The new class names are more specific and unique to the log viewer, ensuring better compatibility.

**Full Changelog**: https://github.com/ammahmoudi/mamood-django-admin-log-viewer/compare/v2.0.3...v2.0.4
