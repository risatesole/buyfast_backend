import time
from django.conf import settings
from supabase import create_client


def upload_file(file) -> str:
    """
    Upload a file received from a Django HTTP request to Supabase Storage.

    Usage in your view:
        from file_storage import upload_file

        url = upload_file(request.FILES["image"])

    Args:
        file: Any Django file-like object (InMemoryUploadedFile, TemporaryUploadedFile, etc.)

    Returns:
        str: The public URL of the uploaded file.

    Required settings.py keys:
        FILE_STORAGE_SUPABASE_PROJECT_ID
        FILE_STORAGE_SUPABASE_SECRET_KEY
        FILE_STORAGE_SUPABASE_BUCKET
    """
    project_id = settings.FILE_STORAGE_SUPABASE_PROJECT_ID
    secret_key = settings.FILE_STORAGE_SUPABASE_SECRET_KEY
    bucket     = settings.FILE_STORAGE_SUPABASE_BUCKET

    client = create_client(f"https://{project_id}.supabase.co", secret_key)

    unique_name = f"{int(time.time())}_{file.name}"
    file_path   = f"uploads/{unique_name}"
    content_type = getattr(file, "content_type", "application/octet-stream")

    client.storage.from_(bucket).upload(
        file_path,
        file.read(),
        {"content-type": content_type},
    )

    return client.storage.from_(bucket).get_public_url(file_path)
