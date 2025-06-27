# yanked 🔨

A universal package manager for GitHub-hosted scripts and tools. Install, track, and manage any executable script from GitHub with just a URL and a name.

## What it does

- 📥 Downloads any script from GitHub (raw URLs or repo URLs)
- 🏠 Installs to `~/.local/bin/` with your chosen name
- 📋 **Tracks all installed packages** with install dates and sources
- 🗑️ **Easy uninstall** - remove packages with one command
- 🛣️ Automatically adds to PATH
- ✅ Makes it executable and ready to use
- 🎨 **Rich colored output** with clear status messages
- 🔄 Works on Linux, macOS, and WSL

## Quick Start

### Install yanked

Copy and paste this command:

```bash
curl -fsSL https://raw.githubusercontent.com/codinganovel/yanked/refs/heads/main/yanked.py -o ~/.local/bin/yanked && chmod +x ~/.local/bin/yanked && echo "✅ yanked installed! Run: yanked"
```

### Use it to install packages

```bash
yanked                     # Interactive installation
yanked list                # Show installed packages  
yanked uninstall my-tool   # Remove a package
yanked info my-tool        # Show package details
```

## Commands

### Install packages
```bash
yanked install    # Interactive mode (same as just 'yanked')
```

When prompted:
- **Enter URL:** Paste the GitHub URL (repo or raw file)
- **Enter file path:** If repo URL, specify which file to install
- **Enter app name:** Choose what to call it
- **Confirm:** Press `y` to install

### Manage installed packages
```bash
yanked list                # List all installed packages
yanked uninstall my-tool   # Remove package and cleanup records
yanked info my-tool        # Show detailed package information
```

## Examples

### Installing from a raw URL
```bash
yanked
# Enter URL: https://raw.githubusercontent.com/user/repo/main/script.py
# Enter app name: my-script
```

### Installing from a repository URL
```bash
yanked
# Enter URL: https://github.com/user/awesome-tool
# Enter file path: src/cli.py
# Enter app name: awesome
```

### Package management
```bash
# See what you've installed
yanked list

# Get details about a package
yanked info my-script

# Remove a package
yanked uninstall my-script
```

## Supported URL Types

✅ **Raw GitHub URLs**
```
https://raw.githubusercontent.com/user/repo/main/file.py
https://raw.githubusercontent.com/user/repo/refs/heads/main/file.py
```

✅ **GitHub Repository URLs**
```
https://github.com/user/repo
```
(You'll be prompted for the specific file path)

## Features

- 🔍 **URL validation** - Checks if URLs are accessible before downloading
- 📦 **Package tracking** - Keeps records of all installed packages
- 🗑️ **Easy uninstall** - Remove packages with full cleanup
- ⏱️ **Install history** - See when and from where you installed packages
- 🎨 **Colored output** - Beautiful terminal UI with status indicators
- ❌ **Smart error handling** - Clear error messages and recovery
- 🔒 **File verification** - SHA256 checksums for installed files
- 🚪 **Graceful exits** - Type 'quit' or 'exit' at any prompt, or use Ctrl+C

## Package Records

yanked keeps track of everything you install in `~/.local/bin/.yankpacks`:

```json
{
  "my-tool": {
    "source_url": "https://github.com/user/repo",
    "file_url": "https://raw.githubusercontent.com/.../tool.py",
    "install_date": "2025-06-26T10:30:00",
    "file_path": "/home/user/.local/bin/my-tool",
    "file_hash": "sha256:abc123..."
  }
}
```

## Requirements

- Python 3.6+ (pre-installed on most systems)
- Internet connection
- No external dependencies - uses only Python standard library

## For Project Maintainers

Add this to your project's README:

# 📦 Installation

1. **Get yanked** (one time setup):
   ```bash
   curl -fsSL https://raw.githubusercontent.com/codinganovel/yanked/refs/heads/main/yanked -o ~/.local/bin/yanked && chmod +x ~/.local/bin/yanked && echo "✅ yanked installed! Run: yanked"
   ```

2. **Install this project:**
   ```bash
   yanked
   ```
   - **URL:** `https://raw.githubusercontent.com/YOUR_USERNAME/YOUR_REPO/main/YOUR_FILE.py`
   - **Name:** `your-app-name`

3. **Done!** Run with: `your-app-name`

Users can later remove it with: `yanked uninstall your-app-name`


## Troubleshooting

**"Command not found" after installation:**
```bash
# Reload shell configuration
source ~/.bashrc  # or ~/.zshrc for zsh
# Or open a new terminal
```

**Installation fails:**
- Check internet connection
- Verify the GitHub URL is correct and public
- Make sure the file exists at the specified path

**Permission errors:**
- Don't use `sudo` with yanked
- It installs to your user directory (`~/.local/bin/`)

**Python not found:**
- yanked requires Python 3.6+
- Check with: `python3 --version`

## Uninstalling

**Remove any installed package:**
```bash
yanked uninstall package-name
```

**Remove yanked itself:**
```bash
rm ~/.local/bin/yanked ~/.local/bin/.yankpacks
```
---
## Advanced: System-Wide Installation

⚠️ **By default, yanked installs to `~/.local/bin/` for your user only** - this is recommended and safe.

### For System-Wide Access

**⚠️ Security Warning:** Installing random scripts system-wide is risky - they get elevated permissions and affect all users.

**Recommended approach:**
1. Install normally with yanked first (test it works)
2. Copy to system location if needed:
```bash
yanked  # Install normally first
# Test it works: your-tool --help
sudo cp ~/.local/bin/your-tool /usr/local/bin/  # Copy to system
```

### When System Installation Makes Sense
✅ **Good reasons:** Multi-user servers, system services, CI/CD, containers  
❌ **Avoid for:** Personal dev tools, experimental scripts, untrusted sources

### Quick Commands
```bash
# Check if tool is system or user installed
which your-tool

# Remove system-installed tool
sudo rm /usr/local/bin/tool-name
```

**💡 Tip:** User installation (`~/.local/bin/`) works for 99% of use cases and is much safer.

## Contributing

1. Fork this repository
2. Create a feature branch  
3. Submit a pull request

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Why yanked?

Because installing scripts from GitHub should be simple AND manageable. No package managers, no complex setup - just a URL and a name. But unlike basic installers, yanked remembers what you installed and lets you clean up easily.

Perfect for:
- 🛠️ Development tools
- 📝 CLI utilities  
- 🤖 Automation scripts
- 🎯 Single-file applications

---

**yanked 🔨** - Making GitHub installations simple AND manageable, one script at a time.