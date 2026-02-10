"""
Fake Directory Generator

Generates realistic fake directory structures for testing.
Mimics actual user directories with various file types and patterns.
"""

import random
from typing import Dict, List
from datetime import datetime, timedelta

from tests.utils.mock_filesystem import MockFilesystem


class FakeDirectoryGenerator:
    """
    Generates realistic fake directory structures for testing.
    
    Creates directories and files that mimic real user data, including:
    - Old installers in Downloads
    - Screenshots on Desktop
    - Archives and documents
    - Large video files
    - Duplicate files
    
    Example:
        >>> with MockFilesystem() as fs:
        ...     generator = FakeDirectoryGenerator()
        ...     stats = generator.generate_complete_structure(fs)
        ...     print(f"Created {stats['total_files']} files")
    """
    
    # Realistic file names by category
    INSTALLERS = [
        ("Chrome.dmg", 80 * 1024 * 1024, 60),  # name, size, age_days
        ("Firefox.dmg", 75 * 1024 * 1024, 45),
        ("VSCode.dmg", 90 * 1024 * 1024, 90),
        ("Docker.dmg", 500 * 1024 * 1024, 120),
        ("Steam-Installer.exe", 15 * 1024 * 1024, 30),
        ("Discord-Setup.exe", 85 * 1024 * 1024, 50),
        ("Zoom.pkg", 40 * 1024 * 1024, 35),
    ]
    
    ARCHIVES = [
        ("project-backup.zip", 50 * 1024 * 1024, 180),
        ("photos-2023.rar", 100 * 1024 * 1024, 200),
        ("documents-archive.tar.gz", 25 * 1024 * 1024, 90),
        ("old-files.7z", 30 * 1024 * 1024, 365),
        ("backup.zip", 15 * 1024 * 1024, 800),  # Very old
    ]
    
    VIDEOS = [
        ("vacation-2024.mp4", 250 * 1024 * 1024, 30),
        ("tutorial-recording.mov", 180 * 1024 * 1024, 15),
        ("presentation.avi", 150 * 1024 * 1024, 60),
        ("zoom-recording.mp4", 300 * 1024 * 1024, 5),
    ]
    
    SCREENSHOTS = [
        ("Screen Shot 2024-01-15 at 10.30.45 AM.png", 500 * 1024, 10),
        ("Screen Shot 2024-02-01 at 09.15.30 AM.png", 450 * 1024, 5),
        ("Screenshot (1).png", 600 * 1024, 20),
        ("Screenshot (2).png", 550 * 1024, 15),
        ("screenshot_20240115_103045.png", 480 * 1024, 25),
    ]
    
    DOCUMENTS = [
        ("resume.pdf", 200 * 1024, 120),
        ("invoice-2024-01.pdf", 150 * 1024, 30),
        ("meeting-notes.docx", 50 * 1024, 7),
        ("report.xlsx", 300 * 1024, 14),
        ("presentation.pptx", 5 * 1024 * 1024, 21),
        ("contract.pdf", 180 * 1024, 60),
    ]
    
    IMAGES = [
        ("photo1.jpg", 2 * 1024 * 1024, 100),
        ("photo2.jpg", 1.8 * 1024 * 1024, 95),
        ("diagram.png", 800 * 1024, 40),
    ]
    
    def generate_downloads(
        self, 
        fs: MockFilesystem, 
        num_installers: int = 3,
        num_archives: int = 2,
        num_documents: int = 5
    ) -> int:
        """
        Generate a realistic Downloads folder.
        
        Args:
            fs: Mock filesystem to populate
            num_installers: Number of installer files to create
            num_archives: Number of archive files to create
            num_documents: Number of document files to create
            
        Returns:
            Number of files created
        """
        count = 0
        
        # Create Downloads directory
        fs.create_directory("Downloads")
        
        # Add installers (old ones that should be cleaned)
        for name, size, age in random.sample(self.INSTALLERS, min(num_installers, len(self.INSTALLERS))):
            fs.create_file(
                f"Downloads/{name}",
                size_bytes=size,
                age_days=age
            )
            count += 1
        
        # Add archives
        for name, size, age in random.sample(self.ARCHIVES, min(num_archives, len(self.ARCHIVES))):
            fs.create_file(
                f"Downloads/{name}",
                size_bytes=size,
                age_days=age
            )
            count += 1
        
        # Add documents
        for name, size, age in random.sample(self.DOCUMENTS, min(num_documents, len(self.DOCUMENTS))):
            fs.create_file(
                f"Downloads/{name}",
                size_bytes=size,
                age_days=age
            )
            count += 1
        
        return count
    
    def generate_desktop(self, fs: MockFilesystem, num_screenshots: int = 3) -> int:
        """
        Generate a realistic Desktop folder.
        
        Args:
            fs: Mock filesystem to populate
            num_screenshots: Number of screenshots to create
            
        Returns:
            Number of files created
        """
        count = 0
        
        fs.create_directory("Desktop")
        
        # Add screenshots
        for name, size, age in random.sample(self.SCREENSHOTS, min(num_screenshots, len(self.SCREENSHOTS))):
            fs.create_file(
                f"Desktop/{name}",
                size_bytes=size,
                age_days=age
            )
            count += 1
        
        # Add some random work files
        fs.create_file("Desktop/notes.txt", content="Meeting notes\n* Task 1\n* Task 2", age_days=3)
        fs.create_file("Desktop/todo.md", content="# TODO\n- [ ] Finish report", age_days=1)
        count += 2
        
        return count
    
    def generate_documents(self, fs: MockFilesystem) -> int:
        """
        Generate a realistic Documents folder with subdirectories.
        
        Args:
            fs: Mock filesystem to populate
            
        Returns:
            Number of files created
        """
        count = 0
        
        # Create subdirectories
        fs.create_directory("Documents/Work")
        fs.create_directory("Documents/Personal")
        fs.create_directory("Documents/Archive")
        
        # Add work documents
        fs.create_file("Documents/Work/report-q1.pdf", size_bytes=1024 * 1024, age_days=30)
        fs.create_file("Documents/Work/presentation.pptx", size_bytes=3 * 1024 * 1024, age_days=15)
        count += 2
        
        # Add personal documents
        fs.create_file("Documents/Personal/tax-2023.pdf", size_bytes=500 * 1024, age_days=180)
        fs.create_file("Documents/Personal/insurance.pdf", size_bytes=300 * 1024, age_days=90)
        count += 2
        
        # Add old archived documents
        fs.create_file("Documents/Archive/old-project.docx", size_bytes=200 * 1024, age_days=400)
        count += 1
        
        return count
    
    def generate_videos(self, fs: MockFilesystem, num_videos: int = 2) -> int:
        """
        Generate Videos folder with large files.
        
        Args:
            fs: Mock filesystem to populate
            num_videos: Number of video files to create
            
        Returns:
            Number of files created
        """
        count = 0
        
        fs.create_directory("Videos")
        
        for name, size, age in random.sample(self.VIDEOS, min(num_videos, len(self.VIDEOS))):
            fs.create_file(
                f"Videos/{name}",
                size_bytes=size,
                age_days=age
            )
            count += 1
        
        return count
    
    def generate_duplicates(self, fs: MockFilesystem) -> int:
        """
        Generate duplicate files for testing duplicate detection.
        
        Args:
            fs: Mock filesystem to populate
            
        Returns:
            Number of files created
        """
        count = 0
        
        # Create identical files in different locations
        content = "This is a duplicate file with identical content."
        
        fs.create_file("Downloads/document.txt", content=content, age_days=30)
        fs.create_file("Desktop/document.txt", content=content, age_days=20)  # Newer
        fs.create_file("Documents/document-copy.txt", content=content, age_days=40)  # Oldest
        count += 3
        
        return count
    
    def generate_complete_structure(self, fs: MockFilesystem) -> Dict[str, int]:
        """
        Generate a complete fake directory structure.
        
        Creates all standard user directories with realistic content.
        
        Args:
            fs: Mock filesystem to populate
            
        Returns:
            Dictionary with statistics about created files:
                - total_files: Total number of files created
                - installers: Number of installer files
                - archives: Number of archive files
                - screenshots: Number of screenshots
                - videos: Number of video files
                - duplicates: Number of duplicate files
        """
        downloads_count = self.generate_downloads(fs, num_installers=3, num_archives=2, num_documents=5)
        desktop_count = self.generate_desktop(fs, num_screenshots=3)
        documents_count = self.generate_documents(fs)
        videos_count = self.generate_videos(fs, num_videos=2)
        duplicates_count = self.generate_duplicates(fs)
        
        # Count all files
        all_files = list(fs.root.rglob("*"))
        total_files = sum(1 for f in all_files if f.is_file())
        
        return {
            "total_files": total_files,
            "installers": 3,
            "archives": 2,
            "screenshots": 3,
            "videos": 2,
            "duplicates": 3,
            "downloads": downloads_count,
            "desktop": desktop_count,
            "documents": documents_count,
        }
    
    def generate_minimal(self, fs: MockFilesystem) -> Dict[str, int]:
        """
        Generate a minimal structure for quick tests.
        
        Args:
            fs: Mock filesystem to populate
            
        Returns:
            Statistics dictionary
        """
        fs.create_directory("Downloads")
        fs.create_file("Downloads/old-installer.dmg", size_bytes=50 * 1024 * 1024, age_days=60)
        fs.create_file("Downloads/archive.zip", size_bytes=10 * 1024 * 1024, age_days=100)
        
        fs.create_directory("Desktop")
        fs.create_file("Desktop/Screen Shot 2024-01-15.png", size_bytes=500 * 1024, age_days=10)
        
        return {
            "total_files": 3,
            "installers": 1,
            "archives": 1,
            "screenshots": 1
        }
