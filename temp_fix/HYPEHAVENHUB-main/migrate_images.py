from dotenv import load_dotenv
load_dotenv('.env.local')
import os
import sys
import django
import base64
from io import BytesIO
from django.core.files.uploadedfile import InMemoryUploadedFile

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'glamour_store.settings')
django.setup()

from store.models import ProductImage, Category, SubCategory, Brand, ReviewImage
from store.storage import upload_file

def b64_to_file(b64_str, name="image.jpg"):
    img_data = base64.b64decode(b64_str)
    io = BytesIO(img_data)
    return InMemoryUploadedFile(io, None, name, 'image/jpeg', len(img_data), None)

def migrate():
    print("Starting image migration to Vercel Blob...")
    
    # 1. Product Images
    print("\n--- Migrating Product Images ---")
    product_images = ProductImage.objects.all()
    for pi in product_images:
        try:
            if not pi.image_url:
                if pi.image_base64:
                    print(f"Uploading base64 for ProductImage ID {pi.id}...")
                    file_obj = b64_to_file(pi.image_base64)
                    pi.image_url = upload_file(file_obj, folder="products")
                    pi.image_base64 = ""
                    pi.save()
                    print(f"  Success: {pi.image_url}")
                elif pi.image and getattr(pi.image, 'file', None):
                    print(f"Uploading local file for ProductImage ID {pi.id}...")
                    pi.image_url = upload_file(pi.image.file, folder="products")
                    pi.image = None
                    pi.save()
                    print(f"  Success: {pi.image_url}")
        except Exception as e:
            print(f"Failed for ProductImage ID {pi.id}: {e}")

    # 2. Categories
    print("\n--- Migrating Categories ---")
    categories = Category.objects.all()
    for cat in categories:
        try:
            if not cat.image_url and cat.image and getattr(cat.image, 'file', None):
                print(f"Uploading local file for Category '{cat.name}'...")
                cat.image_url = upload_file(cat.image.file, folder="categories")
                cat.image = None
                cat.save()
                print(f"  Success: {cat.image_url}")
        except Exception as e:
            print(f"Failed for Category '{cat.name}': {e}")

    # 3. SubCategories
    print("\n--- Migrating SubCategories ---")
    subcategories = SubCategory.objects.all()
    for subcat in subcategories:
        try:
            if not subcat.image_url and subcat.image and getattr(subcat.image, 'file', None):
                print(f"Uploading local file for SubCategory '{subcat.name}'...")
                subcat.image_url = upload_file(subcat.image.file, folder="subcategories")
                subcat.image = None
                subcat.save()
                print(f"  Success: {subcat.image_url}")
        except Exception as e:
            print(f"Failed for SubCategory '{subcat.name}': {e}")

    # 4. Brands
    print("\n--- Migrating Brands ---")
    brands = Brand.objects.all()
    for brand in brands:
        try:
            if not brand.image_url and brand.logo and getattr(brand.logo, 'file', None):
                print(f"Uploading local file for Brand '{brand.name}'...")
                brand.image_url = upload_file(brand.logo.file, folder="brands")
                brand.logo = None
                brand.save()
                print(f"  Success: {brand.image_url}")
        except Exception as e:
            print(f"Failed for Brand '{brand.name}': {e}")

    # 5. ReviewImages
    print("\n--- Migrating ReviewImages ---")
    reviews = ReviewImage.objects.all()
    for review in reviews:
        try:
            if not review.image_url and review.image and getattr(review.image, 'file', None):
                print(f"Uploading local file for ReviewImage ID {review.id}...")
                review.image_url = upload_file(review.image.file, folder="reviews")
                review.image = None
                review.save()
                print(f"  Success: {review.image_url}")
        except Exception as e:
            print(f"Failed for ReviewImage ID {review.id}: {e}")

    print("\nMigration Complete!")

if __name__ == '__main__':
    migrate()
