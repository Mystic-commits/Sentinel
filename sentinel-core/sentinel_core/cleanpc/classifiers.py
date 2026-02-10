"""
File Classification Heuristics

Intelligent detection of file types and categories for cleanup.
"""

import hashlib
from dataclasses import dataclass
from typing import List, Dict, Optional, Tuple
from datetime import datetime
from pathlib import Path

from sentinel_core.models.filesystem import FileMetadata
from sentinel_core.models.enums import FileType


@dataclass
class FileClassification:
    """
    Classification result for a single file.
    
    Attributes:
        file: Original file metadata
        is_installer: Whether file is an installer
        is_archive: Whether file is an archive
        is_large_video: Whether file is a large video (> 100MB)
        video_size_mb: Size of video in MB
        is_screenshot: Whether file appears to be a screenshot
        is_duplicate: Whether file is a duplicate of another
        duplicate_of: Path to the original file if duplicate
        suggested_action: Recommended action (move, delete, etc.)
        suggested_target: Target path for move operations
        age_days: Age of file in days
    """
    file: FileMetadata
    is_installer: bool = False
    is_archive: bool = False
    is_large_video: bool = False
    video_size_mb: int = 0
    is_screenshot: bool = False
    is_duplicate: bool = False
    duplicate_of: Optional[str] = None
    suggested_action: Optional[str] = None
    suggested_target: Optional[str] = None
    age_days: int = 0


