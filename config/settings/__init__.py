from .auth.auth_password_validator import (
    AUTH_PASSWORD_VALIDATORS as AUTH_PASSWORD_VALIDATORS,
)
from .base import *
from .database.database import DATABASES as DATABASES
from .development.testrunner import TEST_RUNNER as TEST_RUNNER
from .hosts.allowed_hosts import ALLOWED_HOSTS as ALLOWED_HOSTS
from .installed_apps.installed_apps import INSTALLED_APPS as INSTALLED_APPS
from .middleware.middleware import MIDDLEWARE as MIDDLEWARE
from .rest_framework.rest_framework import REST_FRAMEWORK as REST_FRAMEWORK
from .staticfiles.staticfiles import STATIC_ROOT as STATIC_ROOT
from .staticfiles.staticfiles import STATIC_URL as STATIC_URL
from .staticfiles.staticfiles import STATICFILES_DIRS as STATICFILES_DIRS
