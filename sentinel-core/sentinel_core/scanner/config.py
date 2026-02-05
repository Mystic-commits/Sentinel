# Scanner Configuration
MAX_SCAN_DEPTH = 3  # Default recursion depth
MAX_PREVIEW_SIZE_CHARS = 500  # Max characters to read for preview
TEXT_EXTENSIONS = {'.txt', '.md', '.py', '.js', '.json', '.csv', '.html', '.css', '.xml', '.yml', '.yaml'}
PDF_EXTENSIONS = {'.pdf'}
IGNORED_DIRS = {'.git', 'node_modules', '__pycache__', '.venv', 'venv', 'env', '.DS_Store', 'Thumbs.db'}
MAX_FILE_SIZE_PREVIEW = 10 * 1024 * 1024 # 10MB limit for attempting preview
