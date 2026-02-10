"""
Tests for Clean My PC Pipeline

Tests file classification, organization rules, and pipeline integration.
"""

import pytest
from datetime import datetime, timedelta
from pathlib import Path

from sentinel_core.cleanpc.classifiers import FileClassifier, FileClassification
from sentinel_core.cleanpc.rules import OrganizationRules
from sentinel_core.models.filesystem import FileMetadata
from sentinel_core.models.enums import FileType


class TestFileClassifier:
    """Tests for file classification heuristics."""
    
    def test_installer_detection_old_dmg(self):
        """Test detection of old .dmg installer in Downloads."""
        file = FileMetadata(
            path="/Users/test/Downloads/Chrome.dmg",
            name="Chrome.dmg",
            extension=".dmg",
            size_bytes=1024 * 1024 * 50,  # 50MB
            created_at=datetime.now() - timedelta(days=60),
            modified_at=datetime.now() - timedelta(days=60),
            file_type=FileType.EXECUTABLE
        )
        
        classifier = FileClassifier()
        classifications = classifier.classify_all([file])
        
        assert len(classifications) == 1
        assert classifications[0].is_installer is True
        assert classifications[0].suggested_action == "delete"
    
    def test_installer_detection_recent_file(self):
        """Test that recent installers are not flagged."""
        file = FileMetadata(
            path="/Users/test/Downloads/App.dmg",
            name="App.dmg",
            extension=".dmg",
            size_bytes=1024 * 1024 * 50,
            created_at=datetime.now() - timedelta(days=5),
            modified_at=datetime.now() - timedelta(days=5),
            file_type=FileType.EXECUTABLE
        )
        
        classifier = FileClassifier()
        classifications = classifier.classify_all([file])
        
        assert classifications[0].is_installer is False
    
    def test_archive_detection(self):
        """Test detection of archive files."""
        file = FileMetadata(
            path="/Users/test/Downloads/archive.zip",
            name="archive.zip",
            extension=".zip",
            size_bytes=1024 * 1024 * 10,
            created_at=datetime.now() - timedelta(days=100),
            modified_at=datetime.now() - timedelta(days=100),
            file_type=FileType.ARCHIVE
        )
        
        classifier = FileClassifier()
        classifications = classifier.classify_all([file])
        
        assert classifications[0].is_archive is True
        assert classifications[0].suggested_action == "move"
        assert "Archives" in classifications[0].suggested_target
    
    def test_large_video_detection(self):
        """Test detection of large video files."""
        file = FileMetadata(
            path="/Users/test/Desktop/video.mp4",
            name="video.mp4",
            extension=".mp4",
            size_bytes=150 * 1024 * 1024,  # 150MB
            created_at=datetime.now() - timedelta(days=10),
            modified_at=datetime.now() - timedelta(days=10),
            file_type=FileType.VIDEO
        )
        
        classifier = FileClassifier()
        classifications = classifier.classify_all([file])
        
        assert classifications[0].is_large_video is True
        assert classifications[0].video_size_mb == 150
        assert "Videos" in classifications[0].suggested_target
    
    def test_screenshot_detection_filename(self):
        """Test detection of screenshots by filename pattern."""
        file = FileMetadata(
            path="/Users/test/Desktop/Screen Shot 2024-01-15 at 10.30.45 AM.png",
            name="Screen Shot 2024-01-15 at 10.30.45 AM.png",
            extension=".png",
            size_bytes=1024 * 500,
            created_at=datetime.now() - timedelta(days=5),
            modified_at=datetime.now() - timedelta(days=5),
            file_type=FileType.IMAGE
        )
        
        classifier = FileClassifier()
        classifications = classifier.classify_all([file])
        
        assert classifications[0].is_screenshot is True
        assert "Screenshots" in classifications[0].suggested_target
    
    def test_screenshot_detection_windows_pattern(self):
        """Test detection of Windows screenshot pattern."""
        file = FileMetadata(
            path="/Users/test/Downloads/Screenshot (1).png",
            name="Screenshot (1).png",
            extension=".png",
            size_bytes=1024 * 300,
            created_at=datetime.now() - timedelta(days=2),
            modified_at=datetime.now() - timedelta(days=2),
            file_type=FileType.IMAGE
        )
        
        classifier = FileClassifier()
        classifications = classifier.classify_all([file])
        
        assert classifications[0].is_screenshot is True


