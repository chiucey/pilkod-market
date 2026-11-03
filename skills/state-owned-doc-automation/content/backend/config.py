import os


BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Windows shared paths
SHARED_BASE_PATH = r"D:\category\归档"
WATCH_DIR = r"D:\category\待归档"

# Model provider placeholder
AI_MODEL = "qwen"  # or "deepseek"
AI_API_KEY = ""

# Local service settings
FLASK_HOST = "127.0.0.1"
FLASK_PORT = 5000

# Storage
DATA_DIR = os.path.join(BASE_DIR, "data")
DB_PATH = os.path.join(DATA_DIR, "archive.db")
INDEX_DIR = os.path.join(BASE_DIR, "index")
UPLOADS_TEMP_DIR = os.path.join(BASE_DIR, "uploads_temp")
PROCESSED_BACKUP_DIR = os.path.join(WATCH_DIR, "_processed_backup")

# Auto archive
MAX_READ_CHARS = 20000

