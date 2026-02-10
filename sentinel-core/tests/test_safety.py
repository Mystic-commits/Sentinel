"""
Tests for the Safety Validator

Tests plan validation, safety checks, and rejection of dangerous operations.
"""

import pytest
from pathlib import Path

from sentinel_core.safety.safety import SafetyValidator
from sentinel_core.models.planner import PlanSchema, OperationSchema, OperationType


class TestBasicValidation:
    """Tests for basic plan validation."""
    
    def test_validate_empty_plan(self):
        """Test validation of a plan with no operations."""
        plan = PlanSchema(
            task_id="test-123",
            operations=[],
            summary="Empty plan"
        )
        
        validator = SafetyValidator()
        result = validator.validate_plan(plan)
        
        assert result.is_safe is True
        assert len(result.errors) == 0
    
    def test_validate_safe_move(self):
        """Test validation of a safe move operation."""
        plan = PlanSchema(
            task_id="test-123",
            operations=[
                OperationSchema(
                    type=OperationType.MOVE,
                    source_path="/Users/test/Downloads/file.txt",
                    destination_path="/Users/test/Documents/file.txt",
                    reason="Organize document"
                )
            ],
            summary="Move 1 file"
        )
        
        validator = SafetyValidator()
        result = validator.validate_plan(plan)
        
        assert result.is_safe is True
        assert len(result.errors) == 0
    
    def test_validate_safe_delete(self):
        """Test validation of a safe delete operation."""
        plan = PlanSchema(
            task_id="test-123",
            operations=[
                OperationSchema(
                    type=OperationType.DELETE,
                    source_path="/Users/test/Downloads/old-installer.dmg",
                    reason="Remove old installer"
                )
            ],
            summary="Delete 1 file"
        )
        
        validator = SafetyValidator()
        result = validator.validate_plan(plan)
        
        assert result.is_safe is True
        assert len(result.errors) == 0


class TestSystemDirectoryProtection:
    """Tests for system directory protection."""
    
    @pytest.mark.parametrize("system_path", [
        "/System/Library/file.txt",
        "/System/Applications/app.app",
        "/usr/bin/command",
        "/Library/System/file",
        "C:\\Windows\\System32\\file.dll",
        "C:\\Program Files\\app\\file.exe",
    ])
    def test_reject_system_directories(self, system_path):
        """Test that operations on system directories are rejected."""
        plan = PlanSchema(
            task_id="test-123",
            operations=[
                OperationSchema(
                    type=OperationType.DELETE,
                    source_path=system_path,
                    reason="Should be rejected"
                )
            ],
            summary="Dangerous operation"
        )
        
        validator = SafetyValidator()
        result = validator.validate_plan(plan)
        
        assert result.is_safe is False
        assert len(result.errors) > 0
        # Error message should mention system/protected directory
        assert any(
            "system" in error.lower() or "protected" in error.lower() 
            for error in result.errors
        )
    
    def test_reject_applications_directory(self):
        """Test that /Applications is protected."""
        plan = PlanSchema(
            task_id="test-123",
            operations=[
                OperationSchema(
                    type=OperationType.DELETE,
                    source_path="/Applications/Safari.app",
                    reason="Should be rejected"
                )
            ],
            summary="Dangerous"
        )
        
        validator = SafetyValidator()
        result = validator.validate_plan(plan)
        
        assert result.is_safe is False


class TestScaleWarnings:
    """Tests for warnings on large-scale operations."""
    
    def test_large_number_of_deletions(self):
        """Test that many deletions trigger a warning."""
        # Create plan with 150 delete operations
        operations = [
            OperationSchema(
                type=OperationType.DELETE,
                source_path=f"/Users/test/file{i}.txt",
                reason="Cleanup"
            )
            for i in range(150)
        ]
        
        plan = PlanSchema(
            task_id="test-123",
            operations=operations,
            summary="Large cleanup"
        )
        
        validator = SafetyValidator()
        result = validator.validate_plan(plan)
        
        # Should be safe but have warnings
        assert result.is_safe is True
        assert len(result.warnings) > 0
        assert any("delete" in warning.lower() for warning in result.warnings)
    
    def test_normal_number_of_operations(self):
        """Test that normal number of operations has no warnings."""
        operations = [
            OperationSchema(
                type=OperationType.MOVE,
                source_path=f"/Users/test/Downloads/file{i}.txt",
                destination_path=f"/Users/test/Documents/file{i}.txt",
                reason="Organize"
            )
            for i in range(20)
        ]
        
        plan = PlanSchema(
            task_id="test-123",
            operations=operations,
            summary="Normal cleanup"
        )
        
        validator = SafetyValidator()
        result = validator.validate_plan(plan)
        
        assert result.is_safe is True
        assert len(result.warnings) == 0