class FileClassifier:
    """
    Classifies files based on heuristics for cleanup and organization.
    """
    
    # File extension sets
    INSTALLER_EXTENSIONS = {'.dmg', '.pkg', '.exe', '.msi', '.app'}
    ARCHIVE_EXTENSIONS = {'.zip', '.rar', '.7z', '.tar', '.gz', '.bz2', '.tar.gz', '.tgz'}
    VIDEO_EXTENSIONS = {'.mp4', '.mov', '.avi', '.mkv', '.webm', '.flv', '.m4v'}
    
    # Screenshot patterns
    SCREENSHOT_PATTERNS = [
        'screenshot',
        'screen shot',
        'screen_shot',
        'scr_',
        'capture',
        'img_',  # Common phone pattern
    ]
    
    # Thresholds
    INSTALLER_AGE_THRESHOLD_DAYS = 30
    OLD_ARCHIVE_THRESHOLD_DAYS = 730  # 2 years
    LARGE_VIDEO_THRESHOLD_BYTES = 100 * 1024 * 1024  # 100MB
    HASH_SIZE_LIMIT_BYTES = 100 * 1024 * 1024  # Don't hash files > 100MB
    
    def __init__(self):
        """Initialize the file classifier."""
        self._hash_cache: Dict[str, str] = {}
    
    def classify_all(self, files: List[FileMetadata]) -> List[FileClassification]:
        """
        Classify all files in the list.
        
        Args:
            files: List of file metadata to classify
            
        Returns:
            List of file classifications
        """
        classifications = []
        
        # Build hash map for duplicate detection
        hash_map = self._build_hash_map(files)
        
        for file in files:
            classification = self._classify_file(file, hash_map)
            classifications.append(classification)
        
        return classifications
    
    def _classify_file(
        self, 
        file: FileMetadata, 
        hash_map: Dict[str, List[FileMetadata]]
    ) -> FileClassification:
        """
        Classify a single file.
        
        Args:
            file: File metadata
            hash_map: Map of file hashes to file lists (for duplicates)
            
        Returns:
            File classification
        """
        age_days = (datetime.now() - file.modified_at).days
        
        classification = FileClassification(
            file=file,
            age_days=age_days
        )
        
        # Check each classification (order matters for priority)
        
        # 1. Check if installer
        if self._is_installer(file, age_days):
            classification.is_installer = True
            classification.suggested_action = "delete"
            classification.suggested_target = "trash"
            return classification
        
        # 2. Check if archive
        if self._is_archive(file):
            classification.is_archive = True
            classification.suggested_action = "move"
            year = file.modified_at.year
            classification.suggested_target = f"~/Archives/{year}/"
            
            # Suggest delete for very old archives in Downloads
            if age_days > self.OLD_ARCHIVE_THRESHOLD_DAYS:
                parent_dir = Path(file.path).parent.name.lower()
                if parent_dir == 'downloads':
                    classification.suggested_action = "delete"
                    classification.suggested_target = "trash"
            
            return classification
        
        # 3. Check if large video
        if self._is_large_video(file):
            classification.is_large_video = True
            classification.video_size_mb = file.size_bytes // (1024 * 1024)
            classification.suggested_action = "move"
            year = file.modified_at.year
            classification.suggested_target = f"~/Videos/{year}/"
            return classification
        
        # 4. Check if screenshot
        if self._is_screenshot(file):
            classification.is_screenshot = True
            classification.suggested_action = "move"
            year = file.created_at.year
            classification.suggested_target = f"~/Pictures/Screenshots/{year}/"
            return classification
        
        # 5. Check if duplicate
        file_hash = self._hash_cache.get(file.path)
        if file_hash and file_hash in hash_map:
            duplicates = hash_map[file_hash]
            if len(duplicates) > 1:
                # Keep the newest file, mark others as duplicates
                newest = max(duplicates, key=lambda f: f.modified_at)
                if file.path != newest.path:
                    classification.is_duplicate = True
                    classification.duplicate_of = newest.path
                    classification.suggested_action = "delete"
                    classification.suggested_target = "trash"
                    return classification
        
        return classification
    
    def _is_installer(self, file: FileMetadata, age_days: int) -> bool:
        """
        Detect installer files.
        
        Criteria:
        - Has installer extension (.dmg, .exe, .msi, etc.)
        - Older than 30 days
        - Located in Downloads or Desktop
        
        Args:
            file: File metadata
            age_days: Age of file in days
            
        Returns:
            True if file is an old installer
        """
        # Check extension
        if file.extension.lower() not in self.INSTALLER_EXTENSIONS:
            return False
        
        # Check age
        if age_days < self.INSTALLER_AGE_THRESHOLD_DAYS:
            return False
        
        # Check location (Downloads or Desktop)
        parent_dir = Path(file.path).parent.name.lower()
        if parent_dir not in ['downloads', 'desktop']:
            return False
        
        return True
    
    def _is_archive(self, file: FileMetadata) -> bool:
        """
        Detect archive files.
        
        Args:
            file: File metadata
            
        Returns:
            True if file is an archive
        """
        return file.extension.lower() in self.ARCHIVE_EXTENSIONS
    
    def _is_large_video(self, file: FileMetadata) -> bool:
        """
        Detect large video files (> 100MB).
        
        Args:
            file: File metadata
            
        Returns:
            True if file is a large video
        """
        if file.extension.lower() not in self.VIDEO_EXTENSIONS:
            return False
        
        return file.size_bytes > self.LARGE_VIDEO_THRESHOLD_BYTES
    
    def _is_screenshot(self, file: FileMetadata) -> bool:
        """
        Detect screenshots.
        
        Heuristics:
        - Filename contains "screenshot", "screen shot", etc.
        - OR is an image in Downloads/Desktop created recently
        
        Args:
            file: File metadata
            
        Returns:
            True if file appears to be a screenshot
        """
        name_lower = file.name.lower()
        
        # Check filename patterns
        for pattern in self.SCREENSHOT_PATTERNS:
            if pattern in name_lower:
                return True
        
        # macOS default pattern: "Screen Shot YYYY-MM-DD at HH.MM.SS.png"
        if name_lower.startswith('screen ') and file.extension.lower() in ['.png', '.jpg']:
            return True
        
        # Windows default pattern: "Screenshot (N).png"
        if name_lower.startswith('screenshot (') and file.extension.lower() == '.png':
            return True
        
        # Additional heuristic: Recent images in Downloads/Desktop
        if file.file_type == FileType.IMAGE:
            parent_dir = Path(file.path).parent.name.lower()
            if parent_dir in ['downloads', 'desktop']:
                age_days = (datetime.now() - file.created_at).days
                # Images created within last 6 months in Downloads/Desktop
                # are likely screenshots
                if age_days < 180:
                    return True
        
        return False
    
    def _build_hash_map(
        self, 
        files: List[FileMetadata]
    ) -> Dict[str, List[FileMetadata]]:
        """
        Build a hash map for duplicate detection.
        
        Only hashes files under the size limit to avoid performance issues.
        
        Args:
            files: List of files to hash
            
        Returns:
            Dictionary mapping file hashes to lists of files
        """
        hash_map: Dict[str, List[FileMetadata]] = {}
        
        # Only hash reasonably-sized files
        hashable_files = [
            f for f in files 
            if f.size_bytes < self.HASH_SIZE_LIMIT_BYTES
        ]
        
        for file in hashable_files:
            try:
                file_hash = self._compute_hash(file.path)
                self._hash_cache[file.path] = file_hash
                
                if file_hash in hash_map:
                    hash_map[file_hash].append(file)
                else:
                    hash_map[file_hash] = [file]
            except Exception:
                # Skip files we can't hash
                continue
        
        return hash_map
    
    def _compute_hash(self, filepath: str, chunk_size: int = 8192) -> str:
        """
        Compute SHA256 hash of file.
        
        Args:
            filepath: Path to file
            chunk_size: Size of chunks to read (default 8KB)
            
        Returns:
            Hexadecimal hash string
            
        Raises:
            IOError: If file cannot be read
        """
        hasher = hashlib.sha256()
        
        with open(filepath, 'rb') as f:
            while chunk := f.read(chunk_size):
                hasher.update(chunk)
        
        return hasher.hexdigest()