class TestOrganizationRules:
    """Tests for organization rules."""
    
    def test_rule_priority(self):
        """Test that rules are applied by priority."""
        rules = OrganizationRules()
        
        # Create a file that matches multiple rules (screenshot + image)
        file = FileMetadata(
            path="/Users/test/Desktop/screenshot.png",
            name="screenshot.png",
            extension=".png",
            size_bytes=1024 * 100,
            created_at=datetime.now(),
            modified_at=datetime.now(),
            file_type=FileType.IMAGE
        )
        
        classifier = FileClassifier()
        classifications = classifier.classify_all([file])
        
        matches = rules.apply_rules(classifications)
        
        # Screenshot rule should match (higher priority)
        assert len(matches) == 1
        assert matches[0].suggested_category == "screenshot"
    
    def test_installer_rule(self):
        """Test installer organization rule."""
        rules = OrganizationRules()
        
        file = FileMetadata(
            path="/Users/test/Downloads/old_installer.dmg",
            name="old_installer.dmg",
            extension=".dmg",
            size_bytes=1024 * 1024 * 50,
            created_at=datetime.now() - timedelta(days=60),
            modified_at=datetime.now() - timedelta(days=60),
            file_type=FileType.EXECUTABLE
        )
        
        classifier = FileClassifier()
        classifications = classifier.classify_all([file])
        matches = rules.apply_rules(classifications)
        
        assert len(matches) == 1
        assert matches[0].suggested_category == "installer"
        assert "Old installer" in matches[0].reason


class TestCleanPCIntegration:
    """Integration tests for the full pipeline."""
    
    @pytest.mark.asyncio
    async def test_pipeline_with_sample_files(self):
        """Test the full pipeline with sample files."""
        # This would require mocking the planner, safety, and executor
        # For now, this is a placeholder for future integration tests
        pass
    
    def test_classification_summary(self):
        """Test that summary statistics are calculated correctly."""
        files = [
            FileMetadata(
                path="/Users/test/Downloads/App.dmg",
                name="App.dmg",
                extension=".dmg",
                size_bytes=50 * 1024 * 1024,
                created_at=datetime.now() - timedelta(days=60),
                modified_at=datetime.now() - timedelta(days=60),
                file_type=FileType.EXECUTABLE
            ),
            FileMetadata(
                path="/Users/test/Desktop/screenshot.png",
                name="screenshot.png",
                extension=".png",
                size_bytes=500 * 1024,
                created_at=datetime.now() - timedelta(days=5),
                modified_at=datetime.now() - timedelta(days=5),
                file_type=FileType.IMAGE
            ),
            FileMetadata(
                path="/Users/test/Downloads/video.mp4",
                name="video.mp4",
                extension=".mp4",
                size_bytes=150 * 1024 * 1024,
                created_at=datetime.now() - timedelta(days=10),
                modified_at=datetime.now() - timedelta(days=10),
                file_type=FileType.VIDEO
            ),
        ]
        
        classifier = FileClassifier()
        classifications = classifier.classify_all(files)
        
        # Count classifications
        installers = sum(1 for c in classifications if c.is_installer)
        screenshots = sum(1 for c in classifications if c.is_screenshot)
        large_videos = sum(1 for c in classifications if c.is_large_video)
        
        assert installers == 1  # The .dmg file
        assert screenshots == 1  # The screenshot.png
        assert large_videos == 1  # The video.mp4


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
