import os

from dotenv import load_dotenv

from config.settings.base_dir import BASE_DIR

load_dotenv()

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
