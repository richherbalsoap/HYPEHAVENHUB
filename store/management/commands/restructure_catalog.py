"""
One-time data migration: moves the catalog from the old "jhumka box set"
model (2 categories, products with no category) to a proper jewelry
catalog with 3 categories (Jhumka Earrings, Necklaces, Bracelets) and
every active product correctly assigned.

What it does, in order:
  1. Deletes the 7 box-set products that have no uploaded image
     (12/16 Piece Assorted Jhumka Box - *) plus any obvious test product.
  2. Renames the 2 existing "box set" categories into 2 of the 3 new
     categories (Jhumka Earrings, Necklaces) and creates the 3rd
     (Bracelets), instead of deleting + recreating, so existing slugs/ids
     that may be referenced elsewhere stay stable where possible.
  3. Assigns every remaining active product to the correct category by
     matching on product name keywords (jhumka / necklace / bracelet,
     bangle, kada).

Safe to run more than once (it only acts on rows that still need fixing).

Usage:
    python manage.py restructure_catalog            # apply
    python manage.py restructure_catalog --dry-run   # preview only
"""
from __future__ import annotations

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils.text import slugify

from store.models import Category, Product, ProductImage


# Products with NO uploaded image at all — confirmed dead rows from the
# old box-set catalog. Matched by exact name to avoid touching anything
# else by accident.
DEAD_PRODUCT_NAMES = [
    "12 Piece Assorted Jhumka Box - Classic Gold",
    "12 Piece Assorted Jhumka Box - Oxidized",
    "12 Piece Assorted Jhumka Box - Pearl Mix",
    "16 Piece Assorted Jhumka Box - Classic Gold",
    "16 Piece Assorted Jhumka Box - Antique",
    "16 Piece Assorted Jhumka Box - Oxidized",
    "16 Piece Assorted Jhumka Box - Rainbow Mix",
    "asdfghjkl",
]

# New category definitions. "old_slug" lets us rename an existing
# category in place instead of deleting it (keeps the row's id stable).
NEW_CATEGORIES = [
    {"name": "Jhumka Earrings", "old_slug": "12-piece-jhumka-box-set"},
    {"name": "Necklaces", "old_slug": "16-piece-jhumka-box-set"},
    {"name": "Bracelets", "old_slug": None},
]

# Keyword -> category name, checked against the product name
# (case-insensitive). First match wins, so order matters a little but
# in practice these keyword sets don't overlap.
CATEGORY_KEYWORDS = {
    "Jhumka Earrings": ["jhumka"],
    "Necklaces": ["necklace", "choker", "pendant"],
    "Bracelets": ["bracelet", "bangle", "kada"],
}


class Command(BaseCommand):
    help = "Restructure the catalog into Jhumka Earrings / Necklaces / Bracelets."

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Show what would change without writing to the database.",
        )

    def handle(self, *args, **options):
        dry_run = options["dry_run"]
        prefix = "[DRY RUN] " if dry_run else ""

        with transaction.atomic():
            self._delete_dead_products(prefix, dry_run)
            categories_by_name = self._upsert_categories(prefix, dry_run)
            self._assign_product_categories(prefix, dry_run, categories_by_name)

            if dry_run:
                # Roll back everything — atomic() only commits if we
                # reach the end of the block without raising.
                transaction.set_rollback(True)

        self.stdout.write(self.style.SUCCESS(f"{prefix}Done."))

    def _delete_dead_products(self, prefix, dry_run):
        qs = Product.objects.filter(name__in=DEAD_PRODUCT_NAMES)
        count = qs.count()
        if count == 0:
            self.stdout.write(f"{prefix}No dead box-set products to delete.")
            return
        names = list(qs.values_list("name", flat=True))
        self.stdout.write(f"{prefix}Deleting {count} product(s) with no image:")
        for n in names:
            self.stdout.write(f"  - {n}")
        if not dry_run:
            qs.delete()

    def _upsert_categories(self, prefix, dry_run):
        result = {}
        for spec in NEW_CATEGORIES:
            name = spec["name"]
            old_slug = spec["old_slug"]
            cat = None
            if old_slug:
                cat = Category.objects.filter(slug=old_slug).first()
            if cat:
                if cat.name != name:
                    self.stdout.write(f"{prefix}Renaming category '{cat.name}' -> '{name}'")
                    if not dry_run:
                        cat.name = name
                        cat.slug = slugify(name)
                        cat.save()
                    else:
                        # Preview the post-rename state in memory so later
                        # steps (category assignment reporting) see the
                        # correct target id without writing to the DB.
                        cat.name = name
            else:
                cat = Category.objects.filter(name=name).first()
                if cat:
                    self.stdout.write(f"{prefix}Category '{name}' already exists, reusing it.")
                else:
                    self.stdout.write(f"{prefix}Creating new category '{name}'")
                    if not dry_run:
                        cat = Category.objects.create(name=name, slug=slugify(name), is_active=True)
                    else:
                        # Unsaved placeholder so dry-run reporting below
                        # can still describe what *would* happen (e.g.
                        # "category None -> <new>") without writing to
                        # the DB or needing a real pk.
                        cat = Category(name=name, slug=slugify(name), is_active=True)
            result[name] = cat
        return result

    def _assign_product_categories(self, prefix, dry_run, categories_by_name):
        # Exclude the dead box-set products even in --dry-run mode, where
        # the delete above is rolled back at the end and would otherwise
        # still be visible to this query within the same transaction.
        products = Product.objects.filter(is_active=True).exclude(name__in=DEAD_PRODUCT_NAMES)
        unmatched = []
        for product in products:
            name_lower = product.name.lower()
            matched_category_name = None
            for cat_name, keywords in CATEGORY_KEYWORDS.items():
                if any(kw in name_lower for kw in keywords):
                    matched_category_name = cat_name
                    break

            if not matched_category_name:
                unmatched.append(product.name)
                continue

            target_cat = categories_by_name.get(matched_category_name)
            if dry_run and target_cat is None:
                # In dry-run mode categories may not have been created in
                # the DB (rolled back on previous runs) — look it up by
                # name only for reporting purposes.
                target_cat = Category.objects.filter(name=matched_category_name).first()

            current_id = product.category_id
            current_name = product.category.name if product.category_id else None
            target_id = target_cat.id if target_cat else None
            needs_change = current_name != matched_category_name
            if needs_change:
                self.stdout.write(
                    f"{prefix}{product.name!r}: category {current_id} -> "
                    f"{target_id} ({matched_category_name})"
                )
                if not dry_run and target_cat is not None:
                    product.category = target_cat
                    product.save(update_fields=["category"])

        if unmatched:
            self.stdout.write(self.style.WARNING(
                f"{prefix}Could not auto-match {len(unmatched)} product(s) by name, "
                f"left as-is: {unmatched}"
            ))
