import os
import sys
import django

sys.path.insert(0, r"c:\Users\abc\Downloads\Attached-Assets (1)\Attached-Assets")
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'glamour_store.settings')
django.setup()

from store.models import Product, ProductImage

print("--- ALL PRODUCTS ---")
for p in Product.objects.all():
    print(f"ID: {p.id} | Slug: {p.slug} | Name: {p.name}")
    images = ProductImage.objects.filter(product=p)
    for img in images:
        print(f"   -> SubImage ID: {img.id} | Image: {img.image} | URL: {img.image.url if img.image else 'N/A'}")
