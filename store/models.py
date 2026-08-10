import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.text import slugify
from django.core.validators import MinValueValidator, MaxValueValidator


# Fixed list of supported languages. Using a fixed choice list (instead of a
# free-text field) so the admin panel can only ever save a real language —
# things like "australian Indian" (not a real language) can no longer be
# typed in and saved. Codes are standard ISO 639-1 codes used as translation
# dictionary keys in store/translations.py.
LANGUAGE_CHOICES = [
    ('en', 'English'),
    ('hi', 'Hindi (हिन्दी)'),
    ('zh', 'Chinese (中文)'),
    ('es', 'Spanish (Español)'),
    ('fr', 'French (Français)'),
    ('ar', 'Arabic (العربية)'),
    ('pt', 'Portuguese (Português)'),
    ('de', 'German (Deutsch)'),
    ('ja', 'Japanese (日本語)'),
    ('ru', 'Russian (Русский)'),
    ('bn', 'Bengali (বাংলা)'),
    ('ur', 'Urdu (اردو)'),
    ('id', 'Indonesian (Bahasa Indonesia)'),
    ('it', 'Italian (Italiano)'),
    ('ko', 'Korean (한국어)'),
    ('tr', 'Turkish (Türkçe)'),
    ('vi', 'Vietnamese (Tiếng Việt)'),
    ('th', 'Thai (ไทย)'),
    ('nl', 'Dutch (Nederlands)'),
    ('pl', 'Polish (Polski)'),
    ('fa', 'Persian (فارسی)'),
    ('sw', 'Swahili (Kiswahili)'),
    ('ta', 'Tamil (தமிழ்)'),
    ('te', 'Telugu (తెలుగు)'),
    ('mr', 'Marathi (मराठी)'),
    ('gu', 'Gujarati (ગુજરાતી)'),
    ('pa', 'Punjabi (ਪੰਜਾਬੀ)'),
    ('ms', 'Malay (Bahasa Melayu)'),
    ('he', 'Hebrew (עברית)'),
    ('el', 'Greek (Ελληνικά)'),
]


# NOTE: Earlier versions of this file hardcoded two demo category slugs
# (12/16-piece jhumka box set) plus fallback image URL pools so that every
# product/category without a real uploaded image would show one of two
# static hero images. That made every catalog page show duplicate images
# and made it impossible to add new categories. All of that has been
# removed — categories and products now always use whatever images are
# actually uploaded (stored in cloud Blob storage, see ProductImage.url
# and Category.display_image_url below). If no image has been uploaded,
# a clean "no image" placeholder is shown in templates instead of a fake
# product photo.



class User(AbstractUser):
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15, blank=True)
    profile_photo = models.ImageField(upload_to='profiles/', null=True, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    is_email_verified = models.BooleanField(default=False)
    otp = models.CharField(max_length=6, blank=True)
    otp_created_at = models.DateTimeField(null=True, blank=True)
    country = models.CharField(max_length=50, blank=True, help_text="Saved country preference")
    language = models.CharField(max_length=5, choices=LANGUAGE_CHOICES, blank=True, help_text="Saved language preference")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.email

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}".strip() or self.email

    def save(self, *args, **kwargs):
        if not self.username and self.email:
            self.username = self.email
        super().save(*args, **kwargs)


class CountrySetting(models.Model):
    name = models.CharField(max_length=100) # e.g., "United States"
    code = models.CharField(max_length=2, unique=True) # e.g., "US"
    currency_code = models.CharField(max_length=3, default='USD') # e.g., "USD"
    currency_symbol = models.CharField(max_length=5, default='$')
    default_language = models.CharField(max_length=5, choices=LANGUAGE_CHOICES, default='en') # Default language for this country
    shipping_charge = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def __str__(self):
        return self.name


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    country = models.ForeignKey(CountrySetting, on_delete=models.SET_NULL, null=True, blank=True)
    preferred_language = models.CharField(max_length=5, choices=LANGUAGE_CHOICES, default='en')

    def __str__(self):
        return f"{self.user.username} Profile"


class Address(models.Model):
    ADDRESS_TYPES = [('home', 'Home'), ('work', 'Work'), ('other', 'Other')]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='addresses')
    type = models.CharField(max_length=10, choices=ADDRESS_TYPES, default='home')
    full_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)
    address_line1 = models.CharField(max_length=255)
    address_line2 = models.CharField(max_length=255, blank=True)
    town = models.CharField(max_length=100, blank=True, default='')
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    pincode = models.CharField(max_length=10)
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'Addresses'

    def __str__(self):
        return f"{self.full_name} - {self.city}"


