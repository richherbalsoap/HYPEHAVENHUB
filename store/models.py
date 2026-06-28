import uuid
import hashlib
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.text import slugify
from django.core.validators import MinValueValidator, MaxValueValidator


def _pexels_url(photo_id):
    return f"https://images.pexels.com/photos/{photo_id}/pexels-photo-{photo_id}.jpeg?auto=compress&cs=tinysrgb&w=1200"


def _unsplash_url(photo_id, width=1200):
    return f"https://images.unsplash.com/{photo_id}?auto=format&fit=crop&w={width}&q=82"


def _stable_gallery(url_pool, seed, count=3):
    if not url_pool:
        return []
    digest = hashlib.md5(seed.encode("utf-8")).hexdigest()
    start = int(digest[:8], 16) % len(url_pool)
    rotated = url_pool[start:] + url_pool[:start]
    result = rotated[:count]
    while len(result) < count:
        result += rotated[: count - len(result)]
    return result


REAL_CATEGORY_IMAGE_URLS = {
    "12-piece-jhumka-box-set": "/static/images/hero-jhumka-large.jpeg",
    "16-piece-jhumka-box-set": "/static/images/hero-jhumka-small.jpeg",
}

JEWELRY_CATEGORY_SLUGS = (
    "12-piece-jhumka-box-set",
    "16-piece-jhumka-box-set",
)

CATEGORY_PRODUCT_IMAGE_POOLS = {
    "12-piece-jhumka-box-set": ["/static/images/hero-jhumka-large.jpeg"],
    "16-piece-jhumka-box-set": ["/static/images/hero-jhumka-small.jpeg"],
}
DEFAULT_PRODUCT_IMAGE_POOL = []

REAL_PRODUCT_IMAGE_URLS = {
    "12-piece-assorted-jhumka-box-classic-gold": [
        "/static/images/hero-jhumka-large.jpeg",
        "/static/images/hero-jhumka-small.jpeg"
    ],
    "12-piece-assorted-jhumka-box-oxidized": [
        "/static/images/hero-jhumka-large.jpeg",
        "/static/images/hero-jhumka-small.jpeg"
    ],
    "12-piece-assorted-jhumka-box-pearl-mix": [
        "/static/images/hero-jhumka-large.jpeg",
        "/static/images/hero-jhumka-small.jpeg"
    ],
    "16-piece-assorted-jhumka-box-classic-gold": [
        "/static/images/hero-jhumka-small.jpeg",
        "/static/images/hero-jhumka-large.jpeg"
    ],
    "16-piece-assorted-jhumka-box-antique": [
        "/static/images/hero-jhumka-small.jpeg",
        "/static/images/hero-jhumka-large.jpeg"
    ],
    "16-piece-assorted-jhumka-box-oxidized": [
        "/static/images/hero-jhumka-small.jpeg",
        "/static/images/hero-jhumka-large.jpeg"
    ],
    "16-piece-assorted-jhumka-box-rainbow-mix": [
        "/static/images/hero-jhumka-small.jpeg",
        "/static/images/hero-jhumka-large.jpeg"
    ]
}



class User(AbstractUser):
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15, blank=True)
    profile_photo = models.ImageField(upload_to='profiles/', null=True, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    is_email_verified = models.BooleanField(default=False)
    otp = models.CharField(max_length=6, blank=True)
    otp_created_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.email

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}".strip() or self.email


class Address(models.Model):
    ADDRESS_TYPES = [('home', 'Home'), ('work', 'Work'), ('other', 'Other')]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='addresses')
    type = models.CharField(max_length=10, choices=ADDRESS_TYPES, default='home')
    full_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)
    address_line1 = models.CharField(max_length=255)
    address_line2 = models.CharField(max_length=255, blank=True)
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
        return (self.image.url if self.image else "") or REAL_CATEGORY_IMAGE_URLS.get(self.slug, "")


class SubCategory(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='subcategories')
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=255)
    image = models.ImageField(upload_to='subcategories/', null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'Sub Categories'
        unique_together = ('category', 'slug')
        ordering = ['name']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.category.name} > {self.name}"


