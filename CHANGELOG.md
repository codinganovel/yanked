# Changelog

All notable changes to yanked will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.0.1] - 2025-07-26

### Fixed
- 🐛 **show_info crash**: Fixed crash when viewing info for custom installer packages (inst method)
- 🔧 **File extension flexibility**: Removed hardcoded .sh extension for custom installers (supports any executable)
- 📡 **User agent version**: Updated HTTP user agent to reflect version 2.0

### Technical Details
- Custom installer packages no longer require file_path tracking
- Method-aware status display in package info
- Temporary files for installers now support any file type

## [2.0.0] - 2025-07-26

### Added
- 🚀 **Dual Installation Methods**: Support for both script (`scr`) and custom installer (`inst`) methods
- 🎯 **Method Selection**: Interactive prompts to choose installation method for each package
- 🔄 **Method-Specific Upgrades**: Hash-based updates for scripts, always-run updates for custom installers
- 📦 **Enhanced Package Tracking**: Records installation method for proper upgrade/uninstall handling
- 🧹 **Method-Aware Uninstallation**: Different cleanup behavior based on installation method
- 💡 **Backward Compatibility**: Existing v1.0 installations continue working seamlessly

### Changed
- Interactive installation flow now includes method selection
- Package records include method field for proper handling
- Upgrade behavior adapts based on installation method
- Uninstall warnings for non-tracked custom installer files

### Technical Details
- Custom installers run with full terminal control via subprocess
- Temporary file handling with automatic cleanup
- Process replacement for install scripts vs file copying for simple scripts
- Enhanced error handling for subprocess operations

## [0.3] - 2025-01-17

### Added
- ✨ **Self-updating**: `yanked update` command to update yanked itself to the latest version
- 📊 **Version tracking**: `yanked --version` flag to show current yanked version
- 🔄 **Atomic updates**: Safe self-replacement with automatic backup creation
- 🎯 **Smart detection**: Only updates when new version is actually available
- 🛡️ **Rollback capability**: Automatic restoration from backup if update fails

### Changed
- Updated help text to include new `update` command
- Enhanced error handling for self-update operations

## [0.2] - 2025-01-17

### Added
- 🔄 **Package upgrades**: `yanked upgrade <package>` command for updating individual packages
- 📈 **Bulk updates**: `yanked upgrade` (no arguments) to update all installed packages
- 🔍 **Hash comparison**: Only updates packages when content actually changes
- 📝 **Update tracking**: Records `last_update` timestamp for each package
- 📊 **Upgrade summaries**: Shows count of updated, up-to-date, and failed packages

### Changed
- Enhanced package records to include update timestamps
- Improved user feedback with detailed upgrade progress

## [0.1] - 2025-01-17

### Added
- 📦 **Core package management**: `install`, `list`, `uninstall`, `info` commands
- 🔗 **GitHub integration**: Support for both raw GitHub URLs and repository URLs
- 📋 **Package tracking**: JSON-based records with install dates and file hashes
- 🎨 **Rich UI**: Colored terminal output with clear status messages
- 🔒 **Security**: SHA256 file verification for all installed packages
- 🚪 **Graceful exits**: Type 'quit' or 'exit' at any prompt, or use Ctrl+C
- 🏠 **User-safe installation**: Installs to `~/.local/bin/` by default
- ✅ **Automatic permissions**: Makes downloaded scripts executable
- 🌐 **URL validation**: Checks if URLs are accessible before downloading
- 📊 **Install history**: Track when and from where packages were installed

### Technical Details
- Pure Python implementation using only standard library
- Single-file application for easy distribution
- Cross-platform support (Linux, macOS, WSL)
- Proper error handling with user-friendly messages
- Request headers to avoid GitHub rate limiting