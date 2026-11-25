import os
import hashlib
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Set

from pypdf import PdfReader
from sentinel_core.models.enums import FileType
from sentinel_core.models.filesystem import FileMetadata, ScanResult
from sentinel_core.scanner import config

from time import monotonic


class ScanBudgetExhausted(Exception):
    """The scan hit a configured entry or time limit."""


class Scanner:
    def __init__(self, root_path: str, max_depth: int = config.MAX_SCAN_DEPTH, *, include_previews: bool = True,
                 max_entries: int | None = None, max_seconds: float | None = None):
        self.max_entries = max_entries
        self.max_seconds = max_seconds
        self.root_path = Path(root_path).resolve()
        self.max_depth = max_depth
        self.include_previews = include_previews
        self.ignored_dirs = config.IGNORED_DIRS
        self.text_extensions = config.TEXT_EXTENSIONS
        self.pdf_extensions = config.PDF_EXTENSIONS

    def scan(self) -> ScanResult:
        """
        Recursively scan the directory and return a ScanResult.
        """
        if not self.root_path.exists():
            return ScanResult(
                root_path=str(self.root_path),
                files=[],
                errors=[f"Directory not found: {self.root_path}"]
            )

        files_metadata: List[FileMetadata] = []
        errors: List[str] = []
        ignored_count = 0
        self.entries_seen = 0
        self.deadline = monotonic() + self.max_seconds if self.max_seconds is not None else None
        truncated = False

        try:
            for path in self._safe_walk(self.root_path, current_depth=0):
                try:
                    metadata = self._extract_metadata(path)
                    files_metadata.append(metadata)
                except Exception as e:
                    errors.append(f"Failed to process {path}: {str(e)}")
                    
        except ScanBudgetExhausted as error:
            truncated = True
            errors.append(str(error))
        except Exception as e:
            errors.append(f"Fatal scan error: {str(e)}")

        return ScanResult(
            root_path=str(self.root_path),
            files=files_metadata,
            ignored_count=ignored_count, # Note: _safe_walk doesn't count ignored yet for simplicity
            errors=errors,
            truncated=truncated
        )

    def _iter_entries(self, directory: Path):
        with os.scandir(directory) as entries:
            for entry in entries:
                yield Path(entry.path)

    def _safe_walk(self, directory: Path, current_depth: int):
        """
        Generator that yields file paths recursively up to max_depth.
        """
        if current_depth > self.max_depth:
            return

        try:
            entries = self._iter_entries(directory)
            if self.max_entries is None and self.deadline is None:
                entries = iter(sorted(entries))
            
            for entry in entries:
                if self.max_entries is not None and self.entries_seen >= self.max_entries:
                    raise ScanBudgetExhausted("Scan reached its entry limit")
                if self.deadline is not None and monotonic() >= self.deadline:
                    raise ScanBudgetExhausted("Scan reached its time limit")
                self.entries_seen += 1
                if entry.name in self.ignored_dirs or entry.name.startswith('.'):
                    continue

                if entry.is_symlink() or getattr(entry, "is_junction", lambda: False)():
                    continue

                if entry.is_dir():
                    yield from self._safe_walk(entry, current_depth + 1)
                elif entry.is_file():
                    yield entry
        except ScanBudgetExhausted:
            raise
        except PermissionError:
            # We skip directories we can't read
            return
        except Exception:
            return

    def _extract_metadata(self, path: Path) -> FileMetadata:
        """
        Extracts metadata from a single file.
        """
        stat = path.stat()
        file_type = self._determine_file_type(path)
        
        preview = None
        # Only attempt preview if small enough
        if self.include_previews and stat.st_size < config.MAX_FILE_SIZE_PREVIEW:
            preview = self._get_preview(path, file_type)

        return FileMetadata(
            path=str(path),
            name=path.name,
            extension=path.suffix.lower(),
            size_bytes=stat.st_size,
            created_at=datetime.fromtimestamp(stat.st_ctime),
            modified_at=datetime.fromtimestamp(stat.st_mtime),
            file_type=file_type,
            preview_text=preview[:150] if preview else None
            # hash is expensive, so we skip it for default scan
        )

    def _determine_file_type(self, path: Path) -> FileType:
        ext = path.suffix.lower()
        if ext in self.text_extensions or ext in self.pdf_extensions or ext in {".doc", ".docx", ".odt", ".rtf"}:
            return FileType.DOCUMENT # Broadly code/text is document for organization
        if ext in {'.jpg', '.jpeg', '.png', '.gif', '.webp', '.svg', '.bmp', '.tiff'}:
            return FileType.IMAGE
        if ext in {'.mp4', '.mov', '.avi', '.mkv', '.webm'}:
            return FileType.VIDEO
        if ext in {'.mp3', '.wav', '.flac', '.aac'}:
            return FileType.AUDIO
        if ext in {'.zip', '.tar', '.gz', '.7z', '.rar'}:
            return FileType.ARCHIVE
        if ext in {'.exe', '.dmg', '.pkg', '.msi', '.app'}:
            return FileType.EXECUTABLE
        return FileType.UNKNOWN

    def _get_preview(self, path: Path, file_type: FileType) -> Optional[str]:
        """
        Safely extracts first N chars of text content.
        """
        ext = path.suffix.lower()
        try:
            if ext in self.pdf_extensions:
                return self._read_pdf_preview(path)
            
            if ext in self.text_extensions:
                return self._read_text_preview(path)
                
        except Exception:
            return None
        return None

    def _read_text_preview(self, path: Path) -> Optional[str]:
        try:
            with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read(config.MAX_PREVIEW_SIZE_CHARS)
                return content.replace('\n', ' ').strip()
        except Exception:
            return None

    def _read_pdf_preview(self, path: Path) -> Optional[str]:
        try:
            reader = PdfReader(path)
            if len(reader.pages) > 0:
                text = reader.pages[0].extract_text()
                if text:
                    return text[:config.MAX_PREVIEW_SIZE_CHARS].replace('\n', ' ').strip()
        except Exception:
            return None
        return None
