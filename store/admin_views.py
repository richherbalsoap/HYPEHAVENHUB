"""
Admin panel views for the store
"""
import json
import base64
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q, Sum, Count, F
from django.db.models.functions import TruncDate
from django.utils import timezone
from datetime import timedelta
from django.conf import settings

from .models import (
    User, Product, ProductVariant, Order, Complaint, Category, Brand,
    AdminDashboardStats, Payment, OrderItem, Review, OrderTracking, ProductImage, ProductPrice, CountrySetting, LANGUAGE_CHOICES, ProductAplusImage, SiteSetting, HeroPanel,
    CustomEarring, CustomBoxOrder, CustomBoxPricing, BOX_TYPE_CHOICES
)
from .forms import (
    ProductForm, AdminComplaintForm, ComplaintForm, AdminOrderUpdateForm, SiteSettingForm, HeroPanelForm
)


from functools import wraps
from django.urls import reverse
import urllib.parse
from django.contrib.auth import authenticate, login as auth_login

def custom_admin_login(request):
    """Custom login page for admin panel (Email/Password only)"""
    if request.user.is_authenticated and request.user.is_staff:
        return redirect('admin_dashboard')
        
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        next_url = request.POST.get('next', 'admin_dashboard')
        
        if not email or not password:
            messages.error(request, "Please enter both email and password.")
        else:
            user = authenticate(request, email=email, password=password)
            if user is not None:
                if user.is_staff or user.is_superuser:
                    auth_login(request, user)
                    if next_url and next_url.startswith('/'):
                        return redirect(next_url)
                    return redirect('admin_dashboard')
                else:
                    messages.error(request, "You are not authorized to access the admin panel.")
            else:
                messages.error(request, "Invalid email or password.")
                
    return render(request, 'admin/admin_login.html', {'next': request.GET.get('next', '')})

def admin_required(function):
    """Decorator to check if user is admin"""
    @wraps(function)
    def wrap(request, *args, **kwargs):
        if not request.user.is_authenticated or not request.user.is_staff:
            login_url = reverse('custom_admin_login')
            next_url = urllib.parse.quote(request.get_full_path())
            return redirect(f"{login_url}?next={next_url}")
        return function(request, *args, **kwargs)
    return wrap
@admin_required
def admin_clear_fake_data(request):
    if request.method == 'POST':
        # Delete all fake data
        AdminDashboardStats.objects.all().delete()
        Complaint.objects.all().delete()
        OrderTracking.objects.all().delete()
        OrderItem.objects.all().delete()
        Payment.objects.all().delete()
        Order.objects.all().delete()
        messages.success(request, 'All fake data has been cleared.')
    return redirect('admin_dashboard')

@admin_required
def admin_dashboard(request):
    """Admin dashboard with statistics"""
    today = timezone.now().date()
    stats, created = AdminDashboardStats.objects.get_or_create(date=today)
    
    # Calculate statistics
    # Only count successful orders for revenue/sales stats (exclude cancelled/failed test data)
    valid_orders = Order.objects.exclude(status__in=['cancelled', 'returned'])
    
    total_orders = valid_orders.count()
    total_revenue = valid_orders.aggregate(Sum('grand_total'))['grand_total__sum'] or 0
    total_users = User.objects.filter(is_staff=False).count()
    new_orders_today = valid_orders.filter(created_at__date=today).count()
    total_products = Product.objects.count()
    returned_orders = Order.objects.filter(status='returned').count()
    total_complaints = Complaint.objects.count()
    open_complaints = Complaint.objects.filter(status__in=['open', 'in_progress']).count()
    pending_orders = valid_orders.filter(status__in=['pending', 'confirmed', 'processing']).count()
    paid_orders = Payment.objects.filter(status='success').count()
    unpaid_orders = Payment.objects.filter(status='pending').count()
    today_revenue = valid_orders.filter(created_at__date=today).aggregate(Sum('grand_total'))['grand_total__sum'] or 0
    
    # Update stats
    stats.total_orders = total_orders
    stats.total_revenue = today_revenue
    stats.total_users = total_users
    stats.new_orders_today = new_orders_today
    stats.total_products = total_products
    stats.returned_orders = returned_orders
    stats.total_complaints = total_complaints
    stats.open_complaints = open_complaints
    stats.save()
    
    # Recent orders
    recent_orders = Order.objects.select_related('user', 'address', 'payment').order_by('-created_at')[:10]
    
    # Recent complaints
    recent_complaints = Complaint.objects.select_related('user').order_by('-created_at')[:5]
    
    context = {
        'stats': stats,
        'recent_orders': recent_orders,
        'recent_complaints': recent_complaints,
        'total_orders': total_orders,
        'total_revenue': total_revenue,
        'total_users': total_users,
        'new_orders_today': new_orders_today,
        'total_products': total_products,
        'returned_orders': returned_orders,
        'pending_orders': pending_orders,
        'paid_orders': paid_orders,
        'unpaid_orders': unpaid_orders,
        'today_revenue': today_revenue,
    }
    return render(request, 'admin/dashboard.html', context)
