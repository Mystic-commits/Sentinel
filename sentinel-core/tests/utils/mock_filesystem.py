"""
Mock Filesystem for Testing

Provides a temporary filesystem that's automatically cleaned up after tests.
"""

import tempfile
import shutil
import os
from pathlib import Path
from typing import Optional
from datetime import datetime, timedelta


class MockFilesystem:
    """
    Creates a temporary filesystem for isolated testing.
    
    All files and directories are created within a temporary directory
    that is automatically cleaned up when done.
    
    Example:
        >>> with MockFilesystem() as fs:
        ...     fs.create_file("test/file.txt", content="Hello")
        ...     fs.create_directory("test/subdir")
        ...     # Files exist within the temporary directory
        ... # Automatically cleaned up here
    """
    
    def __init__(self):
        """Initialize a new mock filesystem."""
        self.temp_dir = tempfile.mkdtemp(prefix="sentinel_test_")
        self.root = Path(self.temp_dir)
    
    def create_file(
        self, 
        path: str, 
        content: str = "", 
        size_bytes: Optional[int] = None,
        age_days: Optional[int] = None
    ) -> str:
        """
        Create a file in the mock filesystem.
        
        Args:
            path: Relative path within the mock filesystem
            content: Text content for the file (default: empty)
            size_bytes: If provided, create file with this exact size
            age_days: If provided, set modification time to N days ago
            
        Returns:
            Absolute path to the created file
            
        Example:
            >>> fs.create_file("docs/test.txt", content="Hello")
            >>> fs.create_file("large.bin", size_bytes=1024*1024)  # 1MB
            >>> fs.create_file("old.txt", age_days=60)  # 60 days old
        """
        full_path = self.root / path
        full_path.parent.mkdir(parents=True, exist_ok=True)
        
        if size_bytes is not None:
            # Create file with specific size
            with open(full_path, 'wb') as f:
                f.write(b'0' * size_bytes)
        else:
            # Create text file with content
            full_path.write_text(content, encoding='utf-8')
        
        # Set modification time if specified
        if age_days is not None:
            past_time = datetime.now() - timedelta(days=age_days)
            timestamp = past_time.timestamp()
            os.utime(full_path, (timestamp, timestamp))
        
        return str(full_path)
    
    def create_directory(self, path: str) -> str:
        """
        Create a directory in the mock filesystem.
        
        Args:
            path: Relative path within the mock filesystem
            
        Returns:
            Absolute path to the created directory
        """
        full_path = self.root / path
        full_path.mkdir(parents=True, exist_ok=True)
        return str(full_path)
    
    def get_path(self, path: str) -> str:
        """
        Get the absolute path for a relative path in the mock filesystem.
        
        Args:
            path: Relative path within the mock filesystem
            
        Returns:
            Absolute path
        """
        return str(self.root / path)
    
    def exists(self, path: str) -> bool:
        """
        Check if a path exists in the mock filesystem.
        
        Args:
            path: Relative path within the mock filesystem
            
        Returns:
            True if path exists
        """
        return (self.root / path).exists()
    
    def cleanup(self):
        """Remove the temporary filesystem and all contents."""
        if self.root.exists():
            shutil.rmtree(self.temp_dir)
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, *args):
        """Context manager exit - cleanup temporary files."""
        self.cleanup()
    
    def __str__(self) -> str:
        """String representation."""
        return f"MockFilesystem(root={self.root})"
