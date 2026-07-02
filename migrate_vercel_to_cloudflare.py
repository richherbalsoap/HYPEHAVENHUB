from dotenv import load_dotenv
load_dotenv('.env')

import os
import sys
import django
import requests
from io import BytesIO
from django.core.files.uploadedfile import InMemoryUploadedFile

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'glamour_store.settings')
django.setup()

from store.models import ProductImage, Category, SubCategory, Brand, ReviewImage
from store.storage import upload_file

def download_image(url):
    response = requests.get(url)
    response.raise_for_status()
    # Extract filename from URL
    filename = url.split('/')[-1]
    # Remove query params if any
    filename = filename.split('?')[0]
    io = BytesIO(response.content)
    return InMemoryUploadedFile(io, None, filename, 'image/jpeg', len(response.content), None)

def process_url(obj, field_name, folder_name):
    url = getattr(obj, field_name, '')
    if url and 'vercel-storage.com' in url:
        print(f"Downloading from Vercel: {url}")
        try:
            file_obj = download_image(url)
            print(f"Uploading to Cloudflare R2...")
            new_url = upload_file(file_obj, folder=folder_name)
            setattr(obj, field_name, new_url)
            obj.save()
            print(f"  Success: {new_url}")
        except Exception as e:
            print(f"  Failed to process {url}: {e}")

def migrate():
    print("Starting image migration from Vercel to Cloudflare R2...")
    
    # 1. Product Images
    print("\n--- Migrating Product Images ---")
    for pi in ProductImage.objects.all():
        process_url(pi, 'image_url', 'products')

    # 2. Categories
    print("\n--- Migrating Categories ---")
    for cat in Category.objects.all():
        process_url(cat, 'image_url', 'categories')

    # 3. SubCategories
    print("\n--- Migrating SubCategories ---")
    for subcat in SubCategory.objects.all():
        process_url(subcat, 'image_url', 'subcategories')

    # 4. Brands
    print("\n--- Migrating Brands ---")
    for brand in Brand.objects.all():
        process_url(brand, 'image_url', 'brands')

    # 5. ReviewImages
    print("\n--- Migrating ReviewImages ---")
    for review in ReviewImage.objects.all():
        process_url(review, 'image_url', 'reviews')

    print("\nMigration Complete!")

if __name__ == '__main__':
    migrate()
