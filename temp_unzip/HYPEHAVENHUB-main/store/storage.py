"""
Helper for uploading files to Vercel Blob storage.

Why this exists: Vercel's filesystem is wiped on every cold start, so
saving uploaded images with a normal Django ImageField (which writes to
local disk) does not work in production — the file looks like it saved,
then disappears the next time the serverless function restarts. Vercel
Blob gives us a real persistent place to put uploaded images, reachable
by a permanent public URL that we store as plain text in the database
(see Category.image_url / ProductImage.image_url).

Setup (one-time, in the Vercel dashboard):
  1. Project -> Storage -> Create Database -> Blob
  2. Connect it to this project
  3. Vercel automatically sets the BLOB_READ_WRITE_TOKEN env var for you

Uses the `vercel_blob` package (a small Python wrapper around Vercel's
Blob REST API) — add `vercel_blob` to requirements.txt.
"""
import os
import uuid

import vercel_blob


class BlobUploadError(Exception):
    pass


def is_configured():
    return bool(os.environ.get('BLOB_READ_WRITE_TOKEN'))


def upload_file(file_obj, folder="uploads"):
    """
    Uploads a single in-memory file (e.g. from request.FILES) to Vercel
    Blob storage and returns its public URL.

    file_obj: a Django UploadedFile (has .name and supports .read()).
    folder: a path prefix inside the blob store, just for organization
    (e.g. "products", "categories").
    """
    if not is_configured():
        raise BlobUploadError(
            "BLOB_READ_WRITE_TOKEN is not set. Connect a Blob store to "
            "this project in the Vercel dashboard (Storage -> Create "
            "Database -> Blob) and redeploy."
        )

    original_name = getattr(file_obj, 'name', 'file')
    ext = original_name.rsplit('.', 1)[-1].lower() if '.' in original_name else ''
    safe_ext = ext if ext and len(ext) <= 5 else 'bin'
    pathname = f"{folder}/{uuid.uuid4().hex}.{safe_ext}"

    file_obj.seek(0)
    data = file_obj.read()

    try:
        result = vercel_blob.put(pathname, data)
    except Exception as exc:
        raise BlobUploadError(f"Vercel Blob upload failed: {exc}") from exc

    url = result.get('url') if isinstance(result, dict) else None
    if not url:
        raise BlobUploadError(f"Vercel Blob upload returned no URL: {result}")
    return url


def delete_file(url):
    """Best-effort delete of a blob given its public URL. Failures are
    swallowed — a stray orphaned blob is harmless, but a crash here
    should never block a product/category delete in the admin panel."""
    if not is_configured() or not url:
        return
    try:
        vercel_blob.delete(url)
    except Exception:
        pass

