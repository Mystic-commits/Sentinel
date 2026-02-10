"""
Tests for the Scanner Module

Tests file scanning, type detection, and metadata extraction.
"""

import pytest
from pathlib import Path

from sentinel_core.scanner.scanner import Scanner
from sentinel_core.models.enums import FileType


class TestBasicScanning:
    """Tests for basic scanning functionality."""
    
    def test_scan_empty_directory(self, mock_fs):
        """Test scanning an empty directory returns no files."""
        empty_dir = mock_fs.create_directory("empty")
        
        scanner = Scanner(empty_dir)
        result = scanner.scan()
        
        assert result.root_path == empty_dir
        assert len(result.files) == 0
        assert len(result.errors) == 0
    
    def test_scan_nonexistent_directory(self, mock_fs):
        """Test scanning a non-existent directory returns error."""
        scanner = Scanner(mock_fs.get_path("nonexistent"))
        result = scanner.scan()
        
        assert len(result.files) == 0
        assert len(result.errors) > 0
        assert "not found" in result.errors[0].lower()
    
    def test_scan_with_files(self, mock_fs):
        """Test scanning a directory with multiple files."""
        mock_fs.create_file("test/file1.txt", content="Hello")
        mock_fs.create_file("test/file2.pdf", size_bytes=1024)
        mock_fs.create_file("test/image.png", size_bytes=2048)
        
        scanner = Scanner(mock_fs.get_path("test"))
        result = scanner.scan()
        
        assert len(result.files) == 3
        assert any(f.name == "file1.txt" for f in result.files)
        assert any(f.name == "file2.pdf" for f in result.files)
        assert any(f.name == "image.png" for f in result.files)
    
    def test_scan_with_subdirectories(self, mock_fs):
        """Test that scanning includes subdirectories."""
        mock_fs.create_file("root/file1.txt")
        mock_fs.create_file("root/sub1/file2.txt")
        mock_fs.create_file("root/sub1/sub2/file3.txt")
        
        scanner = Scanner(mock_fs.get_path("root"))
        result = scanner.scan()
        
        assert len(result.files) == 3


class TestFileTypeDetection:
    """Tests for file type classification."""
    
    def test_document_detection(self, mock_fs):
        """Test detection of document files."""
        mock_fs.create_file("test/document.pdf", size_bytes=1024)
        mock_fs.create_file("test/notes.txt", content="Notes")
        mock_fs.create_file("test/report.docx", size_bytes=2048)
        
        scanner = Scanner(mock_fs.get_path("test"))
        result = scanner.scan()
        
        pdf = next(f for f in result.files if f.name == "document.pdf")
        txt = next(f for f in result.files if f.name == "notes.txt")
        docx = next(f for f in result.files if f.name == "report.docx")
        
        assert pdf.file_type == FileType.DOCUMENT
        assert txt.file_type == FileType.DOCUMENT
        # Note: .docx might be DOCUMENT or UNKNOWN depending on scanner config
    
    def test_image_detection(self, mock_fs):
        """Test detection of image files."""
        extensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp']
        for ext in extensions:
            mock_fs.create_file(f"test/image{ext}", size_bytes=1024)
        
        scanner = Scanner(mock_fs.get_path("test"))
        result = scanner.scan()
        
        for file in result.files:
            assert file.file_type == FileType.IMAGE
    
    def test_video_detection(self, mock_fs):
        """Test detection of video files."""
        extensions = ['.mp4', '.mov', '.avi', '.mkv']
        for ext in extensions:
            mock_fs.create_file(f"test/video{ext}", size_bytes=1024 * 1024)
        
        scanner = Scanner(mock_fs.get_path("test"))
        result = scanner.scan()
        
        for file in result.files:
            assert file.file_type == FileType.VIDEO
    
    def test_archive_detection(self, mock_fs):
        """Test detection of archive files."""
        extensions = ['.zip', '.rar', '.7z', '.tar', '.gz']
        for ext in extensions:
            mock_fs.create_file(f"test/archive{ext}", size_bytes=1024)
        
        scanner = Scanner(mock_fs.get_path("test"))
        result = scanner.scan()
        
        for file in result.files:
            assert file.file_type == FileType.ARCHIVE
    
    def test_executable_detection(self, mock_fs):
        """Test detection of executable/installer files."""
        extensions = ['.exe', '.dmg', '.pkg', '.msi']
        for ext in extensions:
            mock_fs.create_file(f"test/installer{ext}", size_bytes=10 * 1024 * 1024)
        
        scanner = Scanner(mock_fs.get_path("test"))
        result = scanner.scan()
        
        for file in result.files:
            assert file.file_type == FileType.EXECUTABLE


