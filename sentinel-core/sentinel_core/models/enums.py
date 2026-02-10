from enum import Enum

class FileType(str, Enum):
    DOCUMENT = "document"
    IMAGE = "image"
    VIDEO = "video"
    AUDIO = "audio"
    ARCHIVE = "archive"
    EXECUTABLE = "executable"
    CODE = "code"
    UNKNOWN = "unknown"

class ActionType(str, Enum):
    MOVE = "move"
    RENAME = "rename"
    DELETE = "delete"
    CREATE_FOLDER = "create_folder"
    SKIP = "skip"

class TaskStatus(str, Enum):
    SCANNING = "scanning"
    PLANNING = "planning"
    REVIEW = "review"
    EXECUTING = "executing"
    COMPLETED = "completed"
    FAILED = "failed"

TaskState = TaskStatus
