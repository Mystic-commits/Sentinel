from enum import Enum


class FileType(str, Enum):  # noqa: UP042 - preserve existing str(member) representation
    DOCUMENT = "document"
    IMAGE = "image"
    VIDEO = "video"
    AUDIO = "audio"
    ARCHIVE = "archive"
    EXECUTABLE = "executable"
    CODE = "code"
    UNKNOWN = "unknown"


class ActionType(str, Enum):  # noqa: UP042 - preserve existing str(member) representation
    MOVE = "move"
    RENAME = "rename"
    DELETE = "delete"
    CREATE_FOLDER = "create_folder"
    SKIP = "skip"


class TaskStatus(str, Enum):  # noqa: UP042 - preserve existing str(member) representation
    SCANNING = "scanning"
    PLANNING = "planning"
    REVIEW = "review"
    EXECUTING = "executing"
    COMPLETED = "completed"
    FAILED = "failed"


TaskState = TaskStatus
