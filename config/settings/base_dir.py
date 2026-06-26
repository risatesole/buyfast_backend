from pathlib import Path

# Resolves to the project root (the folder that contains manage.py)
# Path chain: base_dir.py → settings/ → config/ → project root
BASE_DIR = Path(__file__).resolve().parent.parent.parent
