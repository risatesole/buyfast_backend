# file_storage

Minimal package: receive a Django request file → upload to Supabase → get back the public URL.

---

## Install

```bash
pip install -e /path/to/file_storage
```

---

## settings.py

Add these three keys to the Django project that uses the package:

```python
FILE_STORAGE_SUPABASE_PROJECT_ID = "your-project-id"
FILE_STORAGE_SUPABASE_SECRET_KEY = "your-secret-key"
FILE_STORAGE_SUPABASE_BUCKET     = "your-bucket-name"
```

---

## Usage in your view

```python
from file_storage import upload_file

# Inside your DRF view, after validating the request:
url = upload_file(request.FILES["image"])
# url → "https://<project>.supabase.co/storage/v1/object/public/<bucket>/uploads/..."
```

That's it. `upload_file` accepts any Django file object and returns the public URL string.
