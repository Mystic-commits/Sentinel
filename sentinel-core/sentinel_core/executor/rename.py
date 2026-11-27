"""Rename a filesystem entry without replacing an existing destination."""

import ctypes
import errno
import os
import sys
from functools import cache
from pathlib import Path


@cache
def _native_rename():
    libc = ctypes.CDLL(None, use_errno=True)
    if sys.platform == "darwin":
        rename = libc.renamex_np
        rename.argtypes = (ctypes.c_char_p, ctypes.c_char_p, ctypes.c_uint)
    elif sys.platform.startswith("linux"):
        rename = libc.renameat2
        rename.argtypes = (
            ctypes.c_int,
            ctypes.c_char_p,
            ctypes.c_int,
            ctypes.c_char_p,
            ctypes.c_uint,
        )
    else:
        raise OSError(errno.ENOTSUP, "Exclusive rename is unavailable on this platform")
    rename.restype = ctypes.c_int
    return rename


def rename_without_replacing(source: str, destination: str) -> None:
    if os.name == "nt":
        Path(source).rename(destination)
        return

    try:
        rename = _native_rename()
    except AttributeError as error:
        raise OSError(errno.ENOTSUP, "Exclusive rename is unavailable on this system") from error

    old_path, new_path = os.fsencode(source), os.fsencode(destination)
    if sys.platform == "darwin":
        result = rename(old_path, new_path, 0x00000004)  # RENAME_EXCL
    else:
        # AT_FDCWD for each path, then RENAME_NOREPLACE.
        result = rename(-100, old_path, -100, new_path, 1)
    if result != 0:
        code = ctypes.get_errno()
        message = {
            errno.EXDEV: "Sentinel moves require source and destination on the same filesystem",
            errno.ENOTSUP: "This filesystem does not support exclusive rename",
        }.get(code, os.strerror(code))
        raise OSError(code, message, source, None, destination)
