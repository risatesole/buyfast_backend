import os

from dotenv import load_dotenv

load_dotenv()

# File storage settings used by custom package that uploads the files to supabase storage
FILE_STORAGE_SUPABASE_PROJECT_ID = os.getenv("SUPABASE_PROJECT_ID")
FILE_STORAGE_SUPABASE_SECRET_KEY = os.getenv("SUPABASE_SECRET_KEY")
FILE_STORAGE_SUPABASE_BUCKET = os.getenv("SUPABASE_BUCKET")
