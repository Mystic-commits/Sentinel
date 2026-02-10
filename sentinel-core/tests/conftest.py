"""
Pytest Configuration and Fixtures

Provides reusable test fixtures for Sentinel tests.
"""

import pytest
from tests.utils.mock_filesystem import MockFilesystem
from tests.utils.fake_generator import FakeDirectoryGenerator


@pytest.fixture
def mock_fs():
    """
    Provide a clean mock filesystem for each test.
    
    The filesystem is automatically cleaned up after the test.
    
    Example:
        def test_something(mock_fs):
            mock_fs.create_file("test.txt", content="Hello")
            assert mock_fs.exists("test.txt")
    """
    fs = MockFilesystem()
    yield fs
    fs.cleanup()


@pytest.fixture
def fake_generator():
    """
    Provide the fake directory generator.
    
    Example:
        def test_structure(mock_fs, fake_generator):
            fake_generator.generate_downloads(mock_fs)
            # Downloads folder now populated
    """
    return FakeDirectoryGenerator()


@pytest.fixture
def populated_fs(mock_fs, fake_generator):
    """
    Provide a filesystem pre-populated with complete fake data.
    
    Creates a realistic directory structure with all file types.
    
    Example:
        def test_cleanup(populated_fs):
            # populated_fs already has Downloads, Desktop, etc.
            scanner = Scanner(str(populated_fs.root))
            result = scanner.scan()
            assert len(result.files) > 0
    """
    fake_generator.generate_complete_structure(mock_fs)
    return mock_fs


@pytest.fixture
def minimal_fs(mock_fs, fake_generator):
    """
    Provide a filesystem with minimal test data.
    
    Useful for fast tests that just need a few files.
    
    Example:
        def test_quick(minimal_fs):
            # Has just a few test files
            pass
    """
    fake_generator.generate_minimal(mock_fs)
    return mock_fs