@admin_required
def admin_products(request):
    """Manage products"""
    products = Product.objects.select_related('brand', 'category').order_by('-created_at')
    



    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        products = products.filter(
            Q(name__icontains=search_query) | 
            Q(description__icontains=search_query)
        )
    
    # Pagination
    from django.core.paginator import Paginator
    paginator = Paginator(products, 20)
    page = request.GET.get('page', 1)
    products = paginator.get_page(page)
    
    context = {
        'products': products,
        'search_query': search_query,
    }
    return render(request, 'admin/products_list.html', context)
@admin_required
def admin_product_create(request):
    """Create new product(s) in catalog"""
    if request.method == 'POST':
        # First check if multi-product catalog was submitted
        created_count = _process_multi_catalog_creation(request)
        if created_count > 0:
            messages.success(request, f'{created_count} Catalog Products created successfully!')
            return redirect('admin_products')

        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            hype_brand, _ = Brand.objects.get_or_create(name='HypeHavenHub')
            product.brand = hype_brand
            product.save()

            if 'video_upload' in request.FILES:
                from .storage import upload_file
                try:
                    product.video_url = upload_file(request.FILES['video_upload'], folder="videos")
                    product.save()
                except Exception as e:
                    messages.error(request, f"Video upload failed: {e}")

            # Handle direct-to-S3 video URL
            video_url = request.POST.get('uploaded_video_url')
            if video_url:
                product.video_url = video_url
                product.save()

            # Handle A+ Image URL(s) (New Multiple System)
            for key in request.POST:
                if key.startswith('uploaded_aplus_image_url_'):
                    url = request.POST[key]
                    if url:
                        ProductAplusImage.objects.create(
                            product=product,
                            image_url=url
                        )
            
            # Handle legacy A+ Image URL
            aplus_url = request.POST.get('aplus_image_url')
            if aplus_url:
                product.aplus_image_url = aplus_url
                product.save()

            # Handle direct-to-S3 image URLs
            is_first = True
            for key in request.POST:
                if key.startswith('uploaded_image_url_'):
                    url = request.POST[key]
                    if url:
                        ProductImage.objects.create(
                            product=product,
                            image_url=url,
                            is_primary=is_first
                        )
                        is_first = False

            # Fallback for old file uploads just in case JS fails
            images = request.FILES.getlist('multiple_images')
            for key in request.FILES:
                if key.startswith('dynamic_image_'):
                    images.extend(request.FILES.getlist(key))
            
            for img in images:
                from .storage import upload_file
                try:
                    url = upload_file(img, folder="products")
                    ProductImage.objects.create(
                        product=product,
                        image_url=url,
                        is_primary=is_first
                    )
                    is_first = False
                except Exception as e:
                    messages.error(request, f"Image upload failed: {e}")

            # Fallback for A+ images
            aplus_images_list = []
            for key in request.FILES:
                if key.startswith('dynamic_aplus_image_'):
                    aplus_images_list.extend(request.FILES.getlist(key))
            
            for img in aplus_images_list:
                from .storage import upload_file
                try:
                    url = upload_file(img, folder="aplus_products")
                    ProductAplusImage.objects.create(
                        product=product,
                        image_url=url
                    )
                except Exception as e:
                    messages.error(request, f"A+ Image upload failed: {e}")

            _save_product_variants(product, request)

            messages.success(request, 'Product created successfully!')
            return redirect('admin_products')
    else:
        form = ProductForm()

    context = {'form': form, 'title': 'Add New Product'}
    return render(request, 'admin/product_form.html', context)