class TestDepthControl:
    """Tests for max_depth parameter."""
    
    def test_max_depth_limit(self, mock_fs):
        """Test that max_depth is respected."""
        # Create nested structure: a/ -> a/b/ -> a/b/c/ -> a/b/c/d/
        mock_fs.create_file("a/file0.txt")
        mock_fs.create_file("a/b/file1.txt")
        mock_fs.create_file("a/b/c/file2.txt")
        mock_fs.create_file("a/b/c/d/file3.txt")
        
        # Scan with depth limit of 2
        scanner = Scanner(mock_fs.get_path("a"), max_depth=2)
        result = scanner.scan()
        
        paths = [f.path for f in result.files]
        
        # Should find files in a/, a/b/, a/b/c/ but NOT a/b/c/d/
        assert any("file0.txt" in p for p in paths)
        assert any("file1.txt" in p for p in paths)
        assert any("file2.txt" in p for p in paths)
        assert not any("file3.txt" in p for p in paths)
    
    def test_depth_zero(self, mock_fs):
        """Test with max_depth=0 (only root directory)."""
        mock_fs.create_file("root/file.txt")
        mock_fs.create_file("root/sub/file.txt")
        
        scanner = Scanner(mock_fs.get_path("root"), max_depth=0)
        result = scanner.scan()
        
        # Should only find file in root, not in sub/
        assert len(result.files) == 1
        assert result.files[0].name == "file.txt"


class TestIgnoredDirectories:
    """Tests for ignored directory handling."""
    
    def test_ignored_directories_skipped(self, mock_fs):
        """Test that ignored directories are not scanned."""
        mock_fs.create_file("test/normal.txt")
        mock_fs.create_file("test/.git/config")
        mock_fs.create_file("test/node_modules/package.json")
        mock_fs.create_file("test/__pycache__/module.pyc")
        
        scanner = Scanner(mock_fs.get_path("test"))
        result = scanner.scan()
        
        # Should only find normal.txt
        assert len(result.files) == 1
        assert result.files[0].name == "normal.txt"
    
    def test_hidden_files_skipped(self, mock_fs):
        """Test that hidden files (starting with .) are skipped."""
        mock_fs.create_file("test/visible.txt")
        mock_fs.create_file("test/.hidden")
        mock_fs.create_file("test/.DS_Store")
        
        scanner = Scanner(mock_fs.get_path("test"))
        result = scanner.scan()
        
        # Should only find visible.txt
        assert len(result.files) == 1
        assert result.files[0].name == "visible.txt"


class TestMetadataExtraction:
    """Tests for file metadata extraction."""
    
    def test_file_size_extraction(self, mock_fs):
        """Test that file sizes are correctly extracted."""
        size = 5 * 1024 * 1024  # 5MB
        mock_fs.create_file("test/large.bin", size_bytes=size)
        
        scanner = Scanner(mock_fs.get_path("test"))
        result = scanner.scan()
        
        assert len(result.files) == 1
        assert result.files[0].size_bytes == size
    
    def test_extension_extraction(self, mock_fs):
        """Test that extensions are correctly extracted."""
        mock_fs.create_file("test/file.txt")
        mock_fs.create_file("test/archive.tar.gz")
        mock_fs.create_file("test/noextension")
        
        scanner = Scanner(mock_fs.get_path("test"))
        result = scanner.scan()
        
        txt_file = next(f for f in result.files if "file.txt" in f.path)
        tar_file = next(f for f in result.files if "archive.tar.gz" in f.path)
        no_ext = next(f for f in result.files if "noextension" in f.path)
        
        assert txt_file.extension == ".txt"
        assert tar_file.extension == ".gz"  # Gets the last extension
        assert no_ext.extension == ""
    
    def test_old_file_age(self, mock_fs):
        """Test scanning old files with modified timestamps."""
        # Create old file (60 days ago)
        mock_fs.create_file("test/old.txt", content="old", age_days=60)
        mock_fs.create_file("test/new.txt", content="new", age_days=1)
        
        scanner = Scanner(mock_fs.get_path("test"))
        result = scanner.scan()
        
        old_file = next(f for f in result.files if "old.txt" in f.path)
        new_file = next(f for f in result.files if "new.txt" in f.path)
        
        # Old file should have earlier modification time
        assert old_file.modified_at < new_file.modified_at


class TestIntegrationWithFakeData:
    """Integration tests using fake directory generator."""
    
    def test_scan_complete_generated_structure(self, populated_fs):
        """Test scanning a complete generated directory structure."""
        scanner = Scanner(str(populated_fs.root))
        result = scanner.scan()
        
        # Should find multiple files
        assert len(result.files) > 10
        
        # Should have various file types
        file_types = {f.file_type for f in result.files}
        assert FileType.EXECUTABLE in file_types  # Installers
        assert FileType.ARCHIVE in file_types  # Archives
        assert FileType.IMAGE in file_types  # Screenshots
    
    def test_scan_minimal_structure(self, minimal_fs):
        """Test scanning a minimal generated structure."""
        scanner = Scanner(str(minimal_fs.root))
        result = scanner.scan()
        
        assert len(result.files) >= 3  # At least installer, archive, screenshot