class Brand(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, max_length=255)
    logo = models.ImageField(upload_to='brands/', null=True, blank=True)
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
    subcategory = models.ForeignKey(SubCategory, on_delete=models.SET_NULL, null=True, blank=True, related_name='products')
    description = models.TextField()
    short_description = models.CharField(max_length=300, blank=True)
    ingredients = models.TextField(blank=True)
    how_to_use = models.TextField(blank=True)
    video_url = models.URLField(blank=True, help_text="YouTube or video URL")
    weight = models.CharField(max_length=100, blank=True, help_text="e.g., 5g, 10ml")
    material = models.CharField(max_length=255, blank=True, help_text="e.g., 18K Gold, Sterling Silver")
    warranty = models.CharField(max_length=100, blank=True, help_text="e.g., 1 Year, Lifetime")
    base_price = models.DecimalField(max_digits=10, decimal_places=2)
    discount_percent = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    is_flash_sale = models.BooleanField(default=False)
    finish = models.CharField(max_length=20, choices=FINISH_CHOICES, blank=True)
    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    is_new_arrival = models.BooleanField(default=False)
    is_bestseller = models.BooleanField(default=False)
    view_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
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
    def selling_price(self):
        if self.discount_percent > 0:
            return round(self.base_price * (1 - self.discount_percent / 100), 2)
        return self.base_price

    @property
    def discount_amount(self):
        return round(self.base_price - self.selling_price, 2)

    @property
    def avg_rating(self):
        reviews = self.reviews.filter(is_approved=True)
        if reviews.exists():
            avg = reviews.aggregate(models.Avg('rating'))['rating__avg']
            return round(avg, 1)
        return 0

    @property
    def review_count(self):
        return self.reviews.filter(is_approved=True).count()

    @property
    def total_stock(self):
        return sum(v.stock for v in self.variants.all())

    @property
    def primary_image(self):
        img = self.images.filter(is_primary=True).first()
        if not img:
            img = self.images.first()
        return img

    @property
    def display_image_url(self):
        primary = self.primary_image
        if primary and primary.url:
            return primary.url
        urls = REAL_PRODUCT_IMAGE_URLS.get(self.slug)
        if not urls:
            category_slug = self.category.slug if self.category else ""
            urls = _stable_gallery(
                CATEGORY_PRODUCT_IMAGE_POOLS.get(category_slug, DEFAULT_PRODUCT_IMAGE_POOL),
                self.slug,
                count=3,
            )
        if urls:
            return urls[0]
        return ""

    @property
    def secondary_image_url(self):
        all_imgs = self.images.all()
        if len(all_imgs) > 1 and all_imgs[1].url:
            return all_imgs[1].url
        urls = REAL_PRODUCT_IMAGE_URLS.get(self.slug)
        if urls and len(urls) > 1:
            return urls[1]
        category_slug = self.category.slug if self.category else ""
        urls = _stable_gallery(
            CATEGORY_PRODUCT_IMAGE_POOLS.get(category_slug, DEFAULT_PRODUCT_IMAGE_POOL),
            self.slug,
            count=3,
        )
        if len(urls) > 1:
            return urls[1]
        return self.display_image_url


    @property
    def display_gallery_urls(self):
        local_urls = [img.url for img in self.images.all() if img.url]
        if local_urls:
            return local_urls
        urls = REAL_PRODUCT_IMAGE_URLS.get(self.slug)
        if not urls:
            category_slug = self.category.slug if self.category else ""
            urls = _stable_gallery(
                CATEGORY_PRODUCT_IMAGE_POOLS.get(category_slug, DEFAULT_PRODUCT_IMAGE_POOL),
                self.slug,
                count=3,
            )
        if urls:
            return urls
        return []

    def __str__(self):
        return self.name


class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
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
        if self.image_base64:
            return f"data:image/jpeg;base64,{self.image_base64}"
        if self.image:
            import os
            from django.conf import settings
            try:
                full_path = os.path.join(settings.MEDIA_ROOT, self.image.name)
                if os.path.exists(full_path):
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
    created_at = models.DateTimeField(auto_now_add=True)

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
        return self.subtotal - self.discount_amount

    @property
    def delivery_charge(self):
        return 0 if self.subtotal >= 499 else 40


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    variant = models.ForeignKey(ProductVariant, on_delete=models.CASCADE, null=True, blank=True)
    quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('cart', 'product', 'variant')

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
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    address = models.ForeignKey(Address, on_delete=models.SET_NULL, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    delivery_charge = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    grand_total = models.DecimalField(max_digits=10, decimal_places=2)
    coupon = models.ForeignKey(Coupon, on_delete=models.SET_NULL, null=True, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.order_id:
            self.order_id = f"HH{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)

    def __str__(self):
        return self.order_id

    @property
    def is_cancellable(self):
        return self.status in ['pending', 'confirmed']

    @property
    def is_returnable(self):
        return self.status == 'delivered'


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    variant = models.ForeignKey(ProductVariant, on_delete=models.SET_NULL, null=True, blank=True)
    product_name = models.CharField(max_length=255)
    variant_label = models.CharField(max_length=100, blank=True)
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