def _process_multi_catalog_creation(request):
    catalog_indices = request.POST.getlist('catalog_indices[]')
    if not catalog_indices:
        return 0
        
    created_count = 0
    copy_shared = request.POST.get('copy_shared_details') in ['true', 'on', '1']
    
    # Base fallback values from first item or form
    first_cat_id = request.POST.get('category_0') or request.POST.get('category')
    first_brand_id = request.POST.get('brand_0') or request.POST.get('brand')
    first_desc = request.POST.get('description_0') or request.POST.get('description', '')
    first_video = request.POST.get('uploaded_video_url_0') or request.POST.get('uploaded_video_url', '')
    
    for idx in catalog_indices:
        name = request.POST.get(f'name_{idx}', '').strip()
        if not name and idx == '0':
            name = request.POST.get('name', '').strip()
        if not name:
            continue
            
        base_price_str = request.POST.get(f'base_price_{idx}') or request.POST.get('base_price', '0')
        discount_str = request.POST.get(f'discount_percent_{idx}') or request.POST.get('discount_percent', '0')
        
        try:
            base_price = float(base_price_str)
        except ValueError:
            base_price = 0.0
            
        try:
            discount_percent = float(discount_str)
        except ValueError:
            discount_percent = 0.0
            
        cat_id = request.POST.get(f'category_{idx}') or (first_cat_id if copy_shared else None)
        brand_id = request.POST.get(f'brand_{idx}') or (first_brand_id if copy_shared else None)
        desc = request.POST.get(f'description_{idx}') or (first_desc if copy_shared else '')
        
        category = Category.objects.filter(id=cat_id).first() if cat_id else Category.objects.first()
        brand = Brand.objects.filter(id=brand_id).first() if brand_id else Brand.objects.get_or_create(name='HypeHavenHub')[0]
        
        weight = request.POST.get(f'weight_{idx}', '')
        material = request.POST.get(f'material_{idx}', '')
        finish = request.POST.get(f'finish_{idx}', '')
        warranty = request.POST.get(f'warranty_{idx}', '')
        
        product = Product.objects.create(
            name=name,
            category=category,
            brand=brand,
            description=desc or name,
            base_price=base_price,
            discount_percent=discount_percent,
            weight=weight,
            material=material,
            finish=finish,
            warranty=warranty,
            is_active=True
        )
        
        # Save video URL
        v_url = request.POST.get(f'uploaded_video_url_{idx}') or (first_video if copy_shared else '')
        if v_url:
            product.video_url = v_url
            product.save()
            
        # Save Images
        is_first = True
        for key in request.POST:
            if key.startswith(f'uploaded_image_url_{idx}_'):
                url = request.POST[key]
                if url:
                    ProductImage.objects.create(
                        product=product,
                        image_url=url,
                        is_primary=is_first
                    )
                    is_first = False
                    
        # Save Product Variants
        shade_names = request.POST.getlist(f'variant_shade_name_{idx}[]')
        add_prices = request.POST.getlist(f'variant_additional_price_{idx}[]')
        stocks = request.POST.getlist(f'variant_stock_{idx}[]')
        
        for s_i in range(len(shade_names)):
            s_name = shade_names[s_i].strip()
            if not s_name:
                continue
            try:
                add_p = float(add_prices[s_i]) if s_i < len(add_prices) and add_prices[s_i] else 0.0
            except ValueError:
                add_p = 0.0
            try:
                stk = int(stocks[s_i]) if s_i < len(stocks) and stocks[s_i] else 10
            except ValueError:
                stk = 10
            v_img = request.POST.get(f'uploaded_variant_image_url_{idx}_{s_i}', '')
            
            ProductVariant.objects.create(
                product=product,
                shade_name=s_name,
                additional_price=add_p,
                stock=stk,
                image_url=v_img
            )
            
        created_count += 1
        
    return created_count
@admin_required
def admin_product_edit(request, pk):
    """Edit product"""
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            product = form.save(commit=False)
            hype_brand, _ = Brand.objects.get_or_create(name='HypeHavenHub')
            product.brand = hype_brand
            product.save()

            if 'video_upload' in request.FILES:
                from .storage import upload_file
                try:
                    product.video_url = upload_file(request.FILES['video_upload'], folder="videos")
                    product.save()
                except Exception as e:
                    messages.error(request, f"Video upload failed: {e}")

            # Handle direct-to-S3 video URL
            video_url = request.POST.get('uploaded_video_url')
            if video_url:
                product.video_url = video_url
                product.save()
                
            # Handle A+ Image URL(s) (New Multiple System)
            for key in request.POST:
                if key.startswith('uploaded_aplus_image_url_'):
                    url = request.POST[key]
                    if url:
                        ProductAplusImage.objects.create(
                            product=product,
                            image_url=url
                        )

            # Handle legacy A+ Image URL
            aplus_url = request.POST.get('aplus_image_url')
            if aplus_url:
                product.aplus_image_url = aplus_url
                product.save()

            # Handle direct-to-S3 image URLs
            has_primary = product.images.filter(is_primary=True).exists()
            for key in request.POST:
                if key.startswith('uploaded_image_url_'):
                    url = request.POST[key]
                    if url:
                        ProductImage.objects.create(
                            product=product,
                            image_url=url,
                            is_primary=not has_primary
                        )
                        has_primary = True

            # Fallback for old file uploads just in case JS fails
            images = request.FILES.getlist('multiple_images')
            for key in request.FILES:
                if key.startswith('dynamic_image_'):
                    images.extend(request.FILES.getlist(key))
            
            for img in images:
                from .storage import upload_file
                try:
                    url = upload_file(img, folder="products")
                    has_primary = product.images.filter(is_primary=True).exists()
                    ProductImage.objects.create(
                        product=product,
                        image_url=url,
                        is_primary=not has_primary
                    )
                except Exception as e:
                    messages.error(request, f"Image upload failed: {e}")

            # Fallback for A+ images
            aplus_images_list = []
            for key in request.FILES:
                if key.startswith('dynamic_aplus_image_'):
                    aplus_images_list.extend(request.FILES.getlist(key))
            
            for img in aplus_images_list:
                from .storage import upload_file
                try:
                    url = upload_file(img, folder="aplus_products")
                    ProductAplusImage.objects.create(
                        product=product,
                        image_url=url
                    )
                except Exception as e:
                    messages.error(request, f"A+ Image upload failed: {e}")

            _save_product_variants(product, request)

            messages.success(request, 'Product updated successfully!')
            return redirect('admin_products')
    else:
        form = ProductForm(instance=product)

    context = {'form': form, 'title': 'Edit Product', 'product': product}
    return render(request, 'admin/product_form.html', context)


