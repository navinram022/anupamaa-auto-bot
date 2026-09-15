import os

# Project Directories
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROFILE_DIR = os.path.join(BASE_DIR, "chrome_profile")
LOGS_DIR = os.path.join(BASE_DIR, "logs")
os.makedirs(PROFILE_DIR, exist_ok=True)
os.makedirs(LOGS_DIR, exist_ok=True)

# URLs
JUSTSHOWBIZ_FEED_URL = "https://www.justshowbiz.net/tag/anupamaa/feed/"
NOTEBOOKLM_URL = "https://notebooklm.google.com/notebook/a611b8b8-35db-4b71-9b7e-034660c3874c"

# Target Email
TARGET_EMAIL = "Navinram022@gmail.com"

# State tracking file to prevent running multiple times on the same day
STATE_FILE = os.path.join(BASE_DIR, "last_run_state.json")
