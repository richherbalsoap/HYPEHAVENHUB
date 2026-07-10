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
    User, Product, Order, Complaint, Category, Brand,
    AdminDashboardStats, Payment, OrderItem, Review, OrderTracking, ProductImage, ProductPrice, CountrySetting, LANGUAGE_CHOICES, ProductAplusImage, SiteSetting, HeroPanel, PerspectiveCarouselImage
)
from .forms import (
    ProductForm, AdminComplaintForm, ComplaintForm, AdminOrderUpdateForm, SiteSettingForm, HeroPanelForm, PerspectiveCarouselImageForm
)


def admin_required(function):
    """Decorator to check if user is admin"""
    def wrap(request, *args, **kwargs):
        if not request.user.is_authenticated or not request.user.is_staff:
            messages.error(request, 'Admin access required')
            return redirect('login')
        return function(request, *args, **kwargs)
    return wrap


@login_required
@admin_required
def admin_dashboard(request):
    """Admin dashboard with statistics"""
    today = timezone.now().date()
    stats, created = AdminDashboardStats.objects.get_or_create(date=today)
    
    # Calculate statistics
    total_orders = Order.objects.count()
    total_revenue = Order.objects.aggregate(Sum('grand_total'))['grand_total__sum'] or 0
    total_users = User.objects.filter(is_staff=False).count()
    new_orders_today = Order.objects.filter(created_at__date=today).count()
    total_products = Product.objects.count()
    returned_orders = Order.objects.filter(status='returned').count()
    total_complaints = Complaint.objects.count()
    open_complaints = Complaint.objects.filter(status__in=['open', 'in_progress']).count()
    pending_orders = Order.objects.filter(status__in=['pending', 'confirmed', 'processing']).count()
    paid_orders = Payment.objects.filter(status='success').count()
    unpaid_orders = Payment.objects.filter(status='pending').count()
    today_revenue = Order.objects.filter(created_at__date=today).aggregate(Sum('grand_total'))['grand_total__sum'] or 0
    
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


@login_required
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


@login_required
@admin_required
def admin_product_create(request):
    """Create new product"""
    if request.method == 'POST':
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

            messages.success(request, 'Product created successfully!')
            return redirect('admin_products')
    else:
        form = ProductForm()

    context = {'form': form, 'title': 'Add New Product'}
    return render(request, 'admin/product_form.html', context)


@login_required
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

            messages.success(request, 'Product updated successfully!')
            return redirect('admin_products')
    else:
        form = ProductForm(instance=product)

    context = {'form': form, 'title': 'Edit Product', 'product': product}
    return render(request, 'admin/product_form.html', context)


@login_required
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


@login_required
@admin_required
def admin_product_image_delete(request, pk):
    """Delete a product image"""
    image = get_object_or_404(ProductImage, pk=pk)
    product_pk = image.product.pk
    image.delete()
    return JsonResponse({'success': True, 'message': 'Image deleted successfully'})


@login_required
@admin_required
def admin_product_aplus_image_delete(request, pk):
    """Delete a product A+ image"""
    image = get_object_or_404(ProductAplusImage, pk=pk)
    image.delete()
    return JsonResponse({'success': True, 'message': 'A+ Image deleted successfully'})


@login_required
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


@login_required
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

@login_required
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


@login_required
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

            # Auto-refund if admin marks as cancelled or returned
            if order.status in ['cancelled', 'returned'] and old_status not in ['cancelled', 'returned']:
                from .utils import process_razorpay_refund
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


@login_required
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


@login_required
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


@login_required
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
    
    # Sales data
    orders = Order.objects.filter(created_at__date__gte=start_date)
    total_sales = orders.aggregate(Sum('grand_total'))['grand_total__sum'] or 0
    total_orders = orders.count()
    avg_order_value = total_sales / total_orders if total_orders > 0 else 0
    
    # Product performance
    product_sales = OrderItem.objects.filter(
        order__created_at__date__gte=start_date
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
        order__created_at__date__gte=start_date
    ).values('product__category__name').annotate(
        total_sold=Sum('quantity'),
        total_revenue=Sum('total_price')
    ).order_by('-total_revenue')
    
    # Daily sales trend
    daily_sales_query = Order.objects.filter(
        created_at__date__gte=start_date
    ).extra(
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


@login_required
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


@login_required
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


@login_required
@admin_required
def admin_hero_panels(request):
    """List all hero panels"""
    panels = HeroPanel.objects.all()
    return render(request, 'admin/hero_panels.html', {'panels': panels})


@login_required
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


@login_required
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


@login_required
@admin_required
def admin_hero_panel_delete(request, pk):
    """Delete a hero panel"""
    panel = get_object_or_404(HeroPanel, pk=pk)
    if request.method == 'POST':
        panel.delete()
        messages.success(request, 'Hero panel deleted successfully.')
        return redirect('admin_hero_panels')


@login_required
@admin_required
def admin_perspective_carousels(request):
    """List all perspective carousel images (Unified Interface)"""
    images = PerspectiveCarouselImage.objects.all().order_by('order', '-created_at')
    return render(request, 'admin/perspective_carousels.html', {'images': images})


@login_required
@admin_required
def admin_perspective_carousel_upload(request):
    """Handle bulk uploading of perspective carousel images"""
    if request.method == 'POST':
        # Check for presigned URL dynamic image fields
        i = 0
        while True:
            img_url = request.POST.get(f'dynamic_image_{i}_url')
            if img_url:
                PerspectiveCarouselImage.objects.create(
                    image_url=img_url,
                    is_active=True,
                    order=0
                )
                i += 1
            elif i > 50:
                break
            else:
                i += 1
        return JsonResponse({'success': True})
    return JsonResponse({'success': False, 'error': 'Invalid request'})


@login_required
@admin_required
def admin_perspective_carousel_delete_ajax(request, pk):
    """Delete a perspective carousel image via AJAX"""
    if request.method == 'POST':
        image = get_object_or_404(PerspectiveCarouselImage, pk=pk)
        image.delete()
        return JsonResponse({'success': True})
    return JsonResponse({'success': False, 'error': 'Invalid request'})



@login_required
def complaint_detail(request, complaint_id):
    """View complaint status"""
    complaint = get_object_or_404(Complaint, complaint_id=complaint_id, user=request.user)
    context = {'complaint': complaint}
    return render(request, 'store/complaint_detail.html', context)


@login_required
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

@login_required
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

@login_required
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

@login_required
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

@login_required
def admin_country_delete(request, pk):
    """Delete country setting"""
    if not request.user.is_staff:
        return redirect('home')
        
    country = get_object_or_404(CountrySetting, pk=pk)
    if request.method == 'POST':
        country.delete()
        messages.success(request, 'Country removed.')
    return redirect('admin_countries')

