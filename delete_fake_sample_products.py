import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'glamour_store.settings')
django.setup()

from store.models import Product

def remove_fake_products():
    print("Finding and deleting fake sample products...")
    
    # Target products created automatically with 'Collection Piece' in name
    fake_prods = Product.objects.filter(name__icontains='Collection Piece')
    count = fake_prods.count()
    
    for p in fake_prods:
        print(f"Deleting fake product: '{p.name}' (ID: {p.id})")
        p.delete()

    print(f"Successfully deleted {count} fake products from database!")

if __name__ == '__main__':
    remove_fake_products()