class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, max_length=255)
    image_url = models.URLField(max_length=600, blank=True, help_text="Vercel Blob storage URL (preferred)")
    image = models.ImageField(upload_to='categories/', null=True, blank=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ['name']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    @property
    def display_image_url(self):
        if self.image_url:
            return self.image_url
        if self.image:
            try:
                return self.image.url
            except Exception:
                pass
        return ""


class Brand(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, max_length=255)
    logo = models.ImageField(upload_to='brands/', null=True, blank=True)
    image_url = models.URLField(max_length=600, blank=True, help_text="Vercel Blob storage URL (preferred)")

    @property
    def logo_url(self):
        if self.image_url:
            return self.image_url
        if self.logo:
            try:
                return self.logo.url
            except ValueError:
                pass
        return ''
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Product(models.Model):
    FINISH_CHOICES = [
        ('matte', 'Matte'), ('glossy', 'Glossy'), ('satin', 'Satin'),
        ('shimmer', 'Shimmer'), ('natural', 'Natural'),
    ]
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, blank=True, max_length=255)
    brand = models.ForeignKey(Brand, on_delete=models.SET_NULL, null=True, blank=True, related_name='products')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='products')
    description = models.TextField()
    short_description = models.CharField(max_length=300, blank=True)
    ingredients = models.TextField(blank=True)
    how_to_use = models.TextField(blank=True)
    video_url = models.URLField(blank=True, help_text="YouTube or video URL")
    weight = models.CharField(max_length=100, blank=True, help_text="e.g., 5g, 10ml")
    material = models.CharField(max_length=255, blank=True, help_text="e.g., 18K Gold, Sterling Silver")
    metal_purity = models.CharField(max_length=100, blank=True, help_text="e.g., 18K Solid Gold, 925 Sterling Silver")
    warranty = models.CharField(max_length=100, blank=True, help_text="e.g., 1 Year, Lifetime")
    artisan_story = models.TextField(blank=True, help_text="Details about the craftsmanship and origin")
    base_price = models.DecimalField(max_digits=10, decimal_places=2)
    discount_percent = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    is_flash_sale = models.BooleanField(default=False, db_index=True)
    finish = models.CharField(max_length=20, choices=FINISH_CHOICES, blank=True)
    is_active = models.BooleanField(default=True, db_index=True)
    is_featured = models.BooleanField(default=False, db_index=True)
    is_new_arrival = models.BooleanField(default=False, db_index=True)
    is_bestseller = models.BooleanField(default=False, db_index=True)
    allow_personalization = models.BooleanField(default=False, help_text="Explicitly allow personalisation input for this product")
    aplus_image_url = models.URLField(max_length=600, blank=True, help_text="Upload a single long image for A+ Amazon-style content")
    view_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.name)
            slug = base
            counter = 1
            while Product.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    @property
    def is_personalizable(self):
        if self.allow_personalization:
            return True
        name_str = (self.name or '').lower()
        slug_str = (self.slug or '').lower()
        cat_name = (self.category.name or '').lower() if self.category else ''
        cat_slug = (self.category.slug or '').lower() if self.category else ''
        combined = f"{name_str} {slug_str} {cat_name} {cat_slug}"
        keywords = ['12', '16', '12-pair', '16-pair', '12-piece', '16-piece', '12 pair', '16 pair', '12pc', '16pc', 'box-set', 'custom-box']
        return any(kw in combined for kw in keywords)

    @property
    def selling_price(self):
        if self.discount_percent > 0:
            return round(self.base_price * (1 - self.discount_percent / 100), 2)
        return self.base_price

    @property
    def discount_amount(self):
        return round(self.base_price - self.selling_price, 2)

    @property
    def avg_rating(self):
        reviews = list(self.reviews.all())
        approved_reviews = [r for r in reviews if r.is_approved]
        if approved_reviews:
            avg = sum(r.rating for r in approved_reviews) / len(approved_reviews)
            return round(avg, 1)
        return 0

    @property
    def is_custom_box(self):
        if self.category and (self.category.slug == 'custom-boxes' or 'custom' in self.category.name.lower()):
            return True
        if self.slug and ('custom-12' in self.slug or 'custom-16' in self.slug or 'custom-boxes' in self.slug or 'custom-earring-box' in self.slug or self.slug.startswith('custom-')):
            return True
        if 'custom' in self.name.lower() and ('box' in self.name.lower() or 'earring' in self.name.lower()):
            return True
        return False

    @property
    def review_count(self):
        reviews = list(self.reviews.all())
        return sum(1 for r in reviews if r.is_approved)

    @property
    def total_stock(self):
        variants = list(self.variants.all())
        return sum(v.stock for v in variants)

    @property
    def primary_image(self):
        images = list(self.images.all())
        if not images:
            return None
        primary = next((img for img in images if img.is_primary), None)
        return primary or images[0]

    @property
    def display_image_url(self):
        primary = self.primary_image
        if primary and primary.url:
            return primary.url
        if self.is_custom_box:
            return "/static/images/custom-box-16pc.jpg" if "16" in str(self.slug) else "/static/images/custom-box-12pc.jpg"
        return ""

    @property
    def secondary_image_url(self):
        all_imgs = [img for img in self.images.all() if img.url]
        if len(all_imgs) > 1:
            return all_imgs[1].url
        if self.is_custom_box:
            return "/static/images/custom-box-12pc.jpg" if "16" in str(self.slug) else "/static/images/custom-box-16pc.jpg"
        return self.display_image_url

    @property
    def display_gallery_urls(self):
        urls = [img.url for img in self.images.all() if img.url]
        if urls:
            return urls
        if self.is_custom_box:
            return ["/static/images/custom-box-16pc.jpg", "/static/images/custom-box-12pc.jpg"]
        return []

    def __str__(self):
        return self.name

    def get_price_for_country(self, country_id):
        country_price = self.country_prices.filter(country_id=country_id).first()
        if country_price:
            return country_price.price
        return self.base_price


