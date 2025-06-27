#!/usr/bin/env python3
"""
yanked - Universal GitHub Package Manager
Install any executable script from GitHub with just a URL and a name.
"""

import argparse
import json
import os
import re
import stat
import subprocess
import sys
import hashlib
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse
from urllib.request import urlopen, Request
from urllib.error import URLError, HTTPError


class Colors:
    """ANSI color codes for terminal output"""
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    END = '\033[0m'


def print_status(message):
    """Print a status message in blue"""
    print(f"{Colors.BLUE}📦 {message}{Colors.END}")


def print_success(message):
    """Print a success message in green"""
    print(f"{Colors.GREEN}✅ {message}{Colors.END}")


def print_error(message):
    """Print an error message in red"""
    print(f"{Colors.RED}❌ {message}{Colors.END}")


def print_warning(message):
    """Print a warning message in yellow"""
    print(f"{Colors.YELLOW}⚠️  {message}{Colors.END}")


class YankedManager:
    def __init__(self):
        self.install_dir = Path.home() / ".local" / "bin"
        self.records_file = self.install_dir / ".yankpacks"  # No extension needed!
        self.install_dir.mkdir(parents=True, exist_ok=True)
        
    def load_records(self):
        """Load the installation records from JSON file"""
        if not self.records_file.exists():
            return {}
        try:
            with open(self.records_file, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            print_error(f"Error reading records: {e}")
            return {}
    
    def save_records(self, records):
        """Save the installation records to JSON file"""
        try:
            with open(self.records_file, 'w') as f:
                json.dump(records, f, indent=2, sort_keys=True)
        except IOError as e:
            print_error(f"Error saving records: {e}")
    
    def check_exit(self, user_input):
        """Check if user wants to exit"""
        if user_input.lower() in ['quit', 'exit']:
            print_warning("Installation cancelled")
            sys.exit(0)
    
    def read_with_exit(self, prompt):
        """Read input with exit option"""
        while True:
            value = input(prompt).strip()
            self.check_exit(value)
            if value:
                return value
            print_error("Please enter a value (or 'quit' to exit)")
    
    def validate_app_name(self, name):
        """Validate app name contains only allowed characters"""
        return bool(re.match(r'^[a-zA-Z0-9_-]+$', name))
    
    def parse_github_url(self, url):
        """Parse GitHub URL and return raw download URL"""
        url = url.strip()
        
        # Handle raw URLs directly
        if 'raw.githubusercontent.com' in url:
            return url, url
        
        # Handle regular GitHub URLs
        if 'github.com' in url:
            # Extract user/repo from URL
            match = re.match(r'https?://github\.com/([^/]+)/([^/]+)/?.*', url)
            if match:
                user, repo = match.groups()
                return url, None  # Will need file path
            
        raise ValueError("Invalid GitHub URL")
    
    def get_raw_url(self, github_url, file_path):
        """Convert GitHub repo URL and file path to raw URL"""
        match = re.match(r'https?://github\.com/([^/]+)/([^/]+)/?.*', github_url)
        if not match:
            raise ValueError("Invalid GitHub URL")
            
        user, repo = match.groups()
        repo = repo.replace('.git', '')  # Remove .git suffix if present
        
        return f"https://raw.githubusercontent.com/{user}/{repo}/main/{file_path}"
    
    def download_file(self, url):
        """Download file from URL and return content"""
        try:
            print_status(f"Downloading from {url}")
            
            # Create request with user agent to avoid blocks
            req = Request(url, headers={
                'User-Agent': 'yanked/1.0 (GitHub Package Manager)'
            })
            
            with urlopen(req, timeout=30) as response:
                if response.status != 200:
                    raise Exception(f"HTTP {response.status}: {response.reason}")
                return response.read()
                
        except (URLError, HTTPError) as e:
            raise Exception(f"Download failed: {e}")
        except Exception as e:
            raise Exception(f"Download failed: {e}")
    
    def calculate_hash(self, content):
        """Calculate SHA256 hash of content"""
        return hashlib.sha256(content).hexdigest()
    
    def install_app(self, app_name, source_url, file_url, content):
        """Install app and update records"""
        app_path = self.install_dir / app_name
        
        # Write file
        with open(app_path, 'wb') as f:
            f.write(content)
        
        # Make executable
        app_path.chmod(app_path.stat().st_mode | stat.S_IEXEC)
        
        # Update records
        records = self.load_records()
        records[app_name] = {
            "source_url": source_url,
            "file_url": file_url,
            "install_date": datetime.now().isoformat(),
            "file_path": str(app_path),
            "file_hash": self.calculate_hash(content)
        }
        self.save_records(records)
        
        print_success(f"{app_name} installed successfully!")
        print(f"Location: {app_path}")
        print(f"Run with: {Colors.CYAN}{app_name}{Colors.END}")
    
    def interactive_install(self):
        """Interactive installation process"""
        print()
        print(f"{Colors.BOLD}🚀 yanked - GitHub Package Manager{Colors.END}")
        print("=" * 35)
        print()
        print_status("Press Ctrl+C or type 'quit'/'exit' at any prompt to exit")
        print()
        
        # Get URL
        print("You can provide either:")
        print("1. A GitHub repository URL (e.g., https://github.com/user/repo)")
        print("2. A raw GitHub file URL (e.g., https://raw.githubusercontent.com/user/repo/main/file.py)")
        print()
        
        source_url = self.read_with_exit("Enter URL: ")
        
        try:
            parsed_url, raw_url = self.parse_github_url(source_url)
        except ValueError as e:
            print_error(str(e))
            return
        
        # If not a raw URL, ask for file path
        if not raw_url:
            print()
            print("Please specify which file to install from the repository.")
            print("Examples: main.py, src/app.py, bin/cli.js, script.sh")
            file_path = self.read_with_exit("Enter the file path: ")
            try:
                raw_url = self.get_raw_url(source_url, file_path)
            except ValueError as e:
                print_error(str(e))
                return
        
        # Get app name
        while True:
            app_name = self.read_with_exit("Enter the name for the installed app: ")
            if self.validate_app_name(app_name):
                break
            print_error("App name must contain only letters, numbers, hyphens, and underscores")
        
        # Check if already installed
        records = self.load_records()
        if app_name in records:
            confirm = input(f"{Colors.YELLOW}⚠️  {app_name} is already installed. Overwrite? (y/N): {Colors.END}")
            if confirm.lower() not in ['y', 'yes']:
                print_warning("Installation cancelled")
                return
        
        # Show summary
        print()
        print("Installation Summary:")
        print(f"Source URL: {source_url}")
        print(f"Download URL: {raw_url}")
        print(f"App name: {app_name}")
        print(f"Install location: {self.install_dir / app_name}")
        print()
        
        confirm = input("Proceed with installation? (y/N): ")
        if confirm.lower() not in ['y', 'yes']:
            print_warning("Installation cancelled")
            return
        
        # Download and install
        try:
            content = self.download_file(raw_url)
            self.install_app(app_name, source_url, raw_url, content)
        except Exception as e:
            print_error(f"Installation failed: {e}")
    
    def list_installed(self):
        """List all installed apps"""
        records = self.load_records()
        
        if not records:
            print("No packages installed yet.")
            print(f"Run '{Colors.CYAN}yanked{Colors.END}' to install your first package!")
            return
        
        print()
        print(f"{Colors.BOLD}📦 Installed Packages{Colors.END}")
        print("=" * 20)
        
        for name, info in sorted(records.items()):
            install_date = datetime.fromisoformat(info['install_date']).strftime('%Y-%m-%d %H:%M')
            print(f"{Colors.CYAN}{name}{Colors.END}")
            print(f"  Source: {info['source_url']}")
            print(f"  Installed: {install_date}")
            print()
    
    def show_info(self, app_name):
        """Show detailed info about an installed app"""
        records = self.load_records()
        
        if app_name not in records:
            print_error(f"Package '{app_name}' is not installed")
            return
        
        info = records[app_name]
        install_date = datetime.fromisoformat(info['install_date']).strftime('%Y-%m-%d %H:%M:%S')
        
        print()
        print(f"{Colors.BOLD}📦 Package Info: {app_name}{Colors.END}")
        print("=" * (15 + len(app_name)))
        print(f"Source URL: {info['source_url']}")
        print(f"Download URL: {info['file_url']}")
        print(f"Install Path: {info['file_path']}")
        print(f"Install Date: {install_date}")
        print(f"File Hash: {info['file_hash'][:16]}...")
        
        # Check if file still exists
        if Path(info['file_path']).exists():
            print(f"Status: {Colors.GREEN}✅ Installed{Colors.END}")
        else:
            print(f"Status: {Colors.RED}❌ Missing (file not found){Colors.END}")
    
    def uninstall_app(self, app_name):
        """Uninstall an app"""
        records = self.load_records()
        
        if app_name not in records:
            print_error(f"Package '{app_name}' is not installed")
            return
        
        info = records[app_name]
        app_path = Path(info['file_path'])
        
        # Confirm uninstallation
        print(f"This will remove: {Colors.CYAN}{app_name}{Colors.END}")
        print(f"Location: {app_path}")
        confirm = input("Are you sure? (y/N): ")
        
        if confirm.lower() not in ['y', 'yes']:
            print_warning("Uninstallation cancelled")
            return
        
        # Remove file if it exists
        if app_path.exists():
            try:
                app_path.unlink()
                print_success(f"Removed {app_path}")
            except OSError as e:
                print_error(f"Failed to remove file: {e}")
                return
        else:
            print_warning(f"File {app_path} was already missing")
        
        # Remove from records
        del records[app_name]
        self.save_records(records)
        
        print_success(f"'{app_name}' uninstalled successfully!")


def setup_exit_handlers():
    """Setup graceful exit handlers"""
    import signal
    
    def signal_handler(sig, frame):
        print()
        print_warning("Installation cancelled")
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)


def main():
    """Main entry point"""
    setup_exit_handlers()
    
    parser = argparse.ArgumentParser(
        description="yanked - Universal GitHub Package Manager",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  yanked                     Interactive installation
  yanked list                List installed packages
  yanked uninstall my-tool   Remove installed package
  yanked info my-tool        Show package details
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Install command (default)
    subparsers.add_parser('install', help='Install a package (default)')
    
    # List command
    subparsers.add_parser('list', help='List installed packages')
    
    # Uninstall command
    uninstall_parser = subparsers.add_parser('uninstall', help='Uninstall a package')
    uninstall_parser.add_argument('package', help='Package name to uninstall')
    
    # Info command
    info_parser = subparsers.add_parser('info', help='Show package information')
    info_parser.add_argument('package', help='Package name to show info for')
    
    args = parser.parse_args()
    
    manager = YankedManager()
    
    # Default to install if no command specified
    if not args.command or args.command == 'install':
        manager.interactive_install()
    elif args.command == 'list':
        manager.list_installed()
    elif args.command == 'uninstall':
        manager.uninstall_app(args.package)
    elif args.command == 'info':
        manager.show_info(args.package)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print()
        print_warning("Operation cancelled")
        sys.exit(0)
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        sys.exit(1)