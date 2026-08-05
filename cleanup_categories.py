import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'glamour_store.settings')
django.setup()

from store.models import Category, Product

# Exact 5 clean categories requested by user
CLEAN_CATEGORIES = [
    {
        'name': '12 Pair Set',
        'slug': '12-pair-set',
        'description': 'Exquisite collection of 12 pair earring sets designed for elegance, daily wear, and special occasions.',
        'image_url': 'https://images.unsplash.com/photo-1630019852942-f89202989a59?auto=format&fit=crop&w=800&q=80'
    },
    {
        'name': 'Necklace With Earrings 16 Pair Set',
        'slug': 'necklace-with-earrings-16-pair-set',
        'description': 'Grand bridal & festive set featuring a statement necklace paired with 16 royal earring designs.',
        'image_url': 'https://images.unsplash.com/photo-1599643478518-a784e5dc4c8f?auto=format&fit=crop&w=800&q=80'
    },
    {
        'name': 'Necklace',
        'slug': 'necklace',
        'description': 'Luxury handcrafted necklaces, chokers, and pendant chains with intricate gold & stone detail.',
        'image_url': 'https://images.unsplash.com/photo-1599643477877-530eb83abc8e?auto=format&fit=crop&w=800&q=80'
    },
    {
        'name': 'Bracelet',
        'slug': 'bracelet',
        'description': 'Stunning artisan bracelets, bangles, and cuffs designed to elevate every outfit with luxury shimmer.',
        'image_url': 'https://images.unsplash.com/photo-1611591475140-be3617c98480?auto=format&fit=crop&w=800&q=80'
    },
    {
        'name': '12 Pair Earrings Box With Bracelet',
        'slug': '12-pair-earrings-box-with-bracelet',
        'description': 'Deluxe combo gift set featuring 12 pair curated jhumka/earrings along with a matching designer bracelet.',
        'image_url': 'https://images.unsplash.com/photo-1535632066927-ab7c9ab60908?auto=format&fit=crop&w=800&q=80'
    }
]

def clean_database():
    print("Cleaning Database Categories...")
    
    # 1. Ensure the 5 clean categories exist
    clean_objs = {}
    clean_slugs = [c['slug'] for c in CLEAN_CATEGORIES]
    for c_data in CLEAN_CATEGORIES:
        cat, created = Category.objects.get_or_create(
            slug=c_data['slug'],
            defaults={
                'name': c_data['name'],
                'description': c_data['description'],
                'image_url': c_data['image_url'],
                'is_active': True
            }
        )
        cat.name = c_data['name']
        cat.is_active = True
        cat.save()
        clean_objs[c_data['slug']] = cat

    fallback_cat = clean_objs['12-pair-set']

    # 2. Reassign products from unwanted categories to fallback_cat
    unwanted_cats = Category.objects.exclude(slug__in=clean_slugs)
    for bad_cat in unwanted_cats:
        prods = list(bad_cat.products.all())
        for p in prods:
            p.category = fallback_cat
            p.save()
            print(f"Reassigned product '{p.name}' from '{bad_cat.name}' -> '{fallback_cat.name}'")
        
        print(f"Deleting unwanted category: '{bad_cat.name}' ({bad_cat.slug})")
        bad_cat.delete()

    print("\nRemaining Active Categories in DB:")
    for c in Category.objects.all():
        print(f"  - ID: {c.id} | Name: {c.name} | Slug: {c.slug} | Products: {c.products.count()}")

if __name__ == '__main__':
    clean_database()
