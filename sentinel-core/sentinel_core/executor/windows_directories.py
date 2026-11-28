"""Keep Windows directory names stable across a journaled move."""

import ctypes
from contextlib import ExitStack, suppress
from ctypes import wintypes
from functools import cache
from pathlib import Path
from stat import FILE_ATTRIBUTE_DIRECTORY, FILE_ATTRIBUTE_REPARSE_POINT

_FILE_SHARE_READ_WRITE = 0x03
_FILE_LIST_DIRECTORY = 0x01
_FILE_READ_ATTRIBUTES = 0x80
_OPEN_EXISTING = 3
_BACKUP_SEMANTICS = 0x02000000
_OPEN_REPARSE_POINT = 0x00200000
_FILE_ATTRIBUTE_TAG_INFO = 9
_INVALID_HANDLE = ctypes.c_void_p(-1).value


class _AttributeTagInfo(ctypes.Structure):
    _fields_ = [("attributes", wintypes.DWORD), ("tag", wintypes.DWORD)]


@cache
def _kernel():
    api = ctypes.WinDLL("kernel32", use_last_error=True)
    api.CreateFileW.argtypes = (
        wintypes.LPCWSTR,
        wintypes.DWORD,
        wintypes.DWORD,
        ctypes.c_void_p,
        wintypes.DWORD,
        wintypes.DWORD,
        wintypes.HANDLE,
    )
    api.CreateFileW.restype = wintypes.HANDLE
    api.GetFileInformationByHandleEx.argtypes = (
        wintypes.HANDLE,
        ctypes.c_int,
        ctypes.c_void_p,
        wintypes.DWORD,
    )
    api.GetFileInformationByHandleEx.restype = wintypes.BOOL
    api.CloseHandle.argtypes = (wintypes.HANDLE,)
    api.CloseHandle.restype = wintypes.BOOL
    return api


def hold_parent(parent: Path, stack: ExitStack, *, create_below: Path | None = None) -> None:
    api = _kernel()
    directory = Path(parent.anchor)
    for component in parent.parts[1:]:
        directory /= component
        if (
            create_below is not None
            and directory != create_below
            and directory.is_relative_to(create_below)
        ):
            with suppress(FileExistsError):
                directory.mkdir()
        # List-directory access participates in share checks. Omit FILE_SHARE_DELETE.
        handle = api.CreateFileW(
            str(directory),
            _FILE_LIST_DIRECTORY | _FILE_READ_ATTRIBUTES,
            _FILE_SHARE_READ_WRITE,
            None,
            _OPEN_EXISTING,
            _BACKUP_SEMANTICS | _OPEN_REPARSE_POINT,
            None,
        )
        if handle == _INVALID_HANDLE:
            raise ctypes.WinError(ctypes.get_last_error(), f"Could not hold directory {directory}")
        stack.callback(api.CloseHandle, handle)
        info = _AttributeTagInfo()
        if not api.GetFileInformationByHandleEx(
            handle, _FILE_ATTRIBUTE_TAG_INFO, ctypes.byref(info), ctypes.sizeof(info)
        ):
            raise ctypes.WinError(ctypes.get_last_error())
        if (
            not info.attributes & FILE_ATTRIBUTE_DIRECTORY
            or info.attributes & FILE_ATTRIBUTE_REPARSE_POINT
        ):
            raise ValueError("A folder in the move path is a link or reparse point")
