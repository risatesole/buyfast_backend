"""
Django settings for main project.
"""

from pathlib import Path
import sys

import os
from dotenv import load_dotenv
load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

sys.path.insert(0, str(BASE_DIR))
TEST_RUNNER = 'django.test.runner.DiscoverRunner'

SECRET_KEY = 'django-insecure-d!0w_bs6g&3xxpm9!i4@y+w%d)$-yuvta7lh&0k6%kyh0=f3wg'

DEBUG: bool = os.getenv("DJANGO_ENVIRONMENT") == "development"

ALLOWED_HOSTS = os.getenv("DJANGO_ALLOWED_HOSTS", "localhost,127.0.0.1").split(",")

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'corsheaders',

    'rest_framework',
    'rest_framework.authtoken',

    'drf_spectacular',

    'taggit',

    'api',
    'products',
    'accounts',
    'cart',
    'inventory'
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',    # ← MUST be first
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework.authentication.SessionAuthentication",
    ),
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
}

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

if os.getenv("DJANGO_DBMS") == "sqlite3":
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': os.getenv('POSTGRESQL_DATABASE_NAME'),
            'USER': os.getenv('POSTGRESQL_DATABASE_USER'),
            'PASSWORD': os.getenv('POSTGRESQL_DATABASE_PASSWORD'),
            'HOST': os.getenv('POSTGRESQL_DATABASE_HOST', '127.0.0.1'),
            'PORT': os.getenv('POSTGRESQL_DATABASE_PORT', '5432'),
        }
    }

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

STATIC_URL = 'static/'

# Custom settings
AUTH_USER_MODEL = "accounts.User"
LOGIN_URL = "/signin"
MEDIA_URL = "/media/"
MEDIA_ROOT = os.getenv("MEDIA_ROOT", "/data/media")

CSRF_TRUSTED_ORIGINS = os.getenv(
    "CSRF_TRUSTED_ORIGINS",
    "http://localhost:3000"
).split(",")

# ─── CORS ────────────────────────────────────────────────────────────────────
# Allow the Next.js dev server to call Django directly from the browser
CORS_ALLOWED_ORIGINS = os.getenv(
    "CORS_ALLOWED_ORIGINS",
    "http://localhost:3000"
).split(",")

# Required so the browser sends the session cookie cross-origin
CORS_ALLOW_CREDENTIALS = True

# Allow the CSRF cookie to be read by JS (needed for PATCH/POST from the browser)
CSRF_COOKIE_SAMESITE = "Lax"
CSRF_COOKIE_HTTPONLY = False   # JS needs to read it to send as header

# ─────────────────────────────────────────────────────────────────────────────

# File storage settings
FILE_STORAGE_SUPABASE_PROJECT_ID = os.getenv('SUPABASE_PROJECT_ID')
FILE_STORAGE_SUPABASE_SECRET_KEY = os.getenv('SUPABASE_SECRET_KEY')
FILE_STORAGE_SUPABASE_BUCKET     = os.getenv("SUPABASE_BUCKET")