import os
import sys
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

sys.path.insert(0, str(BASE_DIR))


if os.getenv("DJANGO_DBMS") == "sqlite3":
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": os.getenv("POSTGRESQL_DATABASE_NAME"),
            "USER": os.getenv("POSTGRESQL_DATABASE_USER"),
            "PASSWORD": os.getenv("POSTGRESQL_DATABASE_PASSWORD"),
            "HOST": os.getenv("POSTGRESQL_DATABASE_HOST", "127.0.0.1"),
            "PORT": os.getenv("POSTGRESQL_DATABASE_PORT", "5432"),
        }
    }
