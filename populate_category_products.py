import os
import uuid
import django
from decimal import Decimal

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'glamour_store.settings')
django.setup()

from store.models import Category, Product, ProductImage, ProductVariant, Brand

SAMPLE_PRODUCTS = {
    '12-pair-set': [
        {
            'name': 'Golden Royal Jhumka 12 Pair Collection',
            'base_price': Decimal('2499.00'),
            'discount_percent': Decimal('20.00'),
            'description': 'A grand collection of 12 handcrafted golden jhumka pairs featuring pearls, Kundan stones, and antique gold polish.',
            'image_url': 'https://images.unsplash.com/photo-1630019852942-f89202989a59?auto=format&fit=crop&w=800&q=80',
            'is_bestseller': True, 'is_featured': True
        },
        {
            'name': 'Oxidized Silver Party 12 Pair Set',
            'base_price': Decimal('1999.00'),
            'discount_percent': Decimal('15.00'),
            'description': 'Boho-chic 12 pair oxidized silver earrings box set perfect for college, festive, and ethnic wear.',
            'image_url': 'https://images.unsplash.com/photo-1535632066927-ab7c9ab60908?auto=format&fit=crop&w=800&q=80',
            'is_new_arrival': True
        },
        {
            'name': 'Temple Antique Jhumka 12 Pair Set',
            'base_price': Decimal('2899.00'),
            'discount_percent': Decimal('25.00'),
            'description': 'Heritage temple design 12 pair jhumkas crafted with ruby pink and emerald green stone detailing.',
            'image_url': 'https://images.unsplash.com/photo-1605100804763-247f67b3557e?auto=format&fit=crop&w=800&q=80',
            'is_featured': True
        },
        {
            'name': 'Meenakari Art 12 Pair Earring Set',
            'base_price': Decimal('2299.00'),
            'discount_percent': Decimal('10.00'),
            'description': 'Vibrant Rajasthani Meenakari hand-painted 12 pair jhumka collection in velvet gift box.',
            'image_url': 'https://images.unsplash.com/photo-1599643478518-a784e5dc4c8f?auto=format&fit=crop&w=800&q=80',
            'is_bestseller': True
        }
    ],
    'necklace-with-earrings-16-pair-set': [
        {
            'name': 'Bridal Kundan Necklace & 16 Pair Earring Deluxe Hamper',
            'base_price': Decimal('4999.00'),
            'discount_percent': Decimal('30.00'),
            'description': 'The ultimate bridal statement set featuring a choker necklace with 16 matching earring pairs.',
            'image_url': 'https://images.unsplash.com/photo-1599643478518-a784e5dc4c8f?auto=format&fit=crop&w=800&q=80',
            'is_featured': True, 'is_bestseller': True
        },
        {
            'name': 'Royal Heritage Choker & 16 Pair Jhumka Box',
            'base_price': Decimal('5499.00'),
            'discount_percent': Decimal('20.00'),
            'description': 'Heavy gold-plated choker necklace set with 16 royal jhumka pairs for wedding functions.',
            'image_url': 'https://images.unsplash.com/photo-1599643477877-530eb83abc8e?auto=format&fit=crop&w=800&q=80',
            'is_new_arrival': True
        },
        {
            'name': 'Pearl & Polki Necklace Set With 16 Pair Earrings',
            'base_price': Decimal('4299.00'),
            'discount_percent': Decimal('15.00'),
            'description': 'Lustrous freshwater pearl necklace paired with 16 versatile Polki stone earring pairs.',
            'image_url': 'https://images.unsplash.com/photo-1611591475140-be3617c98480?auto=format&fit=crop&w=800&q=80',
            'is_featured': True
        },
        {
            'name': 'Emerald Crystal Necklace & 16 Pair Festive Box',
            'base_price': Decimal('4799.00'),
            'discount_percent': Decimal('25.00'),
            'description': 'Deep green emerald glass crystal necklace with 16 matching pair festive jhumkas.',
            'image_url': 'https://images.unsplash.com/photo-1630019852942-f89202989a59?auto=format&fit=crop&w=800&q=80',
            'is_bestseller': True
        }
    ],
    'necklace': [
        {
            'name': 'Emerald Cut Sapphire Pendant Necklace',
            'base_price': Decimal('1899.00'),
            'discount_percent': Decimal('10.00'),
            'description': 'Delicate 18K gold plated chain with a solitaire emerald-cut blue sapphire stone pendant.',
            'image_url': 'https://images.unsplash.com/photo-1599643477877-530eb83abc8e?auto=format&fit=crop&w=800&q=80',
            'is_featured': True
        },
        {
            'name': 'Royal Rajputana Gold Choker Necklace',
            'base_price': Decimal('3499.00'),
            'discount_percent': Decimal('20.00'),
            'description': 'Artisanal gold-plated choker with dangling pearl drops and intricate hand-carved filigree.',
            'image_url': 'https://images.unsplash.com/photo-1599643478518-a784e5dc4c8f?auto=format&fit=crop&w=800&q=80',
            'is_bestseller': True
        },
        {
            'name': 'Layered Layered Kundan Mala Necklace',
            'base_price': Decimal('2799.00'),
            'discount_percent': Decimal('15.00'),
            'description': 'Multi-layer pearl and Kundan long mala necklace for festive sarees and lehengas.',
            'image_url': 'https://images.unsplash.com/photo-1611591475140-be3617c98480?auto=format&fit=crop&w=800&q=80',
            'is_new_arrival': True
        },
        {
            'name': 'Modern Minimalist Solitaire Chain Necklace',
            'base_price': Decimal('1299.00'),
            'discount_percent': Decimal('5.00'),
            'description': 'Sleek silver-finish everyday pendant necklace for office and casual styling.',
            'image_url': 'https://images.unsplash.com/photo-1535632066927-ab7c9ab60908?auto=format&fit=crop&w=800&q=80',
            'is_featured': True
        }
    ],
    'bracelet': [
        {
            'name': '18K Gold Cubic Zirconia Cuff Bracelet',
            'base_price': Decimal('1499.00'),
            'discount_percent': Decimal('15.00'),
            'description': 'Elegant openable gold cuff bracelet inlaid with high-sparkle cubic zirconia crystals.',
            'image_url': 'https://images.unsplash.com/photo-1611591475140-be3617c98480?auto=format&fit=crop&w=800&q=80',
            'is_bestseller': True
        },
        {
            'name': 'Artisanal Temple Gold Kada Bracelet',
            'base_price': Decimal('1999.00'),
            'discount_percent': Decimal('20.00'),
            'description': 'Traditional antique gold floral carved kada bangle with secure clasp.',
            'image_url': 'https://images.unsplash.com/photo-1605100804763-247f67b3557e?auto=format&fit=crop&w=800&q=80',
            'is_featured': True
        },
        {
            'name': 'Pearl & Diamond Tennis Bracelet',
            'base_price': Decimal('1799.00'),
            'discount_percent': Decimal('10.00'),
            'description': 'Sophisticated tennis style bracelet studded with alternating pearls and micro diamonds.',
            'image_url': 'https://images.unsplash.com/photo-1535632066927-ab7c9ab60908?auto=format&fit=crop&w=800&q=80',
            'is_new_arrival': True
        },
        {
            'name': 'Rose Gold Clover Charm Bracelet',
            'base_price': Decimal('1299.00'),
            'discount_percent': Decimal('12.00'),
            'description': 'Trendy 4-leaf clover charm link bracelet in rose gold finish.',
            'image_url': 'https://images.unsplash.com/photo-1630019852942-f89202989a59?auto=format&fit=crop&w=800&q=80',
            'is_featured': True
        }
    ],
    '12-pair-earrings-box-with-bracelet': [
        {
            'name': '12 Pair Jhumka Set With Matching Designer Bracelet',
            'base_price': Decimal('3299.00'),
            'discount_percent': Decimal('20.00'),
            'description': 'Combo hamper containing 12 curated earring pairs and a matching gold kada bracelet.',
            'image_url': 'https://images.unsplash.com/photo-1535632066927-ab7c9ab60908?auto=format&fit=crop&w=800&q=80',
            'is_featured': True, 'is_bestseller': True
        },
        {
            'name': 'Oxidized Silver 12 Pair Box With Boho Cuff Bracelet',
            'base_price': Decimal('2699.00'),
            'discount_percent': Decimal('15.00'),
            'description': 'Bestselling oxidized silver ethnic set with 12 pair jhumkas and an adjustable tribal cuff bracelet.',
            'image_url': 'https://images.unsplash.com/photo-1605100804763-247f67b3557e?auto=format&fit=crop&w=800&q=80',
            'is_new_arrival': True
        },
        {
            'name': 'Kundan Party 12 Pair Earrings With Pearl Bracelet',
            'base_price': Decimal('3499.00'),
            'discount_percent': Decimal('25.00'),
            'description': 'Festive gift hamper featuring 12 premium Kundan earring designs and a pearl strand bracelet.',
            'image_url': 'https://images.unsplash.com/photo-1599643478518-a784e5dc4c8f?auto=format&fit=crop&w=800&q=80',
            'is_bestseller': True
        },
        {
            'name': 'Floral Enamel 12 Pair Set With Charm Bracelet',
            'base_price': Decimal('2999.00'),
            'discount_percent': Decimal('18.00'),
            'description': 'Pastel enamel hand-painted 12 pair earrings box bundled with a delicate charm bracelet.',
            'image_url': 'https://images.unsplash.com/photo-1630019852942-f89202989a59?auto=format&fit=crop&w=800&q=80',
            'is_featured': True
        }
    ],
    '16-pair-earrings-with-bracelet': [
        {
            'name': 'Grand 16 Pair Earring Collection With Royal Gold Bracelet',
            'base_price': Decimal('3999.00'),
            'discount_percent': Decimal('25.00'),
            'description': 'Luxe hamper of 16 handcrafted jhumka & stud pairs accompanied by a solid gold-finish bracelet.',
            'image_url': 'https://images.unsplash.com/photo-1605100804763-247f67b3557e?auto=format&fit=crop&w=800&q=80',
            'is_featured': True, 'is_bestseller': True
        },
        {
            'name': 'Bridal Trousseau 16 Pair Set With Zircon Bracelet',
            'base_price': Decimal('4499.00'),
            'discount_percent': Decimal('20.00'),
            'description': 'Complete wedding trousseau box offering 16 assorted earring pairs and a sparkling zircon bracelet.',
            'image_url': 'https://images.unsplash.com/photo-1599643478518-a784e5dc4c8f?auto=format&fit=crop&w=800&q=80',
            'is_new_arrival': True
        },
        {
            'name': 'Festive Fusion 16 Pair Jhumka Box With Kada Bracelet',
            'base_price': Decimal('3799.00'),
            'discount_percent': Decimal('15.00'),
            'description': 'Traditional and modern fusion 16 pair earring box with an antique carved kada bracelet.',
            'image_url': 'https://images.unsplash.com/photo-1535632066927-ab7c9ab60908?auto=format&fit=crop&w=800&q=80',
            'is_bestseller': True
        },
        {
            'name': 'Celebrity Red Carpet 16 Pair Set With Tennis Bracelet',
            'base_price': Decimal('4299.00'),
            'discount_percent': Decimal('30.00'),
            'description': 'Glamorous 16 pair earring box set paired with a luxury crystal tennis bracelet.',
            'image_url': 'https://images.unsplash.com/photo-1611591475140-be3617c98480?auto=format&fit=crop&w=800&q=80',
            'is_featured': True
        }
    ]
}

