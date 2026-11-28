"""Rename a filesystem entry without replacing an existing destination."""

import ctypes
import errno
import os
import sys
from contextlib import ExitStack, suppress
from functools import cache
from pathlib import Path
from stat import FILE_ATTRIBUTE_REPARSE_POINT, S_ISREG


@cache
def _native_rename():
    libc = ctypes.CDLL(None, use_errno=True)
    if sys.platform == "darwin":
        rename = libc.renameatx_np
    elif sys.platform.startswith("linux"):
        rename = libc.renameat2
    else:
        raise OSError(errno.ENOTSUP, "Exclusive rename is unavailable on this platform")
    rename.argtypes = (
        ctypes.c_int,
        ctypes.c_char_p,
        ctypes.c_int,
        ctypes.c_char_p,
        ctypes.c_uint,
    )
    rename.restype = ctypes.c_int
    return rename


def rename_without_replacing(source: str, destination: str) -> None:
    if os.name == "nt":
        Path(source).rename(destination)
        return

    current_directory = -2 if sys.platform == "darwin" else -100  # AT_FDCWD
    _rename_at(source, destination, current_directory, current_directory)


def _rename_at(source: str, destination: str, source_fd: int, destination_fd: int) -> None:
    try:
        rename = _native_rename()
    except AttributeError as error:
        raise OSError(errno.ENOTSUP, "Exclusive rename is unavailable on this system") from error
    exclusive = 0x00000004 if sys.platform == "darwin" else 1
    result = rename(
        source_fd, os.fsencode(source), destination_fd, os.fsencode(destination), exclusive
    )
    if result != 0:
        code = ctypes.get_errno()
        message = {
            errno.EXDEV: "Sentinel moves require source and destination on the same filesystem",
            errno.ENOTSUP: "This filesystem does not support exclusive rename",
        }.get(code, os.strerror(code))
        raise OSError(code, message, source, None, destination)


def file_fingerprint(info: os.stat_result) -> tuple[int, ...]:
    if not S_ISREG(info.st_mode) or (
        getattr(info, "st_file_attributes", 0) & FILE_ATTRIBUTE_REPARSE_POINT
    ):
        raise ValueError("Expected a regular file")
    return info.st_dev, info.st_ino, info.st_size, info.st_mtime_ns, info.st_ctime_ns


def rename_scoped(root: Path, source: Path, destination: Path, expected: tuple[int, ...]) -> None:
    """Rename through guarded parent directories inside a reviewed folder."""
    source_relative = source.relative_to(root)
    destination_relative = destination.relative_to(root)
    if not root.is_absolute() or any(
        not file.parts or ".." in file.parts for file in (source_relative, destination_relative)
    ):
        raise ValueError("A move failed folder safety validation")
    if os.name == "nt":
        from .windows_directories import hold_parent

        with ExitStack() as handles:
            hold_parent(source.parent, handles)
            hold_parent(destination.parent, handles, create_below=root)
            if file_fingerprint(source.lstat()) != expected:
                raise ValueError("A source file changed before the move")
            rename_without_replacing(str(source), str(destination))
        return

    flags = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW
    with ExitStack() as handles:

        def open_directory(path: str, parent_fd: int | None = None) -> int:
            descriptor = os.open(path, flags, dir_fd=parent_fd)
            handles.callback(os.close, descriptor)
            return descriptor

        root_fd = open_directory(root.anchor)
        for part in root.parts[1:]:
            root_fd = open_directory(part, root_fd)

        def open_parent(relative: Path, *, create: bool) -> int:
            parent_fd = root_fd
            for part in relative.parts[:-1]:
                if create:
                    with suppress(FileExistsError):
                        os.mkdir(part, dir_fd=parent_fd)
                parent_fd = open_directory(part, parent_fd)
            return parent_fd

        source_fd = open_parent(source_relative, create=False)
        destination_fd = open_parent(destination_relative, create=True)
        source_info = os.stat(source.name, dir_fd=source_fd, follow_symlinks=False)
        if file_fingerprint(source_info) != expected:
            raise ValueError("A source file changed before the move")
        for parent, descriptor in (
            (source.parent, source_fd),
            (destination.parent, destination_fd),
        ):
            if not os.path.samestat(parent.lstat(), os.fstat(descriptor)):
                raise ValueError("A folder changed before the move")
        _rename_at(source.name, destination.name, source_fd, destination_fd)
