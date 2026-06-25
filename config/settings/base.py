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


SECRET_KEY = "django-insecure-d!0w_bs6g&3xxpm9!i4@y+w%d)$-yuvta7lh&0k6%kyh0=f3wg"

ROOT_URLCONF = "config.urls"

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


# Custom settings
AUTH_USER_MODEL = "accounts.User"
LOGIN_URL = "/signin"


CSRF_TRUSTED_ORIGINS = os.getenv("CSRF_TRUSTED_ORIGINS", "http://localhost:3000").split(
    ","
)

# ─── CORS ────────────────────────────────────────────────────────────────────
# Allow the Next.js dev server to call Django directly from the browser
CORS_ALLOWED_ORIGINS = os.getenv("CORS_ALLOWED_ORIGINS", "http://localhost:3000").split(
    ","
)

SESSION_COOKIE_SAMESITE = "None"
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SAMESITE = "None"
CSRF_COOKIE_SECURE = True

# Required so the browser sends the session cookie cross-origin
CORS_ALLOW_CREDENTIALS = True

# Allow the CSRF cookie to be read by JS (needed for PATCH/POST from the browser)
# CSRF_COOKIE_SAMESITE = "Lax"
CSRF_COOKIE_HTTPONLY = False  # JS needs to read it to send as header

# ─────────────────────────────────────────────────────────────────────────────

# File storage settings
FILE_STORAGE_SUPABASE_PROJECT_ID = os.getenv("SUPABASE_PROJECT_ID")
FILE_STORAGE_SUPABASE_SECRET_KEY = os.getenv("SUPABASE_SECRET_KEY")
FILE_STORAGE_SUPABASE_BUCKET = os.getenv("SUPABASE_BUCKET")
