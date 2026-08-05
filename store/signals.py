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

@receiver(post_migrate)
def ensure_default_categories(sender, **kwargs):
    if sender.name != 'store':
        return
    try:
        from .models import Category, Product, ProductImage, ProductVariant, Brand
        from decimal import Decimal
        
        brand = Brand.objects.filter(is_active=True).first()

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
            if not created and not cat.is_active:
                cat.is_active = True
                cat.save()

            # Ensure every category has products
            if not cat.products.filter(is_active=True).exists():
                p_name = f"{data['name']} Luxury Collection Piece"
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
                    ProductImage.objects.create(product=prod, url=data['image_url'], is_primary=True)
                if not prod.variants.exists():
                    ProductVariant.objects.create(product=prod, sku=f"SKU-{prod.id}", stock=50, is_active=True)
    except Exception:
        pass

