import random
import string
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q, Avg, Count
from django.core.paginator import Paginator
from django.utils import timezone
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
import json

from .models import (
    User, Category, SubCategory, Brand, Product, ProductImage,
    ProductVariant, Cart, CartItem, Coupon, Order, OrderItem,
    Payment, OrderTracking, Review, ReviewImage, Wishlist,
    Address, ReturnRequest, Notification
)
from .forms import SignupForm, LoginForm, OTPForm, ForgotPasswordForm, ResetPasswordForm, ProfileForm, AddressForm, ReviewForm


def generate_otp():
    return ''.join(random.choices(string.digits, k=6))


def get_or_create_cart(request):
    if request.user.is_authenticated:
        cart, _ = Cart.objects.get_or_create(user=request.user)
        if not request.user.is_authenticated:
            return cart
        sk = request.session.session_key
        if sk:
            try:
                anon_cart = Cart.objects.get(session_key=sk)
                for item in anon_cart.items.all():
                    ci, created = CartItem.objects.get_or_create(
                        cart=cart, product=item.product, variant=item.variant,
                        defaults={'quantity': item.quantity}
                    )
                    if not created:
                        ci.quantity += item.quantity
                        ci.save()
                anon_cart.delete()
            except Cart.DoesNotExist:
                pass
        return cart
    else:
        if not request.session.session_key:
            request.session.create()
        cart, _ = Cart.objects.get_or_create(session_key=request.session.session_key)
        return cart


def home(request):
    featured = Product.objects.filter(is_active=True, is_featured=True).prefetch_related('images', 'variants')[:8]
    new_arrivals = Product.objects.filter(is_active=True, is_new_arrival=True).prefetch_related('images')[:8]
    bestsellers = Product.objects.filter(is_active=True, is_bestseller=True).prefetch_related('images')[:8]
    flash_sale = Product.objects.filter(is_active=True, is_flash_sale=True).prefetch_related('images')[:6]
    categories = Category.objects.filter(is_active=True)[:8]
    brands = Brand.objects.filter(is_active=True)[:10]
    return render(request, 'store/home.html', {
        'featured': featured,
        'new_arrivals': new_arrivals,
        'bestsellers': bestsellers,
        'flash_sale': flash_sale,
        'categories': categories,
        'brands': brands,
    })


def product_list(request):
    products = Product.objects.filter(is_active=True).prefetch_related('images', 'variants')
    categories = Category.objects.filter(is_active=True)
    brands = Brand.objects.filter(is_active=True)

    q = request.GET.get('q', '')
    cat_slug = request.GET.get('category', '')
    subcat_slug = request.GET.get('subcategory', '')
    brand_slug = request.GET.get('brand', '')
    min_price = request.GET.get('min_price', '')
    max_price = request.GET.get('max_price', '')
    rating = request.GET.get('rating', '')
    shade = request.GET.get('shade', '')
    finish = request.GET.get('finish', '')
    sort = request.GET.get('sort', '-created_at')
    discount = request.GET.get('discount', '')

    if q:
        products = products.filter(Q(name__icontains=q) | Q(brand__name__icontains=q) | Q(description__icontains=q))
    if cat_slug:
        products = products.filter(category__slug=cat_slug)
    if subcat_slug:
        products = products.filter(subcategory__slug=subcat_slug)
    if brand_slug:
        products = products.filter(brand__slug=brand_slug)
    if min_price:
        products = products.filter(base_price__gte=min_price)
    if max_price:
        products = products.filter(base_price__lte=max_price)
    if finish:
        products = products.filter(finish=finish)
    if discount:
        products = products.filter(discount_percent__gte=discount)

    sort_options = {
        'price_low': 'base_price',
        'price_high': '-base_price',
        'newest': '-created_at',
        'popularity': '-view_count',
        'rating': '-id',
        '-created_at': '-created_at',
    }
    products = products.order_by(sort_options.get(sort, '-created_at'))

    paginator = Paginator(products, 20)
    page_obj = paginator.get_page(request.GET.get('page', 1))

    return render(request, 'store/product_list.html', {
        'page_obj': page_obj,
        'products': page_obj,
        'categories': categories,
        'brands': brands,
        'q': q,
        'selected_category': cat_slug,
        'selected_brand': brand_slug,
        'sort': sort,
        'discount_opts': ['10', '20', '30', '40', '50'],
    })


