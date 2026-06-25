"""
Django settings for main project.
"""

import os
import sys
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

sys.path.insert(0, str(BASE_DIR))


TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

# ─────────────────────────────────────────────────────────────────────────────

# File storage settings
FILE_STORAGE_SUPABASE_PROJECT_ID = os.getenv("SUPABASE_PROJECT_ID")
FILE_STORAGE_SUPABASE_SECRET_KEY = os.getenv("SUPABASE_SECRET_KEY")
FILE_STORAGE_SUPABASE_BUCKET = os.getenv("SUPABASE_BUCKET")