class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image_url = models.URLField(max_length=600, blank=True, help_text="Vercel Blob storage URL (preferred)")
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    image_base64 = models.TextField(blank=True, null=True)
    alt_text = models.CharField(max_length=200, blank=True)
    is_primary = models.BooleanField(default=False)
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ['order', 'id']

    def __str__(self):
        return f"{self.product.name} - Image {self.id}"

    @property
    def url(self):
        # Preferred: a real, persistent URL from Vercel Blob storage.
        if self.image_url:
            return self.image_url
        # Legacy fallback: images saved as base64 directly in the DB
        # (from before Blob storage was wired up). Still rendered so old
        # rows keep working, but new uploads should always set image_url.
        if self.image_base64:
            return f"data:image/jpeg;base64,{self.image_base64}"
        # Legacy fallback: local filesystem ImageField. This only works
        # on a persistent disk — on Vercel the filesystem is wiped on
        # every cold start, so this branch is effectively dead there.
        if self.image:
            try:
                return self.image.url
            except Exception:
                pass
        return ""


class ProductAplusImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='aplus_images')
    image_url = models.URLField(max_length=600, blank=True, help_text="Vercel Blob storage URL (preferred)")
    image = models.ImageField(upload_to='aplus_products/', blank=True, null=True)
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ['order', 'id']

    def __str__(self):
        return f"{self.product.name} - A+ Image {self.id}"

    @property
    def url(self):
        if self.image_url:
            return self.image_url
        if self.image:
            try:
                return self.image.url
            except Exception:
                pass
        return ""


class ProductVariant(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='variants')
    shade_name = models.CharField(max_length=100, blank=True)
    color_code = models.CharField(max_length=10, blank=True)
    size = models.CharField(max_length=50, blank=True)
    finish = models.CharField(max_length=50, blank=True)
    sku = models.CharField(max_length=100, unique=True, blank=True)
    additional_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    stock = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    image = models.ImageField(upload_to='variants/', null=True, blank=True)
    image_url = models.URLField(max_length=600, blank=True, help_text="Vercel Blob / R2 storage URL")
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def display_image_url(self):
        if self.image_url:
            return self.image_url
        if self.image:
            try:
                return self.image.url
            except Exception:
                pass
        return ""

    def save(self, *args, **kwargs):
        if not self.sku:
            self.sku = f"SKU-{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)

    @property
    def is_in_stock(self):
        return self.stock > 0

    @property
    def label(self):
        parts = [p for p in [self.shade_name, self.size, self.finish] if p]
        return ' / '.join(parts) or 'Default'

    def __str__(self):
        return f"{self.product.name} - {self.label}"


