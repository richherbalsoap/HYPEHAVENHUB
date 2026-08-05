from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .models import UserProfile, CountrySetting

User = get_user_model()

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """
    Auto-creates UserProfile for new users to avoid profile lookup errors.
    """
    if created:
        default_country = CountrySetting.objects.first()
        UserProfile.objects.get_or_create(
            user=instance,
            defaults={
                'country': default_country,
                'preferred_language': 'en'
            }
        )

# Import allauth signal to detect login
from allauth.account.signals import user_logged_in
from .models import Order

@receiver(user_logged_in)
def merge_guest_orders_on_login(request, user, **kwargs):
    """
    Merge guest orders created with `guest_email` into the user's account upon login.
    """
    if user.email:
        guest_orders = Order.objects.filter(guest_email=user.email).exclude(user=user)
        if guest_orders.exists():
            guest_orders.update(user=user)


from django.db.models.signals import post_migrate
from django.apps import AppConfig

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

@receiver(post_migrate)
def ensure_default_categories(sender, **kwargs):
    if sender.name != 'store':
        return
    try:
        from .models import Category, Product, ProductImage, ProductVariant, Brand
        from decimal import Decimal
        
        brand = Brand.objects.filter(is_active=True).first()
        valid_slugs = [data['slug'] for data in CATEGORIES_DATA]

        # 1. Ensure the 7 master categories exist
        master_cats = {}
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
            cat.name = data['name'] # Ensure EXACT case & spelling
            cat.is_active = True
            cat.save()
            master_cats[data['slug']] = cat

        fallback_cat = master_cats.get('12-pair-earrings-box-with-bracelet')

        # 2. Reassign products from unwanted categories and delete the unwanted categories
        unwanted = Category.objects.exclude(slug__in=valid_slugs)
        for bad_cat in unwanted:
            if fallback_cat:
                bad_cat.products.update(category=fallback_cat)
            bad_cat.delete()

        # 3. Ensure every master category has active products
        for data in CATEGORIES_DATA:
            cat = master_cats[data['slug']]
            if not cat.products.filter(is_active=True).exists():
                p_name = f"{data['name']} Collection Piece"
                prod, _ = Product.objects.get_or_create(
                    name=p_name,
                    defaults={
                        'category': cat,
                        'brand': brand,
                        'base_price': Decimal('2499.00'),
                        'discount_percent': Decimal('15.00'),
                        'description': data['description'],
                        'short_description': data['description'][:150],
                        'is_active': True,
                        'is_featured': True,
                        'is_bestseller': True,
                    }
                )
                if not prod.images.exists():
                    ProductImage.objects.create(product=prod, image_url=data['image_url'], is_primary=True)
                if not prod.variants.exists():
                    ProductVariant.objects.create(product=prod, sku=f"SKU-{prod.id}", stock=50, is_active=True)
    except Exception:
        pass