def _save_product_variants(product, request):
    shade_names = request.POST.getlist('variant_shade_name[]')
    additional_prices = request.POST.getlist('variant_additional_price[]')
    stocks = request.POST.getlist('variant_stock[]')
    variant_ids = request.POST.getlist('variant_id[]')
    
    for i in range(len(shade_names)):
        shade = shade_names[i].strip()
        if not shade:
            continue
        
        try:
            add_price = float(additional_prices[i]) if i < len(additional_prices) and additional_prices[i] else 0.0
        except ValueError:
            add_price = 0.0
            
        try:
            stk = int(stocks[i]) if i < len(stocks) and stocks[i] else 0
        except ValueError:
            stk = 0
            
        v_id = variant_ids[i] if i < len(variant_ids) else ''
        
        uploaded_url_key = f'uploaded_variant_image_url_{i}'
        file_key = f'variant_image_{i}'
        
        variant_image_url = request.POST.get(uploaded_url_key, '')
        
        if v_id:
            variant = ProductVariant.objects.filter(pk=v_id, product=product).first()
            if variant:
                variant.shade_name = shade
                variant.additional_price = add_price
                variant.stock = stk
                if variant_image_url:
                    variant.image_url = variant_image_url
                elif file_key in request.FILES:
                    from .storage import upload_file
                    try:
                        variant.image_url = upload_file(request.FILES[file_key], folder="variants")
                    except Exception:
                        pass
                variant.save()
                continue

        # Create new variant
        var_obj = ProductVariant(
            product=product,
            shade_name=shade,
            additional_price=add_price,
            stock=stk,
            image_url=variant_image_url
        )
        if not variant_image_url and file_key in request.FILES:
            from .storage import upload_file
            try:
                var_obj.image_url = upload_file(request.FILES[file_key], folder="variants")
            except Exception:
                pass
        var_obj.save()


@admin_required
def admin_variant_delete(request, pk):
    """Delete a product variant"""
    variant = get_object_or_404(ProductVariant, pk=pk)
    variant.delete()
    return JsonResponse({'success': True, 'message': 'Variant deleted successfully'})

@admin_required
def admin_product_delete(request, pk):
    """Delete product"""
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        product.delete()
        messages.success(request, 'Product deleted successfully!')
        return redirect('admin_products')

    context = {'product': product}
    return render(request, 'admin/product_confirm_delete.html', context)
@admin_required
def admin_product_image_delete(request, pk):
    """Delete a product image"""
    image = get_object_or_404(ProductImage, pk=pk)
    product_pk = image.product.pk
    image.delete()
    return JsonResponse({'success': True, 'message': 'Image deleted successfully'})
@admin_required
def admin_product_aplus_image_delete(request, pk):
    """Delete a product A+ image"""
    image = get_object_or_404(ProductAplusImage, pk=pk)
    image.delete()
    return JsonResponse({'success': True, 'message': 'A+ Image deleted successfully'})
@admin_required
def admin_product_delete_video(request, pk):
    """Delete a product's video (clear video_url)"""
    product = get_object_or_404(Product, pk=pk)
    product.video_url = ''
    product.save()
    return JsonResponse({'success': True, 'message': 'Video deleted successfully'})
@admin_required
def admin_product_prices(request, pk):
    """Manage country specific prices for a product"""
    product = get_object_or_404(Product, pk=pk)
    
    if request.method == 'POST':
        country_id = request.POST.get('country_id')
        price = request.POST.get('price')
        
        if country_id and price:
            country = get_object_or_404(CountrySetting, pk=country_id)
            ProductPrice.objects.update_or_create(
                product=product,
                country=country,
                defaults={'price': price}
            )
            messages.success(request, f'Price for {country.name} updated.')
        
        delete_id = request.POST.get('delete_price_id')
        if delete_id:
            ProductPrice.objects.filter(id=delete_id, product=product).delete()
            messages.success(request, 'Price removed.')
            
        return redirect('admin_product_prices', pk=pk)
        
    prices = product.country_prices.all()
    all_countries = CountrySetting.objects.all().order_by('name')
    context = {
        'product': product, 
        'prices': prices, 
        'all_countries': all_countries,
        'title': f'Manage Prices: {product.name}'
    }
    return render(request, 'admin/product_prices.html', context)
@admin_required
def admin_orders(request):
    """View all orders"""
    orders = Order.objects.select_related('user', 'address', 'payment').prefetch_related('items').order_by('-created_at')
    
    # Filter by status
    status = request.GET.get('status', '')
    if status:
        orders = orders.filter(status=status)

    payment_status = request.GET.get('payment_status', '')
    if payment_status:
        orders = orders.filter(payment__status=payment_status)
    
    # Search
    search_query = request.GET.get('search', '')
    if search_query:
        orders = orders.filter(
            Q(order_id__icontains=search_query) |
            Q(user__email__icontains=search_query) |
            Q(user__first_name__icontains=search_query) |
            Q(user__last_name__icontains=search_query) |
            Q(address__phone__icontains=search_query)
        )
    
    # Pagination
    from django.core.paginator import Paginator
    paginator = Paginator(orders, 20)
    page = request.GET.get('page', 1)
    orders = paginator.get_page(page)
    
    context = {
        'orders': orders,
        'status_list': Order.STATUS_CHOICES,
        'payment_status_list': Payment.STATUS_CHOICES,
        'selected_status': status,
        'selected_payment_status': payment_status,
        'search_query': search_query,
    }
    return render(request, 'admin/orders_list.html', context)


