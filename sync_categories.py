import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'glamour_store.settings')
django.setup()

from store.models import Category, Product

CATEGORIES_DATA = [
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
    },
    {
        'name': '16 Pair Earrings With Bracelet',
        'slug': '16-pair-earrings-with-bracelet',
        'description': 'Ultimate festive hamper containing 16 versatile earring pairs and a premium matching bracelet.',
        'image_url': 'https://images.unsplash.com/photo-1605100804763-247f67b3557e?auto=format&fit=crop&w=800&q=80'
    }
]

def sync_categories():
    print("Syncing Categories...")
    category_objs = {}
    for data in CATEGORIES_DATA:
        cat, created = Category.objects.get_or_create(
            slug=data['slug'],
            defaults={
                'name': data['name'],
                'description': data['description'],
                'image_url': data['image_url'],
                'is_active': True
            }
        )
        if not created:
            cat.name = data['name']
            cat.description = data['description']
            if not cat.image_url:
                cat.image_url = data['image_url']
            cat.is_active = True
            cat.save()
        category_objs[data['slug']] = cat
        print(f"  [{'CREATED' if created else 'UPDATED'}] Category: {cat.name} ({cat.slug})")

    # Map existing products across categories so each category has at least one product
    products = list(Product.objects.all())
    if products:
        category_list = list(category_objs.values())
        for idx, prod in enumerate(products):
            target_cat = category_list[idx % len(category_list)]
            prod.category = target_cat
            prod.save(update_fields=['category'])
            print(f"  Assigned Product '{prod.name}' -> Category '{target_cat.name}'")

    print("Categories Sync Complete!")

if __name__ == '__main__':
    sync_categories()
