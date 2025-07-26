#!/usr/bin/env python3
"""
Comprehensive test suite for yanked v2.0.1
Tests both scr and inst installation methods, URL parsing, package tracking, and more.
"""

import unittest
import tempfile
import json
import os
import stat
import shutil
from pathlib import Path
from unittest.mock import patch, mock_open, MagicMock
import sys

# Import the module under test
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from yanked import YankedManager, Colors


class TestYankedManager(unittest.TestCase):
    """Test suite for YankedManager class"""
    
    def setUp(self):
        """Set up test fixtures"""
        # Create temporary directory for testing
        self.test_dir = tempfile.mkdtemp()
        self.test_install_dir = Path(self.test_dir) / ".local" / "bin"
        self.test_records_file = self.test_install_dir / ".yankpacks"
        
        # Create YankedManager instance with test directories
        self.manager = YankedManager()
        self.manager.install_dir = self.test_install_dir
        self.manager.records_file = self.test_records_file
        
        # Ensure test directory exists
        self.test_install_dir.mkdir(parents=True, exist_ok=True)
    
    def tearDown(self):
        """Clean up test fixtures"""
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    def test_init(self):
        """Test YankedManager initialization"""
        manager = YankedManager()
        self.assertTrue(manager.install_dir.exists())
        self.assertEqual(manager.records_file.name, ".yankpacks")
    
    def test_load_records_empty(self):
        """Test loading records when file doesn't exist"""
        records = self.manager.load_records()
        self.assertEqual(records, {})
    
    def test_save_and_load_records(self):
        """Test saving and loading package records"""
        test_records = {
            "test-app": {
                "method": "scr",
                "source_url": "https://github.com/user/repo",
                "file_url": "https://raw.githubusercontent.com/user/repo/main/script.py",
                "install_date": "2025-07-26T10:30:00",
                "file_path": str(self.test_install_dir / "test-app"),
                "file_hash": "abc123"
            }
        }
        
        self.manager.save_records(test_records)
        loaded_records = self.manager.load_records()
        self.assertEqual(loaded_records, test_records)
    
    def test_validate_app_name(self):
        """Test app name validation"""
        # Valid names
        self.assertTrue(self.manager.validate_app_name("valid-name"))
        self.assertTrue(self.manager.validate_app_name("valid_name"))
        self.assertTrue(self.manager.validate_app_name("ValidName123"))
        
        # Invalid names
        self.assertFalse(self.manager.validate_app_name("invalid name"))  # space
        self.assertFalse(self.manager.validate_app_name("invalid@name"))  # special char
        self.assertFalse(self.manager.validate_app_name(""))  # empty
    
    def test_parse_github_url_raw(self):
        """Test parsing raw GitHub URLs"""
        raw_url = "https://raw.githubusercontent.com/user/repo/main/script.py"
        source_url, parsed_raw_url = self.manager.parse_github_url(raw_url)
        
        self.assertEqual(source_url, raw_url)
        self.assertEqual(parsed_raw_url, raw_url)
    
    def test_parse_github_url_repo(self):
        """Test parsing repository GitHub URLs"""
        repo_url = "https://github.com/user/repo"
        source_url, parsed_raw_url = self.manager.parse_github_url(repo_url)
        
        self.assertEqual(source_url, repo_url)
        self.assertIsNone(parsed_raw_url)  # Should need file path
    
    def test_parse_github_url_invalid(self):
        """Test parsing invalid URLs"""
        with self.assertRaises(ValueError):
            self.manager.parse_github_url("https://invalid-url.com")
    
    def test_get_raw_url(self):
        """Test converting repo URL to raw URL"""
        repo_url = "https://github.com/user/repo"
        file_path = "src/script.py"
        
        raw_url = self.manager.get_raw_url(repo_url, file_path)
        expected = "https://raw.githubusercontent.com/user/repo/main/src/script.py"
        
        self.assertEqual(raw_url, expected)
    
    def test_get_raw_url_with_git_suffix(self):
        """Test converting repo URL with .git suffix"""
        repo_url = "https://github.com/user/repo.git"
        file_path = "script.py"
        
        raw_url = self.manager.get_raw_url(repo_url, file_path)
        expected = "https://raw.githubusercontent.com/user/repo/main/script.py"
        
        self.assertEqual(raw_url, expected)
    
    def test_calculate_hash(self):
        """Test SHA256 hash calculation"""
        content = b"test content"
        hash_result = self.manager.calculate_hash(content)
        
        # Should be a 64-character hex string
        self.assertEqual(len(hash_result), 64)
        self.assertTrue(all(c in '0123456789abcdef' for c in hash_result))
    
    @patch('yanked.urlopen')
    def test_download_file(self, mock_urlopen):
        """Test file downloading"""
        test_content = b"#!/usr/bin/env python3\nprint('Hello World')"
        
        # Mock the HTTP response
        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.read.return_value = test_content
        mock_response.__enter__.return_value = mock_response
        mock_urlopen.return_value = mock_response
        
        result = self.manager.download_file("https://example.com/script.py")
        self.assertEqual(result, test_content)
    
    def test_install_app_scr_method(self):
        """Test installing app with scr method"""
        app_name = "test-script"
        source_url = "https://github.com/user/repo"
        file_url = "https://raw.githubusercontent.com/user/repo/main/script.py"
        content = b"#!/usr/bin/env python3\nprint('Hello')"
        method = "scr"
        
        self.manager.install_app(app_name, source_url, file_url, content, method)
        
        # Check file was created
        app_path = self.test_install_dir / app_name
        self.assertTrue(app_path.exists())
        
        # Check file content
        with open(app_path, 'rb') as f:
            self.assertEqual(f.read(), content)
        
        # Check file is executable
        self.assertTrue(os.access(app_path, os.X_OK))
        
        # Check records were updated
        records = self.manager.load_records()
        self.assertIn(app_name, records)
        self.assertEqual(records[app_name]["method"], "scr")
        self.assertEqual(records[app_name]["source_url"], source_url)
        self.assertEqual(records[app_name]["file_url"], file_url)
        self.assertIn("file_path", records[app_name])
        self.assertIn("file_hash", records[app_name])
    
    @patch('yanked.subprocess.run')
    @patch('yanked.tempfile.NamedTemporaryFile')
    @patch('yanked.os.chmod')
    @patch('yanked.os.unlink')
    def test_install_app_inst_method(self, mock_unlink, mock_chmod, mock_tempfile, mock_subprocess):
        """Test installing app with inst method"""
        app_name = "test-installer"
        source_url = "https://github.com/user/complex-software"
        file_url = "https://raw.githubusercontent.com/user/complex-software/main/install.sh"
        content = b"#!/bin/bash\necho 'Installing...'"
        method = "inst"
        
        # Mock temporary file
        mock_temp_file = MagicMock()
        mock_temp_file.name = "/tmp/test_installer"
        mock_temp_file.__enter__.return_value = mock_temp_file
        mock_tempfile.return_value = mock_temp_file
        
        # Mock successful subprocess run
        mock_subprocess.return_value.returncode = 0
        
        self.manager.install_app(app_name, source_url, file_url, content, method)
        
        # Check subprocess was called with temp file
        mock_subprocess.assert_called_once()
        
        # Check records were updated (no file_path for inst method)
        records = self.manager.load_records()
        self.assertIn(app_name, records)
        self.assertEqual(records[app_name]["method"], "inst")
        self.assertEqual(records[app_name]["source_url"], source_url)
        self.assertEqual(records[app_name]["file_url"], file_url)
        self.assertNotIn("file_path", records[app_name])  # No file tracking for inst
        self.assertIn("file_hash", records[app_name])
        
        # Check temp file was cleaned up
        mock_unlink.assert_called_once()
    
    def test_show_info_scr_method(self):
        """Test showing info for scr method package"""
        # Setup test record
        app_name = "test-app"
        app_path = self.test_install_dir / app_name
        app_path.write_text("test content")
        
        records = {
            app_name: {
                "method": "scr",
                "source_url": "https://github.com/user/repo",
                "file_url": "https://raw.githubusercontent.com/user/repo/main/script.py",
                "install_date": "2025-07-26T10:30:00",
                "file_path": str(app_path),
                "file_hash": "abc123"
            }
        }
        self.manager.save_records(records)
        
        # Capture output
        with patch('builtins.print') as mock_print:
            self.manager.show_info(app_name)
            
            # Check that info was printed (look for key elements)
            printed_output = " ".join([str(call.args[0]) for call in mock_print.call_args_list])
            self.assertIn("Package Info", printed_output)
            self.assertIn("scr", printed_output)
            self.assertIn("Install Path", printed_output)
    
    def test_show_info_inst_method(self):
        """Test showing info for inst method package (no file_path)"""
        app_name = "test-installer"
        records = {
            app_name: {
                "method": "inst",
                "source_url": "https://github.com/user/complex-software",
                "file_url": "https://raw.githubusercontent.com/user/complex-software/main/install.sh",
                "install_date": "2025-07-26T10:30:00",
                "file_hash": "def456"
            }
        }
        self.manager.save_records(records)
        
        # This should not crash (previously would crash on missing file_path)
        with patch('builtins.print') as mock_print:
            self.manager.show_info(app_name)
            
            # Check that info was printed without crashing
            printed_output = " ".join([str(call.args[0]) for call in mock_print.call_args_list])
            self.assertIn("Package Info", printed_output)
            self.assertIn("inst", printed_output)
            self.assertIn("Custom installer", printed_output)
    
    def test_uninstall_app_scr_method(self):
        """Test uninstalling scr method package"""
        app_name = "test-app"
        app_path = self.test_install_dir / app_name
        app_path.write_text("test content")
        
        records = {
            app_name: {
                "method": "scr",
                "source_url": "https://github.com/user/repo",
                "file_url": "https://raw.githubusercontent.com/user/repo/main/script.py",
                "install_date": "2025-07-26T10:30:00",
                "file_path": str(app_path),
                "file_hash": "abc123"
            }
        }
        self.manager.save_records(records)
        
        # Mock user confirmation
        with patch('builtins.input', return_value='y'):
            self.manager.uninstall_app(app_name)
        
        # Check file was removed
        self.assertFalse(app_path.exists())
        
        # Check record was removed
        records = self.manager.load_records()
        self.assertNotIn(app_name, records)
    
    def test_uninstall_app_inst_method(self):
        """Test uninstalling inst method package"""
        app_name = "test-installer"
        records = {
            app_name: {
                "method": "inst",
                "source_url": "https://github.com/user/complex-software",
                "file_url": "https://raw.githubusercontent.com/user/complex-software/main/install.sh",
                "install_date": "2025-07-26T10:30:00",
                "file_hash": "def456"
            }
        }
        self.manager.save_records(records)
        
        # Mock user confirmation
        with patch('builtins.input', return_value='y'):
            self.manager.uninstall_app(app_name)
        
        # Check record was removed (no file to remove for inst method)
        records = self.manager.load_records()
        self.assertNotIn(app_name, records)
    
    @patch('yanked.urlopen')
    def test_upgrade_app_scr_no_change(self, mock_urlopen):
        """Test upgrading scr method package when no changes"""
        app_name = "test-app"
        content = b"test content"
        file_hash = self.manager.calculate_hash(content)
        
        records = {
            app_name: {
                "method": "scr",
                "source_url": "https://github.com/user/repo",
                "file_url": "https://raw.githubusercontent.com/user/repo/main/script.py",
                "install_date": "2025-07-26T10:30:00",
                "file_path": str(self.test_install_dir / app_name),
                "file_hash": file_hash
            }
        }
        self.manager.save_records(records)
        
        # Mock download returning same content
        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.read.return_value = content
        mock_response.__enter__.return_value = mock_response
        mock_urlopen.return_value = mock_response
        
        result = self.manager.upgrade_app(app_name)
        self.assertFalse(result)  # No upgrade needed
    
    @patch('yanked.urlopen')
    def test_upgrade_app_scr_with_change(self, mock_urlopen):
        """Test upgrading scr method package when content changed"""
        app_name = "test-app"
        old_content = b"old content"
        new_content = b"new content"
        
        # Create app file
        app_path = self.test_install_dir / app_name
        app_path.write_bytes(old_content)
        
        records = {
            app_name: {
                "method": "scr",
                "source_url": "https://github.com/user/repo",
                "file_url": "https://raw.githubusercontent.com/user/repo/main/script.py",
                "install_date": "2025-07-26T10:30:00",
                "file_path": str(app_path),
                "file_hash": self.manager.calculate_hash(old_content)
            }
        }
        self.manager.save_records(records)
        
        # Mock download returning new content
        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.read.return_value = new_content
        mock_response.__enter__.return_value = mock_response
        mock_urlopen.return_value = mock_response
        
        result = self.manager.upgrade_app(app_name)
        self.assertTrue(result)  # Upgrade performed
        
        # Check file was updated
        self.assertEqual(app_path.read_bytes(), new_content)
        
        # Check hash was updated in records
        updated_records = self.manager.load_records()
        new_hash = self.manager.calculate_hash(new_content)
        self.assertEqual(updated_records[app_name]["file_hash"], new_hash)


class TestColorCodes(unittest.TestCase):
    """Test color code constants"""
    
    def test_color_constants(self):
        """Test that color constants are defined"""
        self.assertTrue(hasattr(Colors, 'RED'))
        self.assertTrue(hasattr(Colors, 'GREEN'))
        self.assertTrue(hasattr(Colors, 'BLUE'))
        self.assertTrue(hasattr(Colors, 'END'))
        
        # Check they're strings
        self.assertIsInstance(Colors.RED, str)
        self.assertIsInstance(Colors.GREEN, str)
        self.assertIsInstance(Colors.BLUE, str)
        self.assertIsInstance(Colors.END, str)


if __name__ == '__main__':
    # Run tests with verbose output
    unittest.main(argv=[''], verbosity=2, exit=False)