import os
import django
from django.utils.text import slugify

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'glamour_store.settings')
django.setup()

from store.models import Category, Product

# EXACT 7 CATEGORIES REQUESTED BY USER - DO NOT CHANGE 1 SINGLE CHAR/CASE
EXACT_USER_CATEGORIES = [
    {
        'name': '12 Pair Earrings Box With Bracelet',
        'slug': '12-pair-earrings-box-with-bracelet',
        'description': 'Handcrafted 12 pair earrings box with designer bracelet collection.'
    },
    {
        'name': '12 Pair earrings box',
        'slug': '12-pair-earrings-box',
        'description': 'Handcrafted 12 pair earrings box collection.'
    },
    {
        'name': 'Bracelet',
        'slug': 'bracelet',
        'description': 'Luxury artisan bracelets, bangles, and cuffs.'
    },
    {
        'name': 'Necklace',
        'slug': 'necklace',
        'description': 'Handcrafted luxury necklaces and chokers.'
    },
    {
        'name': 'neckless with earring',
        'slug': 'neckless-with-earring',
        'description': 'Statement necklace paired with matching earring collection.'
    },
    {
        'name': '16 Pair earrings box',
        'slug': '16-pair-earrings-box',
        'description': 'Deluxe 16 pair earrings box collection.'
    },
    {
        'name': '16 pair earrings box with bracelet',
        'slug': '16-pair-earrings-box-with-bracelet',
        'description': 'Grand 16 pair earrings box with designer bracelet collection.'
    }
]

def apply_exact_categories():
    print("Applying EXACT 7 User Categories...")

    valid_slugs = [c['slug'] for c in EXACT_USER_CATEGORIES]
    created_cats = []

    # 1. Create or update exact 7 categories
    for c_data in EXACT_USER_CATEGORIES:
        cat, created = Category.objects.get_or_create(
            slug=c_data['slug'],
            defaults={
                'name': c_data['name'],
                'description': c_data['description'],
                'is_active': True
            }
        )
        cat.name = c_data['name'] # Ensure EXACT case & spelling
        cat.description = c_data['description']
        cat.is_active = True
        cat.save()
        created_cats.append(cat)

    fallback_cat = created_cats[0]

    # 2. Reassign products from any category not in valid_slugs to fallback_cat
    unwanted = Category.objects.exclude(slug__in=valid_slugs)
    for bad in unwanted:
        for p in bad.products.all():
            p.category = fallback_cat
            p.save()
            print(f"Reassigned product '{p.name}' -> '{fallback_cat.name}'")
        print(f"Deleting category: '{bad.name}' ({bad.slug})")
        bad.delete()

    print("\n--- FINAL EXACT DATABASE CATEGORIES ---")
    for idx, c in enumerate(Category.objects.filter(is_active=True).order_by('id'), 1):
        print(f"{idx}. Name: '{c.name}' | Slug: '{c.slug}' | Active: {c.is_active} | Products: {c.products.count()}")

if __name__ == '__main__':
    apply_exact_categories()
