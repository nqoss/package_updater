# Debian Package Updater & Cleaner

A Python-based tool for managing Debian package updates and system cleanup. Combines multiple package management commands into a simple, unified interface.

## Features

- **APT Package Management**: Check for and install available updates
- **Flatpak Support**: Update Flatpak applications (if installed)
- **System Cleanup**: Remove orphaned packages and clean cache
- **Safe Operations**: Dry-run mode to preview changes before applying
- **Comprehensive Checking**: Check-only mode to see what needs updating

## Installation

```bash
git clone https://github.com/yourusername/debian-package-updater.git
cd debian-package-updater
chmod +x package_updater.py
```

## Usage

### Basic Update & Clean
```bash
python3 package_updater.py
```

### Preview Changes (Dry Run)
```bash
python3 package_updater.py --dry-run
```

### Check Only (No Changes)
```bash
python3 package_updater.py --check-only
```

### Verbose Output
```bash
python3 package_updater.py --verbose
```

## Requirements

- Python 3.6+
- Debian-based Linux distribution
- sudo privileges for package management
- apt package manager
- flatpak (optional, for Flatpak support)

## What It Does

1. **Updates package lists** from repositories
2. **Checks for APT updates** and displays available packages
3. **Checks for Flatpak updates** (if installed)
4. **Identifies orphaned packages** that can be safely removed
5. **Applies updates** to both APT and Flatpak packages
6. **Cleans up** orphaned packages and cache

## Safety Features

- Dry-run mode shows what would be changed without making actual modifications
- Clear output showing exactly what packages will be updated or removed
- Error handling for failed commands
- No silent operations - everything is clearly reported

## License

MIT License
