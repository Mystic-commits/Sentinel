"""Scanner module for Sentinel."""

from .scanner import Scanner

__all__ = ["Scanner", "scan_directory"]


def scan_directory(path: str):
    """
    Convenience function to scan a directory.
    
    Args:
        path: Path to directory to scan
        
    Returns:
        ScanResult containing file metadata
        
    Example:
        >>> from sentinel_core.scanner import scan_directory
        >>> result = scan_directory("/path/to/folder")
        >>> print(f"Found {result.total_files} files")
    """
    scanner = Scanner(path)
    return scanner.scan()