class TestOperationTypes:
    """Tests for different operation types."""
    
    def test_validate_copy_operation(self):
        """Test validation of copy operations."""
        plan = PlanSchema(
            task_id="test-123",
            operations=[
                OperationSchema(
                    type=OperationType.COPY,
                    source_path="/Users/test/file.txt",
                    destination_path="/Users/test/backup/file.txt",
                    reason="Backup"
                )
            ],
            summary="Copy file"
        )
        
        validator = SafetyValidator()
        result = validator.validate_plan(plan)
        
        assert result.is_safe is True
    
    def test_validate_rename_operation(self):
        """Test validation of rename operations."""
        plan = PlanSchema(
            task_id="test-123",
            operations=[
                OperationSchema(
                    type=OperationType.RENAME,
                    source_path="/Users/test/oldname.txt",
                    destination_path="/Users/test/newname.txt",
                    reason="Better naming"
                )
            ],
            summary="Rename file"
        )
        
        validator = SafetyValidator()
        result = validator.validate_plan(plan)
        
        assert result.is_safe is True


class TestMixedOperations:
    """Tests for plans with mixed operation types."""
    
    def test_mixed_safe_operations(self):
        """Test a plan with multiple safe operation types."""
        plan = PlanSchema(
            task_id="test-123",
            operations=[
                OperationSchema(
                    type=OperationType.MOVE,
                    source_path="/Users/test/Downloads/doc.pdf",
                    destination_path="/Users/test/Documents/doc.pdf",
                    reason="Organize"
                ),
                OperationSchema(
                    type=OperationType.DELETE,
                    source_path="/Users/test/Downloads/old.dmg",
                    reason="Remove installer"
                ),
                OperationSchema(
                    type=OperationType.COPY,
                    source_path="/Users/test/important.txt",
                    destination_path="/Users/test/backup/important.txt",
                    reason="Backup"
                ),
            ],
            summary="Mixed operations"
        )
        
        validator = SafetyValidator()
        result = validator.validate_plan(plan)
        
        assert result.is_safe is True
        assert len(result.errors) == 0
    
    def test_reject_if_any_unsafe(self):
        """Test that plan is rejected if any operation is unsafe."""
        plan = PlanSchema(
            task_id="test-123",
            operations=[
                OperationSchema(
                    type=OperationType.MOVE,
                    source_path="/Users/test/file1.txt",
                    destination_path="/Users/test/Documents/file1.txt",
                    reason="Safe operation"
                ),
                OperationSchema(
                    type=OperationType.DELETE,
                    source_path="/System/Library/important.txt",
                    reason="Unsafe operation"
                ),
            ],
            summary="Mixed safe/unsafe"
        )
        
        validator = SafetyValidator()
        result = validator.validate_plan(plan)
        
        # Entire plan should be rejected
        assert result.is_safe is False
        assert len(result.errors) > 0


class TestPathValidation:
    """Tests for path-specific validation."""
    
    def test_reject_missing_destination(self):
        """Test that MOVE requires a destination."""
        plan = PlanSchema(
            task_id="test-123",
            operations=[
                OperationSchema(
                    type=OperationType.MOVE,
                    source_path="/Users/test/file.txt",
                    destination_path=None,  # Missing!
                    reason="Move file"
                )
            ],
            summary="Invalid move"
        )
        
        validator = SafetyValidator()
        result = validator.validate_plan(plan)
        
        # Should be rejected for missing destination
        assert result.is_safe is False
    
    def test_allow_user_directories(self):
        """Test that user directories are allowed."""
        safe_paths = [
            "/Users/test/Downloads/file.txt",
            "/Users/test/Desktop/file.txt",
            "/Users/test/Documents/file.txt",
            "/Users/test/Pictures/file.jpg",
            "C:\\Users\\test\\Downloads\\file.txt",
        ]
        
        for path in safe_paths:
            plan = PlanSchema(
                task_id="test-123",
                operations=[
                    OperationSchema(
                        type=OperationType.DELETE,
                        source_path=path,
                        reason="Test"
                    )
                ],
                summary="Test"
            )
            
            validator = SafetyValidator()
            result = validator.validate_plan(plan)
            
            assert result.is_safe is True, f"Should allow: {path}"
