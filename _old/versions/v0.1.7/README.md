# Readloom v0.1.7

**Release Date**: October 25, 2025

## What's New

This version focuses on UI consistency improvements, book details page redesign, and manga volume detection fixes.

## Key Features

- **Book Details Redesign** - Full-width layout matching manga pages
- **UI Consistency** - Consistent button styling across pages
- **Volume Detection Fix** - Three-tier detection system working properly
- **E-book Management** - Improved file handling and organization
- **Notification System** - In-app toast notifications

## Documentation

- **[Features Overview](FEATURES.md)** - What's new in v0.1.7
- **[Volume Detection Fix](VOLUME_DETECTION_FIX.md)** - How volume detection works
- **[Volume Fix Summary](VOLUME_FIX_FINAL_SUMMARY.md)** - Complete fix details
- **[Dashboard UI Changes](DASHBOARD_UI_CHANGES.md)** - Dashboard improvements

## Upgrading from v0.1.6

1. Update your installation
2. Restart Readloom
3. Volumes will be automatically detected and cached
4. No data loss or migration required

## Features

- **Book Page Redesign**: Full-width layout with consistent buttons
- **Volume Detection**: Three-tier system (static DB → web scraping → estimation)
- **E-book Management**: Improved file scanning and organization
- **Notification System**: Toast notifications instead of browser popups
- **Dashboard**: Updated stat cards (Manga Series, Books, Authors)

## Technical Details

- Manga volume cache table for performance
- Three-tier volume detection system
- Improved file permission handling
- Better error messages and logging

## Known Issues

- See [Known Issues](../../troubleshooting/KNOWN_ISSUES.md)

For more information, see the main [Documentation](../../INDEX.md).
