import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'glamour_store.settings')
django.setup()

from store.models import Category, Product

CATEGORIES_DATA = [
    {
        'name': '12 Pair Earrings Box With Bracelet',
        'slug': '12-pair-earrings-box-with-bracelet',
        'description': 'Handcrafted 12 pair earrings box with designer bracelet collection.',
        'image_url': 'https://images.unsplash.com/photo-1535632066927-ab7c9ab60908?auto=format&fit=crop&w=800&q=80'
    },
    {
        'name': '12 Pair earrings box',
        'slug': '12-pair-earrings-box',
        'description': 'Handcrafted 12 pair earrings box collection.',
        'image_url': 'https://images.unsplash.com/photo-1630019852942-f89202989a59?auto=format&fit=crop&w=800&q=80'
    },
    {
        'name': 'Bracelet',
        'slug': 'bracelet',
        'description': 'Stunning artisan bracelets, bangles, and cuffs.',
        'image_url': 'https://images.unsplash.com/photo-1611591475140-be3617c98480?auto=format&fit=crop&w=800&q=80'
    },
    {
        'name': 'Necklace',
        'slug': 'necklace',
        'description': 'Luxury handcrafted necklaces and chokers.',
        'image_url': 'https://images.unsplash.com/photo-1599643477877-530eb83abc8e?auto=format&fit=crop&w=800&q=80'
    },
    {
        'name': 'neckless with earring',
        'slug': 'neckless-with-earring',
        'description': 'Statement necklace paired with matching earring collection.',
        'image_url': 'https://images.unsplash.com/photo-1599643478518-a784e5dc4c8f?auto=format&fit=crop&w=800&q=80'
    },
    {
        'name': '16 Pair earrings box',
        'slug': '16-pair-earrings-box',
        'description': 'Deluxe 16 pair earrings box collection.',
        'image_url': 'https://images.unsplash.com/photo-1605100804763-247f67b3557e?auto=format&fit=crop&w=800&q=80'
    },
    {
        'name': '16 pair earrings box with bracelet',
        'slug': '16-pair-earrings-box-with-bracelet',
        'description': 'Grand 16 pair earrings box with designer bracelet collection.',
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
