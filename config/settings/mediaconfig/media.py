import os

from dotenv import load_dotenv

load_dotenv()

MEDIA_URL = "/media/"
MEDIA_ROOT = os.getenv("MEDIA_ROOT", "/data/media")
