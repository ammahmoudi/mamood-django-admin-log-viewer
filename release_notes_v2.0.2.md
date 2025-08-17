## What's New in v2.0.2

### Fixed
- Fixed dropdown styling issues where text was not fully visible due to improper height settings
- Fixed log message parsing to display only the message content without timestamp, level, and module metadata
- Fixed JavaScript errors in multiline log modal display by implementing data attribute approach instead of inline onclick
- Fixed pagination issues by implementing proper multiline-aware pagination using entries instead of lines
- Fixed "Next" button not appearing in pagination due to incorrect pagination calculation

### Changed
- Updated views to use multiline-aware log reading functions for proper pagination
- Improved JavaScript security by replacing inline onclick handlers with data attributes
- Enhanced CSS styling for all select elements with consistent height and text visibility

### Technical Improvements
- Refactored `format_multiline_log_entry` function to properly separate message content from metadata
- Updated view pagination logic to work with log entries rather than raw lines
- Added comprehensive dropdown styling with dark theme support
- Implemented safer JavaScript modal handling to prevent syntax errors from special characters
- Added Future Features section to README with cloud storage and advanced integrations

**Full Changelog**: https://github.com/ammahmoudi/mamood-django-admin-log-viewer/compare/v2.0.1...v2.0.2
