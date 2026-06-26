import os

ALLOWED_HOSTS = os.getenv("DJANGO_ALLOWED_HOSTS", "localhost,127.0.0.1").split(",")

vercel_url = os.getenv("VERCEL_URL")
if vercel_url:
    ALLOWED_HOSTS.append(vercel_url)
