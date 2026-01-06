# Technical Documentation

In-depth technical documentation for developers and advanced users.

## Architecture & Design

- **[Codebase Structure](CODEBASE_STRUCTURE.md)** - Overview of the modular architecture
- **[Database Schema](DATABASE.md)** - Database structure and relationships
- **[UI Structure](UI_STRUCTURE.md)** - Frontend organization

## API & Integration

- **[API Reference](API.md)** - Complete API documentation
- **[Image Proxy](IMAGE_PROXY.md)** - Image handling and caching
- **[Direct Execution](DIRECT_EXECUTION.md)** - Running without Docker

## Performance & Optimization

- **[Performance Tips](PERFORMANCE_TIPS.md)** - Optimize for large collections
- **[Smart Caching System](SMART_CACHING_SYSTEM.md)** - Volume detection caching

## Implementation Details

- **[Implementation Notes](IMPLEMENTATION_NOTES.md)** - Technical implementation details
- **[Database and README Structure](DATABASE_AND_README_STRUCTURE.md)** - Folder organization and metadata files

## For Developers

- See [Development](../development/) section for contribution guidelines
- See [Troubleshooting](../troubleshooting/) for debugging help

## Quick Reference

- **Main Entry Point**: `Readloom.py`
- **Backend**: `backend/` (modular packages)
- **Frontend**: `frontend/` (Flask routes and templates)
- **Database**: SQLite in `data/` folder
- **Configuration**: `data/ai_providers_config.json`