def populate():
    print("Populating Category Products...")
    brand = Brand.objects.filter(is_active=True).first()

    for slug, product_list in SAMPLE_PRODUCTS.items():
        cat = Category.objects.filter(slug=slug).first()
        if not cat:
            print(f"Category {slug} not found! Skipping.")
            continue

        for p_data in product_list:
            prod, created = Product.objects.get_or_create(
                name=p_data['name'],
                defaults={
                    'category': cat,
                    'brand': brand,
                    'base_price': p_data['base_price'],
                    'discount_percent': p_data['discount_percent'],
                    'description': p_data['description'],
                    'short_description': p_data['description'][:150],
                    'is_active': True,
                    'is_bestseller': p_data.get('is_bestseller', False),
                    'is_featured': p_data.get('is_featured', False),
                    'is_new_arrival': p_data.get('is_new_arrival', False),
                }
            )
            if not created:
                prod.category = cat
                prod.is_active = True
                prod.save()

            # Ensure image exists
            if not prod.images.exists():
                ProductImage.objects.create(
                    product=prod,
                    image_url=p_data['image_url'],
                    is_primary=True
                )
            
            # Ensure at least 1 variant exists for stock
            if not prod.variants.exists():
                ProductVariant.objects.create(
                    product=prod,
                    sku=f"SKU-{prod.id}-{uuid.uuid4().hex[:6].upper()}",
                    shade_name="Gold",
                    size="Standard",
                    stock=50,
                    is_active=True
                )
            print(f"  [{'CREATED' if created else 'UPDATED'}] '{prod.name}' -> Category '{cat.name}'")

    print("All categories populated with rich products!")

if __name__ == '__main__':
    populate()
