import os

CSRF_TRUSTED_ORIGINS = os.getenv("CSRF_TRUSTED_ORIGINS", "http://localhost:3000").split(",")
CORS_ALLOWED_ORIGINS = os.getenv("CORS_ALLOWED_ORIGINS", "http://localhost:3000").split(",")

vercel_url = os.getenv("VERCEL_URL")
if vercel_url:
    CSRF_TRUSTED_ORIGINS.append(f"https://{vercel_url}")
    CORS_ALLOWED_ORIGINS.append(f"https://{vercel_url}")


SESSION_COOKIE_SAMESITE = "None"
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SAMESITE = "None"
CSRF_COOKIE_SECURE = True

# Required so the browser sends the session cookie cross-origin
CORS_ALLOW_CREDENTIALS = True

# Allow the CSRF cookie to be read by JS (needed for PATCH/POST from the browser)
# CSRF_COOKIE_SAMESITE = "Lax"
CSRF_COOKIE_HTTPONLY = False  # JS needs to read it to send as header