class Coupon(models.Model):
    DISCOUNT_TYPES = [('percent', 'Percentage'), ('flat', 'Flat Amount')]
    code = models.CharField(max_length=50, unique=True)
    discount_type = models.CharField(max_length=10, choices=DISCOUNT_TYPES)
    discount_value = models.DecimalField(max_digits=10, decimal_places=2)
    minimum_order_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    max_discount_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    usage_limit = models.PositiveIntegerField(default=0)
    used_count = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    valid_from = models.DateTimeField()
    valid_to = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.code

    def is_valid(self):
        from django.utils import timezone
        now = timezone.now()
        return (
            self.is_active and
            self.valid_from <= now <= self.valid_to and
            (self.usage_limit == 0 or self.used_count < self.usage_limit)
        )


class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='cart', null=True, blank=True)
    session_key = models.CharField(max_length=40, null=True, blank=True)
    coupon = models.ForeignKey(Coupon, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Cart - {self.user or self.session_key}"

    @property
    def total_items(self):
        return sum(item.quantity for item in self.items.all())

    @property
    def subtotal(self):
        return sum(item.total_price for item in self.items.all())

    @property
    def discount_amount(self):
        if not self.coupon or not self.coupon.is_valid():
            return 0
        sub = self.subtotal
        if self.coupon.discount_type == 'percent':
            disc = sub * self.coupon.discount_value / 100
            if self.coupon.max_discount_amount:
                disc = min(disc, self.coupon.max_discount_amount)
            return round(disc, 2)
        return min(self.coupon.discount_value, sub)

    @property
    def grand_total(self):
        return self.subtotal - self.discount_amount + self.delivery_charge

    @property
    def delivery_charge(self):
        return 0


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    variant = models.ForeignKey(ProductVariant, on_delete=models.CASCADE, null=True, blank=True)
    personalization_name = models.CharField(max_length=255, blank=True, default='', verbose_name="Name for Personalisation")
    quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('cart', 'product', 'variant', 'personalization_name')

    @property
    def unit_price(self):
        base = self.product.selling_price
        if self.variant:
            base += self.variant.additional_price
        return base

    @property
    def total_price(self):
        return self.unit_price * self.quantity

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"


class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'), ('confirmed', 'Confirmed'),
        ('processing', 'Processing'), ('shipped', 'Shipped'),
        ('out_for_delivery', 'Out for Delivery'), ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'), ('returned', 'Returned'),
    ]
    order_id = models.CharField(max_length=20, unique=True, blank=True)
    shipping_tracking_id = models.CharField(max_length=100, blank=True, help_text="Shiprocket Shipment ID / AWB")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    address = models.ForeignKey(Address, on_delete=models.SET_NULL, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', db_index=True)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    delivery_charge = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    grand_total = models.DecimalField(max_digits=10, decimal_places=2)
    coupon = models.ForeignKey(Coupon, on_delete=models.SET_NULL, null=True, blank=True)
    notes = models.TextField(blank=True)
    guest_email = models.EmailField(max_length=255, blank=True, null=True, help_text="Email captured during guest checkout")
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.order_id:
            import time
            ts_hex = f"{int(time.time()):X}"
            rnd_hex = uuid.uuid4().hex[:4].upper()
            self.order_id = f"HH{ts_hex}{rnd_hex}"
        super().save(*args, **kwargs)

    def __str__(self):
        return self.order_id

    @property
    def is_cancellable(self):
        return self.status in ['pending', 'confirmed']

    @property
    def is_returnable(self):
        return False

    @property
    def shiprocket_tracking_url(self):
        """
        Returns Shiprocket Official Live Tracking URL for this store.
        """
        return "https://hypehavenhub.shiprocket.co/"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    variant = models.ForeignKey(ProductVariant, on_delete=models.SET_NULL, null=True, blank=True)
    product_name = models.CharField(max_length=255)
    variant_label = models.CharField(max_length=100, blank=True)
    personalization_name = models.CharField(max_length=255, blank=True, default='', verbose_name="Name for Personalisation")
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.product_name} x {self.quantity}"