from django.http import JsonResponse
import boto3
import uuid
import os
@admin_required
def get_presigned_url(request):
    """
    Returns a presigned PUT URL for uploading directly to Cloudflare R2
    Bypasses the Vercel 4.5MB payload limit.
    """
    if request.method != 'GET':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    filename = request.GET.get('filename', 'file')
    content_type = request.GET.get('content_type', 'application/octet-stream')
    folder = request.GET.get('folder', 'uploads')
    
    # Secure the filename
    ext = filename.rsplit('.', 1)[-1].lower() if '.' in filename else ''
    safe_ext = ext if ext and len(ext) <= 5 else 'bin'
    key = f"{folder}/{uuid.uuid4().hex}.{safe_ext}"
    
    try:
        s3_client = boto3.client(
            's3',
            endpoint_url=settings.AWS_S3_ENDPOINT_URL,
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name='auto'
        )
        
        presigned_url = s3_client.generate_presigned_url(
            'put_object',
            Params={
                'Bucket': settings.AWS_STORAGE_BUCKET_NAME,
                'Key': key,
                'ContentType': content_type
            },
            ExpiresIn=3600,
            HttpMethod='PUT'
        )
        
        # Calculate the final public URL for this file
        domain = settings.AWS_S3_CUSTOM_DOMAIN
        if domain:
            public_url = f"https://{domain}/{key}"
        else:
            public_url = f"{settings.AWS_S3_ENDPOINT_URL}/{settings.AWS_STORAGE_BUCKET_NAME}/{key}"
            
        return JsonResponse({
            'success': True,
            'presigned_url': presigned_url,
            'public_url': public_url,
            'key': key
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)
@admin_required
def admin_order_detail(request, order_id):
    """View and update a customer's full order lifecycle."""
    order = get_object_or_404(
        Order.objects.select_related('user', 'address', 'payment', 'coupon')
        .prefetch_related('items__product', 'tracking', 'complaints'),
        order_id=order_id,
    )
    payment = getattr(order, 'payment', None)
    old_status = order.status
    old_payment_status = payment.status if payment else ''

    if request.method == 'POST':
        form = AdminOrderUpdateForm(request.POST, instance=order, payment=payment)
        if form.is_valid():
            order = form.save()
            payment_method = form.cleaned_data['payment_method']
            payment_status = form.cleaned_data['payment_status']
            payment, _ = Payment.objects.get_or_create(
                order=order,
                defaults={
                    'method': payment_method,
                    'status': payment_status,
                    'amount': order.grand_total,
                }
            )
            payment.method = payment_method
            payment.status = payment_status
            payment.amount = order.grand_total
            payment.save()

            tracking_note = form.cleaned_data.get('tracking_note', '').strip()
            if order.status != old_status or tracking_note:
                description = tracking_note or f"Order status updated to {order.get_status_display()}."
                OrderTracking.objects.create(
                    order=order,
                    status=order.status,
                    description=description,
                )

            if payment.status != old_payment_status:
                OrderTracking.objects.create(
                    order=order,
                    status=f"payment_{payment.status}",
                    description=f"Payment marked as {payment.get_status_display()}.",
                )

            # Auto-refund & Shiprocket cancel if admin marks as cancelled or returned
            if order.status in ['cancelled', 'returned'] and old_status not in ['cancelled', 'returned']:
                from .utils import process_razorpay_refund
                from .shipping import ShiprocketService
                
                try:
                    ShiprocketService.cancel_shipment(order)
                except Exception as sr_err:
                    messages.warning(request, f"Shiprocket cancellation warning: {sr_err}")

                refund_status, refund_msg = process_razorpay_refund(order, f"Admin marked order as {order.status}")
                if refund_status == "processed":
                    messages.success(request, f"Order updated and {refund_msg}")
                elif refund_status == "failed":
                    messages.warning(request, f"Order updated but {refund_msg}")
                else:
                    messages.success(request, f"Order {order.order_id} updated successfully.")
            else:
                messages.success(request, f"Order {order.order_id} updated successfully.")
            return redirect('admin_order_detail', order_id=order.order_id)
    else:
        form = AdminOrderUpdateForm(instance=order, payment=payment)

    context = {
        'order': order,
        'payment': getattr(order, 'payment', None),
        'items': order.items.select_related('product', 'variant').all(),
        'tracking': order.tracking.all(),
        'complaints': order.complaints.select_related('user').all(),
        'form': form,
    }
    return render(request, 'admin/order_detail.html', context)


@admin_required
def admin_retry_shiprocket(request, order_id):
    """Admin endpoint to update order address if needed and re-trigger Shiprocket shipment creation."""
    order = get_object_or_404(Order, order_id=order_id)
    if request.method == 'POST':
        city = request.POST.get('city', '').strip()
        pincode = request.POST.get('pincode', '').strip()
        state = request.POST.get('state', '').strip()
        address_line1 = request.POST.get('address_line1', '').strip()

        if order.address:
            if city:
                order.address.city = city
            if pincode:
                order.address.pincode = pincode
            if state:
                order.address.state = state
            if address_line1:
                order.address.address_line1 = address_line1
            order.address.save()

        from .shipping import ShiprocketService
        shipment_id, error_msg = ShiprocketService.create_shipment(order)
        if shipment_id:
            order.shipping_tracking_id = str(shipment_id)
            order.status = 'confirmed'
            order.save()
            OrderTracking.objects.create(
                order=order,
                status='confirmed',
                description=f'Shiprocket booking retry succeeded! Shipment ID: {shipment_id}'
            )
            messages.success(request, f'Shiprocket booking successful! Shipment ID: {shipment_id}')
        else:
            OrderTracking.objects.create(
                order=order,
                status='shiprocket_failed',
                description=f'Shiprocket Retry Failed: {error_msg}'
            )
            messages.error(request, f'Shiprocket Retry Failed: {error_msg}')

    return redirect('admin_order_detail', order_id=order_id)
@admin_required
def admin_complaints(request):
    """Manage complaints"""
    complaints = Complaint.objects.select_related('user', 'order').order_by('-created_at')
    
    # Filter by status
    status = request.GET.get('status', '')
    if status:
        complaints = complaints.filter(status=status)
    
    # Filter by priority
    priority = request.GET.get('priority', '')
    if priority:
        complaints = complaints.filter(priority=priority)
    
    # Pagination
    from django.core.paginator import Paginator
    paginator = Paginator(complaints, 20)
    page = request.GET.get('page', 1)
    complaints = paginator.get_page(page)
    
    context = {
        'complaints': complaints,
        'status_list': Complaint.STATUS_CHOICES,
        'priority_list': [('low', 'Low'), ('medium', 'Medium'), ('high', 'High')],
        'selected_status': status,
        'selected_priority': priority,
    }
    return render(request, 'admin/complaints_list.html', context)
@admin_required
def admin_complaint_detail(request, complaint_id):
    """View and respond to complaint"""
    complaint = get_object_or_404(Complaint, complaint_id=complaint_id)
    
    if request.method == 'POST':
        form = AdminComplaintForm(request.POST, instance=complaint)
        if form.is_valid():
            updated = form.save(commit=False)
            if updated.status in ['resolved', 'closed'] and not updated.resolved_at:
                updated.resolved_at = timezone.now()
            elif updated.status not in ['resolved', 'closed']:
                updated.resolved_at = None
            updated.save()
            form.save_m2m()
            messages.success(request, 'Complaint updated successfully!')
            return redirect('admin_complaints')
    else:
        form = AdminComplaintForm(instance=complaint)
    
    context = {
        'complaint': complaint,
        'form': form,
    }
    return render(request, 'admin/complaint_detail.html', context)
@admin_required
def admin_reports(request):
    """Analytics and reports"""
    # Get date range
    days = request.GET.get('days', 30)
    try:
        days = int(days)
    except ValueError:
        days = 30
    
    start_date = timezone.now().date() - timedelta(days=days)
    
    # Sales data (Exclude cancelled/failed test orders)
    orders = Order.objects.filter(created_at__date__gte=start_date).exclude(status__in=['cancelled', 'returned'])
    total_sales = orders.aggregate(Sum('grand_total'))['grand_total__sum'] or 0
    total_orders = orders.count()
    avg_order_value = total_sales / total_orders if total_orders > 0 else 0
    
    # Product performance
    product_sales = OrderItem.objects.filter(
        order__created_at__date__gte=start_date,
        order__status__in=['pending', 'confirmed', 'processing', 'shipped', 'delivered']
    ).values('product__name').annotate(
        total_sold=Sum('quantity'),
        total_revenue=Sum('total_price')
    ).order_by('-total_revenue')[:10]
    
    # Return rate
    returned_orders = Order.objects.filter(
        status='returned',
        created_at__date__gte=start_date
    ).count()
    return_rate = (returned_orders / total_orders * 100) if total_orders > 0 else 0
    
    # Category performance
    category_sales = OrderItem.objects.filter(
        order__created_at__date__gte=start_date,
        order__status__in=['pending', 'confirmed', 'processing', 'shipped', 'delivered']
    ).values('product__category__name').annotate(
        total_sold=Sum('quantity'),
        total_revenue=Sum('total_price')
    ).order_by('-total_revenue')
    
    # Daily sales trend
    daily_sales_query = Order.objects.filter(
        created_at__date__gte=start_date
    ).exclude(status__in=['cancelled', 'returned']).extra(
        select={'date': 'DATE(created_at)'}
    ).values('date').annotate(
        revenue=Sum('grand_total'),
        order_count=Count('id')
    ).order_by('date')
    daily_sales = []
    for day in daily_sales_query:
        order_count = day['order_count'] or 0
        revenue = day['revenue'] or 0
        day['avg_order_value'] = revenue / order_count if order_count else 0
        daily_sales.append(day)
    
    context = {
        'total_sales': total_sales,
        'total_orders': total_orders,
        'avg_order_value': avg_order_value,
        'returned_orders': returned_orders,
        'return_rate': return_rate,
        'product_sales': product_sales,
        'category_sales': category_sales,
        'daily_sales': daily_sales,
        'days': days,
    }
    return render(request, 'admin/reports.html', context)
def submit_complaint(request):
    """User complaint submission"""
    if request.method == 'POST':
        form = ComplaintForm(request.POST)
        if form.is_valid():
            complaint = form.save(commit=False)
            complaint.user = request.user
            complaint.save()
            messages.success(request, 'Your complaint has been submitted successfully!')
            return redirect('complaint_detail', complaint_id=complaint.complaint_id)
    else:
        form = ComplaintForm()
    
    # Get user's orders for the complaint form
    user_orders = Order.objects.filter(user=request.user).order_by('-created_at')
    
    context = {
        'form': form,
        'user_orders': user_orders,
    }
    return render(request, 'store/user_complaints.html', context)
@admin_required
def admin_site_settings(request):
    """Manage global site settings like announcement text"""
    setting, created = SiteSetting.objects.get_or_create(id=1)
    if request.method == 'POST':
        form = SiteSettingForm(request.POST, instance=setting)
        if form.is_valid():
            form.save()
            messages.success(request, 'Site settings updated successfully.')
            return redirect('admin_site_settings')
    else:
        form = SiteSettingForm(instance=setting)
    
    return render(request, 'admin/site_settings.html', {'form': form})
@admin_required
def admin_hero_panels(request):
    """List all hero panels"""
    panels = HeroPanel.objects.all()
    return render(request, 'admin/hero_panels.html', {'panels': panels})
@admin_required
def admin_hero_panel_create(request):
    """Create a new hero panel"""
    if request.method == 'POST':
        form = HeroPanelForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Hero panel created successfully.')
            return redirect('admin_hero_panels')
    else:
        form = HeroPanelForm()
    
    return render(request, 'admin/hero_panel_form.html', {'form': form, 'is_edit': False})
@admin_required
def admin_hero_panel_edit(request, pk):
    """Edit an existing hero panel"""
    panel = get_object_or_404(HeroPanel, pk=pk)
    if request.method == 'POST':
        form = HeroPanelForm(request.POST, request.FILES, instance=panel)
        if form.is_valid():
            form.save()
            messages.success(request, 'Hero panel updated successfully.')
            return redirect('admin_hero_panels')
    else:
        form = HeroPanelForm(instance=panel)
    
    return render(request, 'admin/hero_panel_form.html', {'form': form, 'panel': panel, 'is_edit': True})
@admin_required
def admin_hero_panel_delete(request, pk):
    """Delete a hero panel"""
    panel = get_object_or_404(HeroPanel, pk=pk)
    if request.method == 'POST':
        panel.delete()
        messages.success(request, 'Hero panel deleted successfully.')
        return redirect('admin_hero_panels')
def complaint_detail(request, complaint_id):
    """View complaint status"""
    complaint = get_object_or_404(Complaint, complaint_id=complaint_id, user=request.user)
    context = {'complaint': complaint}
    return render(request, 'store/complaint_detail.html', context)
def user_complaints(request):
    """List user's complaints"""
    complaints = Complaint.objects.filter(user=request.user).order_by('-created_at')
    
    # Pagination
    from django.core.paginator import Paginator
    paginator = Paginator(complaints, 10)
    page = request.GET.get('page', 1)
    complaints = paginator.get_page(page)
    
    context = {'complaints': complaints}
    return render(request, 'store/complaints_list.html', context)
def admin_countries(request):
    """List all country settings"""
    if not request.user.is_staff:
        messages.error(request, 'Access denied.')
        return redirect('home')
        
    countries = CountrySetting.objects.all().order_by('name')
    return render(request, 'admin/countries_list.html', {
        'countries': countries,
        'title': 'Currency Settings'
    })
def admin_country_create(request):
    """Create new country setting"""
    if not request.user.is_staff:
        return redirect('home')
        
    if request.method == 'POST':
        name = request.POST.get('name')
        code = request.POST.get('code')
        currency_code = request.POST.get('currency_code')
        currency_symbol = request.POST.get('currency_symbol')
        default_language = 'en'
        shipping_charge = request.POST.get('shipping_charge')

        try:
            CountrySetting.objects.create(
                name=name,
                code=code,
                currency_code=currency_code,
                currency_symbol=currency_symbol,
                default_language=default_language,
                shipping_charge=shipping_charge
            )
            messages.success(request, 'Currency added successfully!')
            return redirect('admin_countries')
        except Exception as e:
            messages.error(request, f'Error adding currency: {str(e)}')
            
    return render(request, 'admin/country_form.html', {
        'title': 'Add Currency Setting',
        'language_choices': LANGUAGE_CHOICES,
    })
def admin_country_edit(request, pk):
    """Edit country setting"""
    if not request.user.is_staff:
        return redirect('home')
        
    country = get_object_or_404(CountrySetting, pk=pk)
    
    if request.method == 'POST':
        country.name = request.POST.get('name')
        country.code = request.POST.get('code')
        country.currency_code = request.POST.get('currency_code')
        country.currency_symbol = request.POST.get('currency_symbol')
        country.default_language = 'en'
        country.shipping_charge = request.POST.get('shipping_charge')
        
        try:
            country.save()
            messages.success(request, 'Currency updated successfully!')
            return redirect('admin_countries')
        except Exception as e:
            messages.error(request, f'Error updating currency: {str(e)}')
            
    return render(request, 'admin/country_form.html', {
        'country': country,
        'title': f'Edit {country.currency_code}',
        'language_choices': LANGUAGE_CHOICES,
    })
def admin_country_delete(request, pk):
    """Delete country setting"""
    if not request.user.is_staff:
        return redirect('home')
        
    country = get_object_or_404(CountrySetting, pk=pk)
    if request.method == 'POST':
        country.delete()
        messages.success(request, 'Country removed.')
    return redirect('admin_countries')
@admin_required
def admin_shiprocket_test(request):
    """
    Read-only Shiprocket diagnostic page. Does NOT place any order.
    Checks:
      1. Are the env vars actually configured on this deployment?
      2. Does login/auth against Shiprocket succeed?
      3. Does the configured pickup location name exist on the account?
    """
    from .shipping import ShiprocketService
    result = ShiprocketService.test_connection()
    return render(request, 'admin/shiprocket_test.html', {'result': result})


# ═══════════════════════════════════════════════════════
#  CUSTOMIZE YOUR EARRINGS — Admin Views
# ═══════════════════════════════════════════════════════

@admin_required
def admin_custom_earrings(request):
    """List all uploaded single earring photos."""
    earrings = CustomEarring.objects.all()
    return render(request, 'admin/custom_earrings.html', {'earrings': earrings})


@admin_required
def admin_custom_earring_create(request):
    """Upload a new single earring photo."""
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        image_url = request.POST.get('image_url', '').strip()
        display_order = request.POST.get('order', 0)

        if not image_url:
            messages.error(request, 'Image is required.')
            return render(request, 'admin/custom_earring_form.html', {
                'form_name': name, 'form_image_url': image_url, 'form_order': display_order
            })

        try:
            display_order = int(display_order)
        except (ValueError, TypeError):
            display_order = 0

        earring = CustomEarring.objects.create(
            name=name,
            image_url=image_url,
            order=display_order,
        )
        display_name = earring.name or f"Earring #{earring.pk}"
        messages.success(request, f'Earring "{display_name}" added successfully!')
        return redirect('admin_custom_earrings')

    return render(request, 'admin/custom_earring_form.html', {})


@admin_required
def admin_custom_earring_edit(request, pk):
    """Edit an existing earring."""
    earring = get_object_or_404(CustomEarring, pk=pk)

    if request.method == 'POST':
        earring.name = request.POST.get('name', '').strip()
        new_url = request.POST.get('image_url', '').strip()
        if new_url:
            earring.image_url = new_url
        try:
            earring.order = int(request.POST.get('order', earring.order))
        except (ValueError, TypeError):
            pass
        earring.is_active = request.POST.get('is_active') == 'on'
        earring.save()
        display_name = earring.name or f"Earring #{earring.pk}"
        messages.success(request, f'Earring "{display_name}" updated!')
        return redirect('admin_custom_earrings')

    return render(request, 'admin/custom_earring_form.html', {
        'earring': earring,
        'form_name': earring.name,
        'form_image_url': earring.image_url,
        'form_order': earring.order,
        'form_is_active': earring.is_active,
    })


@admin_required
def admin_custom_earring_delete(request, pk):
    """Delete an earring photo."""
    earring = get_object_or_404(CustomEarring, pk=pk)
    if request.method == 'POST':
        name = earring.name
        earring.delete()
        messages.success(request, f'Earring "{name}" deleted.')
    return redirect('admin_custom_earrings')


@admin_required
def admin_custom_earring_toggle(request, pk):
    """Toggle active/inactive status."""
    earring = get_object_or_404(CustomEarring, pk=pk)
    earring.is_active = not earring.is_active
    earring.save()
    status = 'activated' if earring.is_active else 'deactivated'
    messages.success(request, f'Earring "{earring.name}" {status}.')
    return redirect('admin_custom_earrings')


@admin_required
def admin_custom_orders(request):
    """List all real customize orders (only paid via Razorpay)."""
    custom_orders = CustomBoxOrder.objects.select_related(
        'order', 'order__user', 'order__payment', 'order__address'
    ).filter(
        order__payment__status='success'
    ).order_by('-created_at')

    return render(request, 'admin/custom_orders.html', {'custom_orders': custom_orders})


@admin_required
def admin_custom_order_detail(request, order_id):
    """View which earrings the customer selected."""
    custom_box = get_object_or_404(
        CustomBoxOrder.objects.select_related(
            'order', 'order__user', 'order__payment', 'order__address'
        ).prefetch_related('selected_earrings'),
        order__order_id=order_id
    )
    return render(request, 'admin/custom_order_detail.html', {'custom_box': custom_box})


@admin_required
def admin_custom_box_pricing(request):
    """Set/edit prices for 12-pair and 16-pair boxes."""
    if request.method == 'POST':
        for box_type, _ in BOX_TYPE_CHOICES:
            price = request.POST.get(f'price_{box_type}', '').strip()
            is_active = request.POST.get(f'active_{box_type}') == 'on'
            if price:
                try:
                    price_val = float(price)
                    obj, _ = CustomBoxPricing.objects.get_or_create(box_type=box_type)
                    obj.price = price_val
                    obj.is_active = is_active
                    obj.save()
                except ValueError:
                    pass
        messages.success(request, 'Box pricing updated!')
        return redirect('admin_custom_box_pricing')

    pricing = {}
    for box_type, label in BOX_TYPE_CHOICES:
        obj = CustomBoxPricing.objects.filter(box_type=box_type).first()
        pricing[box_type] = {
            'label': label,
            'price': obj.price if obj else '',
            'is_active': obj.is_active if obj else True,
        }

    return render(request, 'admin/custom_box_pricing.html', {'pricing': pricing})
