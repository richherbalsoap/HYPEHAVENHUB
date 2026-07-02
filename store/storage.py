"""
Helper for uploading files to Cloudflare R2 (S3) storage.
"""
import os
import uuid
from django.core.files.storage import default_storage

class BlobUploadError(Exception):
    pass

def is_configured():
    return True

def upload_file(file_obj, folder="uploads"):
    """
    Uploads a single in-memory file (e.g. from request.FILES) to default_storage
    and returns its public URL.
    """
    original_name = getattr(file_obj, 'name', 'file')
    ext = original_name.rsplit('.', 1)[-1].lower() if '.' in original_name else ''
    safe_ext = ext if ext and len(ext) <= 5 else 'bin'
    pathname = f"{folder}/{uuid.uuid4().hex}.{safe_ext}"

    try:
        saved_path = default_storage.save(pathname, file_obj)
        url = default_storage.url(saved_path)
        return url
    except Exception as exc:
        raise BlobUploadError(f"Upload failed: {exc}") from exc

def delete_file(url):
    """Best-effort delete of a blob given its public URL."""
    try:
        # Very basic attempt to get path from URL
        path = '/'.join(url.split('/')[-2:])
        default_storage.delete(path)
    except Exception:
        pass