class Payment(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'), ('success', 'Success'),
        ('failed', 'Failed'), ('refunded', 'Refunded'),
    ]
    METHOD_CHOICES = [
        ('upi', 'UPI'), ('card', 'Card'), ('netbanking', 'Net Banking'),
        ('wallet', 'Wallet'), ('cod', 'Cash on Delivery'),
    ]
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='payment')
    payment_id = models.CharField(max_length=100, unique=True, blank=True)
    method = models.CharField(max_length=20, choices=METHOD_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    gateway_response = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.payment_id:
            self.payment_id = f"PAY-{uuid.uuid4().hex[:10].upper()}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.payment_id} - {self.status}"


class OrderTracking(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='tracking')
    status = models.CharField(max_length=30)
    description = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"{self.order.order_id} - {self.status}"


class Review(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')
    rating = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    title = models.CharField(max_length=200)
    body = models.TextField()
    is_approved = models.BooleanField(default=True)
    is_verified_purchase = models.BooleanField(default=False)
    helpful_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('product', 'user')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.email} - {self.product.name} ({self.rating}*)"


class ReviewImage(models.Model):
    review = models.ForeignKey(Review, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='reviews/')
    image_url = models.URLField(max_length=600, blank=True, help_text="Vercel Blob storage URL (preferred)")

    @property
    def display_image_url(self):
        if self.image_url:
            return self.image_url
        if self.image:
            try:
                return self.image.url
            except ValueError:
                pass
        return ''

    def __str__(self):
        return f"Image for review {self.review.id}"


class Wishlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='wishlist')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'product')

    def __str__(self):
        return f"{self.user.email} - {self.product.name}"


class ReturnRequest(models.Model):
    STATUS_CHOICES = [
        ('requested', 'Requested'), ('approved', 'Approved'),
        ('picked_up', 'Picked Up'), ('refunded', 'Refunded'), ('rejected', 'Rejected'),
    ]
    REASON_CHOICES = [
        ('damaged', 'Jewelry is Damaged'), ('wrong', 'Wrong Jewelry Delivered'),
        ('not_as_described', 'Not as Described'), ('expired', 'Quality Issue'), ('other', 'Other'),
    ]
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='returns')
    order_item = models.ForeignKey(OrderItem, on_delete=models.CASCADE, null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    reason = models.CharField(max_length=30, choices=REASON_CHOICES)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='requested')
    refund_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Return - {self.order.order_id}"


class Notification(models.Model):
    TYPES = [('order', 'Order Update'), ('offer', 'Offer / Discount'), ('general', 'General')]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    type = models.CharField(max_length=20, choices=TYPES, default='general')
    title = models.CharField(max_length=200)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    link = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.email} - {self.title}"


class UserPreference(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='preferences')
    email_order_updates = models.BooleanField(default=True)
    email_promotions = models.BooleanField(default=True)
    sms_order_updates = models.BooleanField(default=True)
    sms_promotions = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Preferences - {self.user.email}"


class FlashSale(models.Model):
    end_time = models.DateTimeField()
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"Flash Sale ends at {self.end_time}"


class Complaint(models.Model):
    STATUS_CHOICES = [
        ('open', 'Open'), ('in_progress', 'In Progress'),
        ('resolved', 'Resolved'), ('closed', 'Closed'),
    ]
    COMPLAINT_TYPE_CHOICES = [
        ('product_quality', 'Product Quality'), ('delivery', 'Delivery Issue'),
        ('payment', 'Payment Issue'), ('account', 'Account Issue'),
        ('website', 'Website Issue'), ('other', 'Other'),
    ]
    
    complaint_id = models.CharField(max_length=20, unique=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='complaints')
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True, blank=True, related_name='complaints')
    complaint_type = models.CharField(max_length=30, choices=COMPLAINT_TYPE_CHOICES)
    subject = models.CharField(max_length=255)
    description = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
    admin_response = models.TextField(blank=True)
    priority = models.CharField(max_length=10, choices=[('low', 'Low'), ('medium', 'Medium'), ('high', 'High')], default='medium')
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_complaints')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    resolved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.complaint_id:
            self.complaint_id = f"CP{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.complaint_id} - {self.subject}"


class AdminDashboardStats(models.Model):
    """Cache for dashboard statistics - updated periodically"""
    date = models.DateField(auto_now_add=True, unique=True)
    total_orders = models.PositiveIntegerField(default=0)
    total_revenue = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    total_users = models.PositiveIntegerField(default=0)
    new_orders_today = models.PositiveIntegerField(default=0)
    total_products = models.PositiveIntegerField(default=0)
    returned_orders = models.PositiveIntegerField(default=0)
    total_complaints = models.PositiveIntegerField(default=0)
    open_complaints = models.PositiveIntegerField(default=0)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Dashboard Stats"
        ordering = ['-date']

    def __str__(self):
        return f"Stats - {self.date}"

