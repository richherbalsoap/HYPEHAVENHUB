from __future__ import annotations

from decimal import Decimal
from io import BytesIO

from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand, CommandError
from django.utils.text import slugify

from store.models import (
    Brand,
    Category,
    JEWELRY_CATEGORY_SLUGS,
    Product,
    ProductImage,
    ProductVariant,
    SubCategory,
)


class Command(BaseCommand):
    help = "Create the two jhumka box set products with local PNG images."

    def add_arguments(self, parser):
        parser.add_argument(
            "--count",
            type=int,
            default=10,
            help="Number of products to create.",
        )
        parser.add_argument(
            "--replace",
            action="store_true",
            help="Deactivate existing catalog records before seeding the jewelry catalog.",
        )

    def handle(self, *args, **options):
        try:
            from PIL import Image, ImageDraw, ImageFont
        except Exception as exc:  # pragma: no cover
            raise CommandError(f"Pillow is required to generate images: {exc}") from exc

        self.image_lib = (Image, ImageDraw, ImageFont)
        catalog = self._catalog()
        count = max(1, min(options["count"], len(catalog)))
        catalog = catalog[:count]
        created_products = 0
        updated_products = 0

        if options["replace"]:
            Product.objects.update(is_active=False)
            Category.objects.update(is_active=False)
            SubCategory.objects.update(is_active=False)
            Brand.objects.update(is_active=False)

        for idx, item in enumerate(catalog, start=1):
            category = self._get_or_create_category(item["category"], item["c1"], item["c2"])
            subcategory = None
            if item.get("subcategory"):
                subcategory = self._get_or_create_subcategory(category, item["subcategory"])
            brand = self._get_or_create_brand(item["brand"])

            product, created = Product.objects.update_or_create(
                slug=slugify(item["name"]),
                defaults={
                    "name": item["name"],
                    "brand": brand,
                    "category": category,
                    "subcategory": subcategory,
                    "description": item["description"],
                    "short_description": item["short_description"],
                    "ingredients": item["ingredients"],
                    "how_to_use": item["how_to_use"],
                    "base_price": Decimal(item["price"]),
                    "discount_percent": Decimal(item["discount"]),
                    "finish": item["finish"],
                    "is_active": True,
                    "is_featured": True,
                    "is_new_arrival": idx == 2,
                    "is_bestseller": idx == 1,
                    "is_flash_sale": False,
                },
            )

            if created:
                created_products += 1
            else:
                updated_products += 1

            if options["replace"]:
                product.images.all().delete()

            if not product.images.exists():
                primary = self._build_image_file(
                    title=item["name"],
                    subtitle=item["brand"],
                    color_a=item["c1"],
                    color_b=item["c2"],
                    filename=f"{product.slug}-primary.png",
                )
                ProductImage.objects.create(
                    product=product,
                    image=primary,
                    alt_text=f"{product.name} primary image",
                    is_primary=True,
                    order=0,
                )

                detail = self._build_image_file(
                    title=item["name"],
                    subtitle=item.get("image_subtitle", "Jhumka Box"),
                    color_a=item["c2"],
                    color_b=item["c1"],
                    filename=f"{product.slug}-detail.png",
                )
                ProductImage.objects.create(
                    product=product,
                    image=detail,
                    alt_text=f"{product.name} detail image",
                    is_primary=False,
                    order=1,
                )

            variant, _ = ProductVariant.objects.get_or_create(
                product=product,
                shade_name=item["variant_name"],
                defaults={
                    "color_code": item["variant_color"],
                    "size": item["variant_size"],
                    "finish": item["finish"],
                    "stock": item["stock"],
                    "additional_price": Decimal("0.00"),
                    "is_active": True,
                },
            )
            variant.color_code = item["variant_color"]
            variant.size = item["variant_size"]
            variant.finish = item["finish"]
            variant.stock = item["stock"]
            variant.is_active = True
            variant.save()

        Product.objects.filter(is_active=True).exclude(
            category__slug__in=JEWELRY_CATEGORY_SLUGS
        ).update(is_active=False)
        SubCategory.objects.filter(is_active=True).exclude(
            category__slug__in=JEWELRY_CATEGORY_SLUGS
        ).update(is_active=False)
        Category.objects.filter(is_active=True).exclude(
            slug__in=JEWELRY_CATEGORY_SLUGS
        ).update(is_active=False)

        self.stdout.write(
            self.style.SUCCESS(
                f"Jewelry products ready: created={created_products}, updated={updated_products}, total_seeded={count}"
            )
        )

    def _build_image_file(self, title: str, subtitle: str, color_a: str, color_b: str, filename: str) -> ContentFile:
        Image, ImageDraw, ImageFont = self.image_lib
        width, height = 1200, 1200
        img = Image.new("RGB", (width, height), color_a)
        draw = ImageDraw.Draw(img)
        c1 = self._hex_to_rgb(color_a)
        c2 = self._hex_to_rgb(color_b)

        for y in range(height):
            ratio = y / (height - 1)
            color = (
                int(c1[0] * (1 - ratio) + c2[0] * ratio),
                int(c1[1] * (1 - ratio) + c2[1] * ratio),
                int(c1[2] * (1 - ratio) + c2[2] * ratio),
            )
            draw.line((0, y, width, y), fill=color)

        try:
            title_font = ImageFont.truetype("arial.ttf", 76)
            subtitle_font = ImageFont.truetype("arial.ttf", 42)
            badge_font = ImageFont.truetype("arial.ttf", 32)
        except OSError:
            title_font = ImageFont.load_default()
            subtitle_font = ImageFont.load_default()
            badge_font = ImageFont.load_default()

        gold = (230, 184, 92)
        soft_gold = (255, 224, 151)
        ivory = (255, 250, 240)
        charcoal = (38, 31, 35)

        draw.rounded_rectangle((78, 78, 1122, 1122), radius=34, outline=soft_gold, width=7)
        draw.rounded_rectangle((130, 150, 1070, 1045), radius=36, fill=ivory, outline=(255, 255, 255), width=3)
        draw.text((178, 232), "GLAMOUR JEWELS", fill=gold, font=badge_font)
        draw.text((178, 336), title[:30], fill=charcoal, font=title_font)
        draw.text((178, 456), subtitle[:30], fill=(106, 80, 74), font=subtitle_font)

        count = 16 if "16" in title else 12
        cols = 4
        rows = count // cols
        box_left, box_top = 620, 565
        box_right, box_bottom = 1060, 1010
        cell_w = (box_right - box_left - 48) / cols
        cell_h = (box_bottom - box_top - 48) / rows

        draw.rounded_rectangle(
            (box_left, box_top, box_right, box_bottom),
            radius=28,
            fill=(255, 248, 236),
            outline=gold,
            width=8,
        )
        draw.rounded_rectangle(
            (box_left + 18, box_top + 18, box_right - 18, box_bottom - 18),
            radius=20,
            outline=(240, 218, 171),
            width=3,
        )

        jewel_colors = [
            soft_gold,
            (247, 180, 203),
            (196, 231, 217),
            (244, 207, 119),
            (226, 185, 230),
            (245, 225, 186),
        ]
        item_index = 0
        for row in range(rows):
            for col in range(cols):
                if item_index >= count:
                    break
                cx = int(box_left + 36 + (col * cell_w) + cell_w / 2)
                cy = int(box_top + 36 + (row * cell_h) + cell_h / 2)
                tone = jewel_colors[item_index % len(jewel_colors)]
                draw.ellipse((cx - 22, cy - 42, cx + 22, cy + 2), fill=tone, outline=gold, width=4)
                draw.pieslice((cx - 34, cy - 2, cx + 34, cy + 72), start=180, end=360, fill=gold, outline=gold)
                draw.ellipse((cx - 13, cy + 38, cx + 13, cy + 64), fill=ivory, outline=(214, 162, 72), width=3)
                draw.ellipse((cx - 6, cy - 20, cx + 6, cy - 8), fill=ivory)
                item_index += 1

        draw.rounded_rectangle((178, 586, 496, 686), radius=22, fill=charcoal)
        draw.text((208, 615), f"{count} PIECE BOX", fill=soft_gold, font=badge_font)

        buffer = BytesIO()
        img.save(buffer, format="PNG")
        return ContentFile(buffer.getvalue(), name=filename)

    @staticmethod
    def _hex_to_rgb(value: str) -> tuple[int, int, int]:
        value = value.lstrip("#")
        return (int(value[0:2], 16), int(value[2:4], 16), int(value[4:6], 16))

    def _get_or_create_category(self, name: str, color_a: str, color_b: str) -> Category:
        category, _ = Category.objects.get_or_create(
            slug=slugify(name),
            defaults={"name": name, "description": f"{name} jewelry", "is_active": True},
        )
        category.name = name
        category.description = f"Curated {name.lower()} designs for festive, bridal, and daily styling."
        category.is_active = True
        category.save(update_fields=["name", "description", "is_active"])
        if not category.image:
            category_image = self._build_image_file(
                title=name,
                subtitle="Category",
                color_a=color_a,
                color_b=color_b,
                filename=f"category-{category.slug}.png",
            )
            category.image.save(category_image.name, category_image, save=True)
        return category

    @staticmethod
    def _get_or_create_subcategory(category: Category, name: str) -> SubCategory:
        subcategory, _ = SubCategory.objects.get_or_create(
            category=category,
            slug=slugify(name),
            defaults={"name": name, "is_active": True},
        )
        subcategory.name = name
        subcategory.is_active = True
        subcategory.save(update_fields=["name", "is_active"])
        return subcategory

    @staticmethod
    def _get_or_create_brand(name: str) -> Brand:
        brand, _ = Brand.objects.get_or_create(
            slug=slugify(name),
            defaults={"name": name, "description": f"{name} jewelry", "is_active": True},
        )
        brand.name = name
        brand.description = f"{name} handcrafted fashion jewelry."
        brand.is_active = True
        brand.save(update_fields=["name", "description", "is_active"])
        return brand

    @staticmethod
    def _catalog() -> list[dict[str, str]]:
        return [
            {
                "name": "12 Piece Jhumka Box Set",
                "category": "12 Piece Jhumka Box Set",
                "subcategory": "",
                "brand": "HYPEHAVENHUB",
                "price": "599.00",
                "discount": "10.00",
                "finish": "shimmer",
                "variant_name": "Assorted Jhumka Box",
                "variant_color": "#d8ad4f",
                "variant_size": "12 Pieces",
                "stock": 75,
                "c1": "#3b2432",
                "c2": "#d8ad4f",
                "short_description": "A ready box of 12 assorted jhumka pieces for daily, festive, and gifting use.",
                "description": "This 12 piece jhumka box set brings together assorted lightweight designs in one neat box. It is made for resellers, gifting, college wear, festive styling, and quick outfit matching.",
                "ingredients": "Alloy base, enamel accents, faux pearls, crystal-style stones, and gold-tone polish. Keep away from perfume, sweat, and water.",
                "how_to_use": "Store every jhumka in the box after use. Mix the designs with kurtis, sarees, lehengas, and casual ethnic outfits.",
                "image_subtitle": "12 Pieces",
            },
            {
                "name": "16 Piece Jhumka Box Set",
                "category": "16 Piece Jhumka Box Set",
                "subcategory": "",
                "brand": "HYPEHAVENHUB",
                "price": "799.00",
                "discount": "12.00",
                "finish": "glossy",
                "variant_name": "Premium Assorted Box",
                "variant_color": "#c96f90",
                "variant_size": "16 Pieces",
                "stock": 60,
                "c1": "#c9348f",
                "c2": "#f3c15f",
                "short_description": "A fuller 16 piece jhumka box set with assorted colors and festive designs.",
                "description": "This 16 piece jhumka box set gives more variety in one premium box, with assorted colors, pearl looks, and festive-ready patterns for daily sales, gifting, and outfit styling.",
                "ingredients": "Alloy base, enamel accents, faux pearls, crystal-style stones, and gold-tone polish. Keep dry and store inside the box.",
                "how_to_use": "Choose a pair by outfit color, then place it back in its slot after use. Ideal for boutique display, gifting, and regular ethnic wear.",
                "image_subtitle": "16 Pieces",
            },
        ]
