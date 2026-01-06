# Readloom v0.2.0

**Release Date**: November 11, 2025

## What's New

This version focuses on enhanced author management with improved OpenLibrary integration and better enrichment strategies.

## Key Features

- **Enhanced Authors Tab** - Better author information display
- **OpenLibrary Integration** - Improved book and author metadata
- **Hybrid Enrichment** - OpenLibrary first, then Groq AI fallback
- **Unicode Fixes** - Windows compatibility improvements

## Documentation

- **[Features Overview](FEATURES.md)** - What's new in v0.2.0
- **[Author Enrichment](AUTHOR_ENRICHMENT_HYBRID.md)** - Hybrid enrichment strategy
- **[Author Sync](AUTHOR_SYNC_COMPLETE.md)** - Complete author synchronization
- **[Data Sources](AUTHOR_DATA_SOURCES.md)** - Comparison of AI vs fixed sources

## Upgrading from v0.1.9

1. Update your installation
2. Restart Readloom
3. No database migration required
4. Author enrichment will work automatically

## Known Issues

- See [Known Issues](../../troubleshooting/KNOWN_ISSUES.md)

## Technical Details

- OpenLibrary API integration for author metadata
- Groq AI fallback for missing biographies
- Unicode encoding fixes for Windows
- Enhanced error handling and logging

For more information, see the main [Documentation](../../INDEX.md).