class ProductPrice(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='country_prices')
    country = models.ForeignKey(CountrySetting, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2) # e.g., India ke liye 999, US ke liye 30

    class Meta:
        unique_together = ('product', 'country')

    def __str__(self):
        return f"{self.product.name} - {self.country.code} ({self.price})"


class SiteSetting(models.Model):
    """Singleton model for global site settings"""
    announcement_text = models.CharField(max_length=255, default="WILL YOU BE MY CUSTOMER 😍 IF YES THEN SCROLL DOWN AND BUY MY PRODUCT 🛍️")
    marquee_text = models.TextField(default="FREE Shipping on orders above ₹499 ✦ Use Code JHUMKA10 ✦ Authentic Oxidised Silver ✦ Free Delivery Above ₹499 ✦ Use Code JHUMKA10 ✦ Authentic Oxidised Silver ✦")
    
    class Meta:
        verbose_name = "Site Setting"
        verbose_name_plural = "Site Settings"
        
    def __str__(self):
        return "Global Site Settings"


class HeroPanel(models.Model):
    """Model for dynamic hero slider panels"""
    title = models.CharField(max_length=100, blank=True, help_text="Title / Label (e.g. Ruby Stone Long Jhumka)")
    background_text = models.CharField(max_length=200, blank=True, help_text="Text shown behind photo in hero animation (Ghost Text)")
    image = models.ImageField(upload_to='hero_panels/', blank=True, null=True, help_text="Upload image file directly from admin")
    image_url = models.URLField(max_length=600, blank=True, help_text="Vercel Blob/Cloudflare R2 storage URL (alternative)")
    bg_color = models.CharField(max_length=20, default="#7C1F45", help_text="Hero section background color hex e.g. #7C1F45")
    panel_color = models.CharField(max_length=20, default="#9A2E5B", help_text="Secondary panel color hex e.g. #9A2E5B")
    link = models.CharField(max_length=500, blank=True, help_text="Where should this panel redirect when clicked?")
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0, help_text="Order in which this panel appears")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order', '-created_at']
        verbose_name = "Hero Panel"
        verbose_name_plural = "Hero Panels"

    def __str__(self):
        return self.title or f"Hero Panel {self.id}"

    @property
    def display_image_url(self):
        if self.image:
            return self.image.url
        return self.image_url if self.image_url else ''

    @property
    def display_word(self):
        if self.background_text:
            return self.background_text.upper()
        return (self.title or "").upper()



class ProductQuestion(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='questions')
    question = models.TextField()
    email = models.EmailField()
    display_name = models.CharField(max_length=100)
    is_answered = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Question by {self.display_name} on {self.product.name}"


class CustomEarring(models.Model):
    """Single earring photos uploaded by admin for the customizer."""
    name = models.CharField(max_length=150, blank=True, default='')
    image_url = models.URLField(max_length=600, help_text="Cloudflare R2 image URL")
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0, help_text="Display order")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order', '-created_at']
        verbose_name = "Custom Earring"
        verbose_name_plural = "Custom Earrings"

    def __str__(self):
        return self.name or f"Earring #{self.pk}"


BOX_TYPE_CHOICES = [
    ('12', '12 Pairs'),
    ('16', '16 Pairs'),
]


class CustomBoxPricing(models.Model):
    """Admin-configurable pricing for custom earring boxes."""
    box_type = models.CharField(max_length=2, choices=BOX_TYPE_CHOICES, unique=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, help_text="Price in INR")
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Custom Box Pricing"
        verbose_name_plural = "Custom Box Pricing"

    def __str__(self):
        return f"{self.get_box_type_display()} — ₹{self.price}"


class CustomBoxOrder(models.Model):
    """Tracks which earrings a customer selected in their custom box order."""
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='custom_box')
    box_type = models.CharField(max_length=2, choices=BOX_TYPE_CHOICES)
    selected_earrings = models.ManyToManyField(CustomEarring, related_name='custom_orders')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Custom Box Order"
        verbose_name_plural = "Custom Box Orders"

    def __str__(self):
        return f"Custom {self.get_box_type_display()} — {self.order.order_id}"