def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug, is_active=True)
    product.view_count += 1
    product.save(update_fields=['view_count'])

    variants = product.variants.filter(is_active=True)
    images = product.images.all()
    reviews = product.reviews.filter(is_approved=True).select_related('user')
    similar = Product.objects.filter(
        is_active=True, category=product.category
    ).exclude(id=product.id).prefetch_related('images')[:6]

    user_review = None
    user_in_wishlist = False
    if request.user.is_authenticated:
        user_review = reviews.filter(user=request.user).first()
        user_in_wishlist = Wishlist.objects.filter(user=request.user, product=product).exists()

    review_form = ReviewForm()
    if request.method == 'POST' and request.user.is_authenticated:
        review_form = ReviewForm(request.POST)
        if review_form.is_valid():
            if not Review.objects.filter(user=request.user, product=product).exists():
                rev = review_form.save(commit=False)
                rev.user = request.user
                rev.product = product
                has_order = Order.objects.filter(
                    user=request.user, items__product=product, status='delivered'
                ).exists()
                rev.is_verified_purchase = has_order
                rev.save()
                images_files = request.FILES.getlist('review_images')
                for img in images_files[:3]:
                    ReviewImage.objects.create(review=rev, image=img)
                messages.success(request, 'Review submitted successfully!')
                return redirect('product_detail', slug=slug)
            else:
                messages.warning(request, 'You have already reviewed this product.')

    return render(request, 'store/product_detail.html', {
        'product': product,
        'variants': variants,
        'images': images,
        'reviews': reviews,
        'similar': similar,
        'user_review': user_review,
        'user_in_wishlist': user_in_wishlist,
        'review_form': review_form,
    })


def category_products(request, slug):
    category = get_object_or_404(Category, slug=slug, is_active=True)
    return redirect(f'/products/?category={slug}')


def brand_products(request, slug):
    brand = get_object_or_404(Brand, slug=slug, is_active=True)
    return redirect(f'/products/?brand={slug}')


def search_suggestions(request):
    q = request.GET.get('q', '')
    results = []
    if q and len(q) >= 2:
        products = Product.objects.filter(
            Q(name__icontains=q) | Q(brand__name__icontains=q),
            is_active=True
        ).values('name', 'slug', 'brand__name')[:6]
        for p in products:
            results.append({'name': p['name'], 'brand': p['brand__name'], 'slug': p['slug']})
    return JsonResponse({'results': results})


def signup_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    form = SignupForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.save(commit=False)
        user.username = form.cleaned_data['email']
        user.set_password(form.cleaned_data['password'])
        otp = generate_otp()
        user.otp = otp
        user.otp_created_at = timezone.now()
        user.save()
        request.session['verify_email'] = user.email
        print(f"[OTP for {user.email}]: {otp}")
        messages.info(request, f'Verification OTP sent to {user.email}. (Check console in dev)')
        return redirect('verify_otp')
    return render(request, 'auth/signup.html', {'form': form})


