from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from django.db.models import Count, Sum, Avg
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import (
    User, Address, Category, SubCategory, Brand, Product,
    ProductImage, ProductVariant, Coupon, Cart, CartItem,
    Order, OrderItem, Payment, OrderTracking, Review, ReviewImage,
    Wishlist, ReturnRequest, Notification
)

admin.site.site_header = "Glamour Store Admin"
admin.site.site_title = "Glamour Store"
admin.site.index_title = "Store Management Dashboard"


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['email', 'get_full_name', 'phone', 'is_email_verified', 'is_active', 'date_joined']
    list_filter = ['is_active', 'is_email_verified', 'is_staff']
    search_fields = ['email', 'first_name', 'last_name', 'phone']
    ordering = ['-date_joined']
    readonly_fields = ['date_joined', 'last_login', 'created_at', 'updated_at']

    fieldsets = BaseUserAdmin.fieldsets + (
        ('Profile', {'fields': ('phone', 'profile_photo', 'date_of_birth', 'is_email_verified')}),
    )

    def get_full_name(self, obj):
        return obj.get_full_name()
    get_full_name.short_description = 'Name'


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'user', 'city', 'state', 'pincode', 'type', 'is_default']
    list_filter = ['type', 'is_default', 'state']
    search_fields = ['full_name', 'user__email', 'city', 'pincode']


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'is_active', 'product_count', 'created_at']
    list_filter = ['is_active']
    search_fields = ['name']
    prepopulated_fields = {'slug': ('name',)}

    def product_count(self, obj):
        return obj.products.count()
    product_count.short_description = 'Products'


@admin.register(SubCategory)
class SubCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'slug', 'is_active']
    list_filter = ['is_active', 'category']
    search_fields = ['name', 'category__name']
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'is_active', 'product_count', 'created_at']
    list_filter = ['is_active']
    search_fields = ['name']
    prepopulated_fields = {'slug': ('name',)}

    def product_count(self, obj):
        return obj.products.count()
    product_count.short_description = 'Products'


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 3
    readonly_fields = ['image_preview']
    fields = ['image', 'image_preview', 'alt_text', 'is_primary', 'order']

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="80" height="80" style="object-fit:cover;border-radius:6px;" />', obj.image.url)
        return '-'
    image_preview.short_description = 'Preview'


class ProductVariantInline(admin.TabularInline):
    model = ProductVariant
    extra = 2
    fields = ['shade_name', 'color_code', 'size', 'finish', 'sku', 'stock', 'additional_price', 'is_active', 'swatch_preview']
    readonly_fields = ['sku', 'swatch_preview']

    def swatch_preview(self, obj):
        if obj.color_code:
            return format_html('<div style="width:30px;height:30px;background:{};border-radius:50%;border:2px solid #ddd;" title="{}"></div>', obj.color_code, obj.shade_name)
        return '-'
    swatch_preview.short_description = 'Color'


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'brand', 'category', 'base_price', 'discount_percent', 'is_active', 'is_featured', 'stock_status', 'avg_rating_display', 'view_count']
    list_filter = ['is_active', 'is_featured', 'is_new_arrival', 'is_bestseller', 'is_flash_sale', 'category', 'brand', 'finish']
    search_fields = ['name', 'brand__name', 'category__name']
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ['view_count', 'avg_rating_display', 'created_at', 'updated_at']
    inlines = [ProductImageInline, ProductVariantInline]
    list_per_page = 25

    fieldsets = (
        ('Basic Info', {
            'fields': ('name', 'slug', 'brand', 'category', 'subcategory', 'short_description', 'description')
        }),
        ('Pricing', {
            'fields': ('base_price', 'discount_percent', 'is_flash_sale')
        }),
        ('Details', {
            'fields': ('finish', 'ingredients', 'how_to_use')
        }),
        ('Status & Labels', {
            'fields': ('is_active', 'is_featured', 'is_new_arrival', 'is_bestseller')
        }),
        ('Analytics', {
            'fields': ('view_count', 'avg_rating_display', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def stock_status(self, obj):
        total = sum(v.stock for v in obj.variants.all())
        if total == 0:
            return format_html('<span style="color:red;font-weight:bold;">Out of Stock</span>')
        elif total < 10:
            return format_html('<span style="color:orange;font-weight:bold;">Low ({})</span>', total)
        return format_html('<span style="color:green;">In Stock ({})</span>', total)
    stock_status.short_description = 'Stock'

    def avg_rating_display(self, obj):
        rating = obj.avg_rating
        stars = '★' * int(rating) + '☆' * (5 - int(rating))
        return format_html('<span style="color:#f4a261;">{}</span> ({})', stars, rating)
    avg_rating_display.short_description = 'Rating'


@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = ['code', 'discount_type', 'discount_value', 'minimum_order_amount', 'usage_limit', 'used_count', 'is_active', 'valid_from', 'valid_to']
    list_filter = ['discount_type', 'is_active']
    search_fields = ['code']


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['product_name', 'variant_label', 'quantity', 'unit_price', 'total_price']
    can_delete = False


class OrderTrackingInline(admin.TabularInline):
    model = OrderTracking
    extra = 1
    fields = ['status', 'description', 'created_at']
    readonly_fields = ['created_at']


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_id', 'user', 'status', 'grand_total', 'payment_status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['order_id', 'user__email']
    readonly_fields = ['order_id', 'created_at', 'updated_at', 'subtotal', 'grand_total']
    inlines = [OrderItemInline, OrderTrackingInline]
    ordering = ['-created_at']

    def payment_status(self, obj):
        try:
            status = obj.payment.status
            colors = {'success': 'green', 'pending': 'orange', 'failed': 'red', 'refunded': 'blue'}
            return format_html('<span style="color:{};">{}</span>', colors.get(status, 'gray'), status.title())
        except:
            return format_html('<span style="color:gray;">No Payment</span>')
    payment_status.short_description = 'Payment'


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['payment_id', 'order', 'method', 'status', 'amount', 'created_at']
    list_filter = ['status', 'method']
    search_fields = ['payment_id', 'order__order_id']
    readonly_fields = ['payment_id', 'created_at', 'updated_at']


class ReviewImageInline(admin.TabularInline):
    model = ReviewImage
    extra = 0


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['product', 'user', 'rating', 'title', 'is_approved', 'is_verified_purchase', 'created_at']
    list_filter = ['is_approved', 'is_verified_purchase', 'rating']
    search_fields = ['product__name', 'user__email', 'title']
    inlines = [ReviewImageInline]
    actions = ['approve_reviews', 'disapprove_reviews']

    def approve_reviews(self, request, queryset):
        queryset.update(is_approved=True)
        self.message_user(request, f"{queryset.count()} reviews approved.")
    approve_reviews.short_description = "Approve selected reviews"

    def disapprove_reviews(self, request, queryset):
        queryset.update(is_approved=False)
        self.message_user(request, f"{queryset.count()} reviews disapproved.")
    disapprove_reviews.short_description = "Disapprove selected reviews"


@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = ['user', 'product', 'added_at']
    search_fields = ['user__email', 'product__name']


@admin.register(ReturnRequest)
class ReturnRequestAdmin(admin.ModelAdmin):
    list_display = ['order', 'user', 'reason', 'status', 'refund_amount', 'created_at']
    list_filter = ['status', 'reason']
    search_fields = ['order__order_id', 'user__email']


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['user', 'type', 'title', 'is_read', 'created_at']
    list_filter = ['type', 'is_read']
    search_fields = ['user__email', 'title']
