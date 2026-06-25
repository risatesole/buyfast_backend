import os

from dotenv import load_dotenv

load_dotenv()

DEBUG: bool = os.getenv("DJANGO_ENVIRONMENT") == "development"