def verify_otp_view(request):
    email = request.session.get('verify_email')
    if not email:
        return redirect('signup')
    user = get_object_or_404(User, email=email)
    if request.method == 'POST':
        otp_entered = request.POST.get('otp', '')
        if otp_entered == user.otp:
            user.is_email_verified = True
            user.otp = ''
            user.save()
            login(request, user)
            messages.success(request, 'Email verified! Welcome to Glamour Store.')
            del request.session['verify_email']
            return redirect('home')
        else:
            messages.error(request, 'Invalid OTP. Please try again.')
    return render(request, 'auth/verify_otp.html', {'email': email})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    form = LoginForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.cleaned_data['user']
        login(request, user)
        next_url = request.GET.get('next', 'home')
        messages.success(request, f'Welcome back, {user.first_name or user.email}!')
        return redirect(next_url)
    return render(request, 'auth/login.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('home')


def forgot_password_view(request):
    form = ForgotPasswordForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        email = form.cleaned_data['email']
        user = User.objects.get(email=email)
        otp = generate_otp()
        user.otp = otp
        user.otp_created_at = timezone.now()
        user.save()
        request.session['reset_email'] = email
        print(f"[Reset OTP for {email}]: {otp}")
        messages.info(request, f'Password reset OTP sent to {email}. (Check console)')
        return redirect('reset_otp')
    return render(request, 'auth/forgot_password.html', {'form': form})


def reset_otp_view(request):
    email = request.session.get('reset_email')
    if not email:
        return redirect('forgot_password')
    user = get_object_or_404(User, email=email)
    if request.method == 'POST':
        otp = request.POST.get('otp', '')
        if otp == user.otp:
            request.session['reset_verified'] = True
            return redirect('reset_password')
        messages.error(request, 'Invalid OTP.')
    return render(request, 'auth/reset_otp.html', {'email': email})


def reset_password_view(request):
    if not request.session.get('reset_verified'):
        return redirect('forgot_password')
    email = request.session.get('reset_email')
    user = get_object_or_404(User, email=email)
    form = ResetPasswordForm(user=user, data=request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        user.otp = ''
        user.save()
        del request.session['reset_email']
        del request.session['reset_verified']
        messages.success(request, 'Password reset successfully! Please log in.')
        return redirect('login')
    return render(request, 'auth/reset_password.html', {'form': form})


@login_required
def profile_view(request):
    form = ProfileForm(request.POST or None, request.FILES or None, instance=request.user)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Profile updated!')
        return redirect('profile')
    orders = Order.objects.filter(user=request.user).order_by('-created_at')[:5]
    notifications = Notification.objects.filter(user=request.user, is_read=False)[:5]
    return render(request, 'store/profile.html', {
        'form': form,
        'orders': orders,
        'notifications': notifications,
    })


@login_required
def address_list(request):
    addresses = Address.objects.filter(user=request.user)
    return render(request, 'store/addresses.html', {'addresses': addresses})


@login_required
def add_address(request):
    form = AddressForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        addr = form.save(commit=False)
        addr.user = request.user
        if addr.is_default:
            Address.objects.filter(user=request.user).update(is_default=False)
        addr.save()
        messages.success(request, 'Address added!')
        return redirect('address_list')
    return render(request, 'store/address_form.html', {'form': form, 'title': 'Add Address'})


@login_required
def edit_address(request, pk):
    addr = get_object_or_404(Address, pk=pk, user=request.user)
    form = AddressForm(request.POST or None, instance=addr)
    if request.method == 'POST' and form.is_valid():
        updated = form.save(commit=False)
        if updated.is_default:
            Address.objects.filter(user=request.user).exclude(pk=pk).update(is_default=False)
        updated.save()
        messages.success(request, 'Address updated!')
        return redirect('address_list')
    return render(request, 'store/address_form.html', {'form': form, 'title': 'Edit Address'})


@login_required
def delete_address(request, pk):
    addr = get_object_or_404(Address, pk=pk, user=request.user)
    addr.delete()
    messages.success(request, 'Address removed.')
    return redirect('address_list')


def cart_view(request):
    cart = get_or_create_cart(request)
    items = cart.items.select_related('product', 'variant').all()
    return render(request, 'store/cart.html', {'cart': cart, 'items': items})


@require_POST
def add_to_cart(request):
    data = json.loads(request.body) if request.content_type == 'application/json' else request.POST
    product_id = data.get('product_id')
    variant_id = data.get('variant_id')
    quantity = int(data.get('quantity', 1))

    product = get_object_or_404(Product, id=product_id, is_active=True)
    variant = None
    if variant_id:
        variant = get_object_or_404(ProductVariant, id=variant_id, product=product)

    cart = get_or_create_cart(request)
    ci, created = CartItem.objects.get_or_create(
        cart=cart, product=product, variant=variant,
        defaults={'quantity': quantity}
    )
    if not created:
        ci.quantity += quantity
        ci.save()

    return JsonResponse({'success': True, 'cart_count': cart.total_items, 'message': 'Added to cart!'})


@require_POST
def update_cart(request):
    data = json.loads(request.body) if request.content_type == 'application/json' else request.POST
    item_id = data.get('item_id')
    action = data.get('action')
    cart = get_or_create_cart(request)

    try:
        item = CartItem.objects.get(id=item_id, cart=cart)
        if action == 'increase':
            item.quantity += 1
            item.save()
        elif action == 'decrease':
            if item.quantity > 1:
                item.quantity -= 1
                item.save()
            else:
                item.delete()
                return JsonResponse({'success': True, 'removed': True, 'cart_count': cart.total_items})
        elif action == 'remove':
            item.delete()
            return JsonResponse({'success': True, 'removed': True, 'cart_count': cart.total_items})
    except CartItem.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Item not found'})

    return JsonResponse({
        'success': True,
        'quantity': item.quantity,
        'item_total': float(item.total_price),
        'cart_subtotal': float(cart.subtotal),
        'cart_total': float(cart.grand_total),
        'cart_count': cart.total_items,
    })


@require_POST
def apply_coupon(request):
    data = json.loads(request.body) if request.content_type == 'application/json' else request.POST
    code = data.get('code', '').strip().upper()
    cart = get_or_create_cart(request)

    try:
        coupon = Coupon.objects.get(code=code)
        if not coupon.is_valid():
            return JsonResponse({'success': False, 'message': 'Coupon is expired or invalid.'})
        if cart.subtotal < coupon.minimum_order_amount:
            return JsonResponse({'success': False, 'message': f'Minimum order amount is ₹{coupon.minimum_order_amount}'})
        cart.coupon = coupon
        cart.save()
        return JsonResponse({
            'success': True,
            'message': f'Coupon applied! You save ₹{cart.discount_amount}',
            'discount': float(cart.discount_amount),
            'grand_total': float(cart.grand_total),
        })
    except Coupon.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Invalid coupon code.'})


@require_POST
def remove_coupon(request):
    cart = get_or_create_cart(request)
    cart.coupon = None
    cart.save()
    return JsonResponse({'success': True, 'message': 'Coupon removed.'})


@login_required
def wishlist_view(request):
    wishlist = Wishlist.objects.filter(user=request.user).select_related('product').prefetch_related('product__images')
    return render(request, 'store/wishlist.html', {'wishlist': wishlist})


@login_required
@require_POST
def toggle_wishlist(request):
    data = json.loads(request.body) if request.content_type == 'application/json' else request.POST
    product_id = data.get('product_id')
    product = get_object_or_404(Product, id=product_id)
    obj, created = Wishlist.objects.get_or_create(user=request.user, product=product)
    if not created:
        obj.delete()
        return JsonResponse({'success': True, 'in_wishlist': False, 'message': 'Removed from wishlist'})
    return JsonResponse({'success': True, 'in_wishlist': True, 'message': 'Added to wishlist'})


@login_required
def checkout_view(request):
    cart = get_or_create_cart(request)
    if not cart.items.exists():
        messages.warning(request, 'Your cart is empty.')
        return redirect('cart')
    addresses = Address.objects.filter(user=request.user)
    return render(request, 'store/checkout.html', {
        'cart': cart,
        'addresses': addresses,
        'items': cart.items.select_related('product', 'variant').all(),
    })


@login_required
@require_POST
def place_order(request):
    data = json.loads(request.body) if request.content_type == 'application/json' else request.POST
    address_id = data.get('address_id')
    payment_method = data.get('payment_method', 'cod')

    if not address_id:
        return JsonResponse({'success': False, 'message': 'Please select a delivery address.'})

    address = get_object_or_404(Address, id=address_id, user=request.user)
    cart = get_or_create_cart(request)

    if not cart.items.exists():
        return JsonResponse({'success': False, 'message': 'Cart is empty.'})

    order = Order.objects.create(
        user=request.user,
        address=address,
        subtotal=cart.subtotal,
        discount_amount=cart.discount_amount,
        delivery_charge=cart.delivery_charge,
        grand_total=cart.grand_total + cart.delivery_charge,
        coupon=cart.coupon,
        status='pending',
    )

    for item in cart.items.all():
        OrderItem.objects.create(
            order=order,
            product=item.product,
            variant=item.variant,
            product_name=item.product.name,
            variant_label=item.variant.label if item.variant else '',
            quantity=item.quantity,
            unit_price=item.unit_price,
            total_price=item.total_price,
        )
        if item.variant:
            item.variant.stock = max(0, item.variant.stock - item.quantity)
            item.variant.save()

    payment = Payment.objects.create(
        order=order,
        method=payment_method,
        amount=order.grand_total,
        status='pending' if payment_method != 'cod' else 'pending',
    )

    if payment_method == 'cod':
        payment.status = 'pending'
        payment.save()
        order.status = 'confirmed'
        order.save()
        OrderTracking.objects.create(order=order, status='confirmed', description='Order confirmed and will be processed soon.')

    if cart.coupon:
        cart.coupon.used_count += 1
        cart.coupon.save()

    Notification.objects.create(
        user=request.user,
        type='order',
        title='Order Placed!',
        message=f'Your order #{order.order_id} has been placed successfully.',
        link=f'/orders/{order.order_id}/'
    )

    cart.items.all().delete()
    cart.coupon = None
    cart.save()

    return JsonResponse({
        'success': True,
        'order_id': order.order_id,
        'redirect': f'/orders/{order.order_id}/'
    })


@login_required
def order_list(request):
    orders = Order.objects.filter(user=request.user).prefetch_related('items', 'payment')
    return render(request, 'store/order_list.html', {'orders': orders})


@login_required
def order_detail(request, order_id):
    order = get_object_or_404(Order, order_id=order_id, user=request.user)
    tracking = order.tracking.all()
    all_statuses = [
        ('pending', 'Ordered'), ('confirmed', 'Confirmed'),
        ('processing', 'Processing'), ('shipped', 'Shipped'),
        ('out_for_delivery', 'Out for Delivery'), ('delivered', 'Delivered'),
    ]
    current_idx = next((i for i, (s, _) in enumerate(all_statuses) if s == order.status), 0)
    order_steps = [
        {'label': label, 'active': i <= current_idx}
        for i, (status, label) in enumerate(all_statuses)
    ]
    return render(request, 'store/order_detail.html', {
        'order': order,
        'tracking': tracking,
        'order_steps': order_steps,
    })


@login_required
@require_POST
def cancel_order(request, order_id):
    order = get_object_or_404(Order, order_id=order_id, user=request.user)
    if not order.is_cancellable:
        return JsonResponse({'success': False, 'message': 'Order cannot be cancelled.'})
    order.status = 'cancelled'
    order.save()
    OrderTracking.objects.create(order=order, status='cancelled', description='Order cancelled by customer.')
    Notification.objects.create(
        user=request.user, type='order', title='Order Cancelled',
        message=f'Your order #{order.order_id} has been cancelled.',
    )
    return JsonResponse({'success': True, 'message': 'Order cancelled successfully.'})


@login_required
def return_request_view(request, order_id):
    order = get_object_or_404(Order, order_id=order_id, user=request.user)
    if not order.is_returnable:
        messages.error(request, 'This order is not eligible for return.')
        return redirect('order_detail', order_id=order_id)
    if request.method == 'POST':
        reason = request.POST.get('reason')
        description = request.POST.get('description', '')
        ReturnRequest.objects.create(
            order=order, user=request.user, reason=reason, description=description,
            refund_amount=order.grand_total
        )
        order.status = 'returned'
        order.save()
        messages.success(request, 'Return request submitted successfully.')
        return redirect('order_detail', order_id=order_id)
    return render(request, 'store/return_request.html', {'order': order})


@login_required
def notifications_view(request):
    notifs = Notification.objects.filter(user=request.user)
    notifs.filter(is_read=False).update(is_read=True)
    return render(request, 'store/notifications.html', {'notifications': notifs})


def get_variant_info(request, variant_id):
    variant = get_object_or_404(ProductVariant, id=variant_id)
    product = variant.product
    price = float(product.selling_price) + float(variant.additional_price)
    return JsonResponse({
        'price': price,
        'stock': variant.stock,
        'in_stock': variant.is_in_stock,
        'sku': variant.sku,
        'label': variant.label,
        'image': variant.image.url if variant.image else None,
    })
