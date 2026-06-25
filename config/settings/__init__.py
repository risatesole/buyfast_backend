from .auth.auth import AUTH_USER_MODEL as AUTH_USER_MODEL
from .auth.auth import LOGIN_URL as LOGIN_URL
from .auth.auth_password_validator import (
    AUTH_PASSWORD_VALIDATORS as AUTH_PASSWORD_VALIDATORS,
)
from .base import *
from .database.database import DATABASES as DATABASES
from .development.testrunner import TEST_RUNNER as TEST_RUNNER
from .hosts.allowed_hosts import ALLOWED_HOSTS as ALLOWED_HOSTS
from .installed_apps.installed_apps import INSTALLED_APPS as INSTALLED_APPS
from .localization.localization import LANGUAGE_CODE as LANGUAGE_CODE
from .localization.localization import TIME_ZONE as TIME_ZONE
from .localization.localization import USE_I18N as USE_I18N
from .mediaconfig.media import MEDIA_ROOT as MEDIA_ROOT
from .mediaconfig.media import MEDIA_URL as MEDIA_URL
from .middleware.middleware import MIDDLEWARE as MIDDLEWARE
from .rest_framework.rest_framework import REST_FRAMEWORK as REST_FRAMEWORK
from .staticfiles.staticfiles import STATIC_ROOT as STATIC_ROOT
from .staticfiles.staticfiles import STATIC_URL as STATIC_URL
from .staticfiles.staticfiles import STATICFILES_DIRS as STATICFILES_DIRS
