import random
import string
import logging
import base64
from urllib import parse as urllib_parse
from urllib import request as urllib_request
from decimal import Decimal, InvalidOperation
from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponseServerError
from django.db.models import Q
from django.core.paginator import Paginator
from django.core.mail import send_mail
from django.utils import timezone
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST
import json

from .models import (
    User, Category, Brand, Product,
    ProductVariant, Cart, CartItem, Coupon, Order, OrderItem,
    Payment, OrderTracking, Review, ReviewImage, Wishlist,
    Address, ReturnRequest, Notification, UserPreference, FlashSale, Complaint,
    UserProfile, CountrySetting, LANGUAGE_CHOICES, HeroPanel, ProductQuestion
)
from .forms import (
    SignupForm, LoginForm, OTPForm, ForgotPasswordForm, ResetPasswordForm,
    ProfileForm, AddressForm, ReviewForm, UserPreferenceForm,
)

logger = logging.getLogger(__name__)


def active_categories():
    """All active categories, ordered by name. Replaces the old hardcoded
    2-category jhumka-box-set list so any category an admin creates
    actually shows up across the site."""
    return Category.objects.filter(is_active=True)


def generate_otp():
    return ''.join(random.choices(string.digits, k=6))


def send_otp_email(to_email, otp, purpose='verification'):
    if purpose == 'password_reset':
        subject = 'HYPEHAVENHUB password reset OTP'
        action = 'reset your password'
    else:
        subject = 'HYPEHAVENHUB email verification OTP'
        action = 'verify your email'

    message = (
        f"Your OTP to {action} is: {otp}\n\n"
        "This OTP is valid for one-time use only.\n"
        "If you did not request this, please ignore this email."
    )

    try:
        sent_count = send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[to_email],
            fail_silently=False,
        )
        return sent_count > 0
    except Exception:
        logger.exception("Failed to send OTP email to %s", to_email)
        return False


def is_console_email_backend():
    return settings.EMAIL_BACKEND == 'django.core.mail.backends.console.EmailBackend'


def build_login_redirect_url(request, fallback='/', notice=''):
    referer = request.META.get('HTTP_REFERER', '')
    next_url = fallback

    if referer:
        parsed = urllib_parse.urlparse(referer)
        if parsed.scheme and parsed.netloc:
            if parsed.netloc == request.get_host():
                next_url = parsed.path or fallback
                if parsed.query:
                    next_url = f"{next_url}?{parsed.query}"
        elif referer.startswith('/'):
            next_url = referer

    if not url_has_allowed_host_and_scheme(next_url, {request.get_host()}):
        next_url = fallback

    login_base = settings.LOGIN_URL if str(settings.LOGIN_URL).startswith('/') else '/auth/login/'
    query = {'next': next_url}
    if notice:
        query['notice'] = notice
    return f"{login_base}?{urllib_parse.urlencode(query)}"


def normalize_phone_number(phone):
    if not phone:
        return ''

    raw = str(phone).strip()
    digits = ''.join(ch for ch in raw if ch.isdigit())
    if not digits:
        return ''

    if raw.startswith('+'):
        return f'+{digits}'
    if len(digits) == 10:
        return f'+91{digits}'
    if len(digits) > 10:
        return f'+{digits}'
    return ''


def build_order_bill_message(order):
    site_url = getattr(settings, 'SITE_URL', 'http://127.0.0.1:8000').rstrip('/')
    track_url = f"{site_url}/orders/{order.order_id}/"
    lines = [
        f"Order Invoice - {order.order_id}",
        f"Date: {timezone.localtime(order.created_at).strftime('%d-%m-%Y %I:%M %p')}",
        f"Status: {order.get_status_display()}",
        "",
        "Items:",
    ]

    for idx, item in enumerate(order.items.all(), start=1):
        variant_text = f" ({item.variant_label})" if item.variant_label else ''
        lines.append(
            f"{idx}. {item.product_name}{variant_text} x {item.quantity} = INR {item.total_price:.2f}"
        )

    lines.extend([
        "",
        f"Subtotal: INR {order.subtotal:.2f}",
        f"Discount: INR {order.discount_amount:.2f}",
        f"Delivery: INR {order.delivery_charge:.2f}",
        f"Grand Total: INR {order.grand_total:.2f}",
        "",
    ])

    if order.address:
        lines.extend([
            "Delivery Address:",
            f"{order.address.full_name}, {order.address.phone}",
            order.address.address_line1,
            order.address.address_line2 or '',
            f"{order.address.city}, {order.address.state} - {order.address.pincode}",
            "",
        ])

    lines.extend([
        "Thank you for shopping with HYPEHAVENHUB.",
        f"Track your order: {track_url}",
    ])
    return '\n'.join(line for line in lines if line is not None)


def send_order_bill_email(order):
    if not order.user.email:
        return False

    subject = f"HYPEHAVENHUB invoice for order {order.order_id}"
    message = build_order_bill_message(order)
    try:
        sent_count = send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[order.user.email],
            fail_silently=False,
        )
        return sent_count > 0
    except Exception:
        logger.exception("Failed to send order invoice email for %s", order.order_id)
        return False


def send_order_bill_sms(order):
    phone = normalize_phone_number(order.address.phone if order.address else order.user.phone)
    if not phone:
        return False

    site_url = getattr(settings, 'SITE_URL', 'http://127.0.0.1:8000').rstrip('/')
    track_url = f"{site_url}/orders/{order.order_id}/"
    sms_text = (
        f"HYPEHAVENHUB: Order {order.order_id} confirmed. "
        f"Total INR {order.grand_total:.2f}. Track: {track_url}"
    )

    sid = getattr(settings, 'TWILIO_ACCOUNT_SID', '')
    token = getattr(settings, 'TWILIO_AUTH_TOKEN', '')
    from_number = getattr(settings, 'TWILIO_FROM_NUMBER', '')
    if not (sid and token and from_number):
        if settings.DEBUG:
            print(f"[Order SMS to {phone}] {sms_text}")
        return False

    api_url = f"https://api.twilio.com/2010-04-01/Accounts/{sid}/Messages.json"
    payload = urllib_parse.urlencode({
        'To': phone,
        'From': from_number,
        'Body': sms_text,
    }).encode('utf-8')
    auth_token = base64.b64encode(f"{sid}:{token}".encode('utf-8')).decode('utf-8')

    req = urllib_request.Request(api_url, data=payload, method='POST')
    req.add_header('Authorization', f'Basic {auth_token}')
    req.add_header('Content-Type', 'application/x-www-form-urlencoded')

    try:
        timeout = getattr(settings, 'SMS_TIMEOUT', 15)
        with urllib_request.urlopen(req, timeout=timeout) as response:
            return 200 <= response.status < 300
    except Exception:
        logger.exception("Failed to send order SMS for %s", order.order_id)
        return False


def merge_anonymous_cart(request, user):
    sk = request.session.session_key
    if not sk:
        return
    try:
        anon_cart = Cart.objects.get(session_key=sk)
        cart, _ = Cart.objects.get_or_create(user=user)
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

def get_or_create_cart(request):
    if request.user.is_authenticated:
        cart, _ = Cart.objects.get_or_create(user=request.user)
        return cart
    else:
        if not request.session.session_key:
            request.session.create()
        cart, _ = Cart.objects.get_or_create(session_key=request.session.session_key)
        return cart


def home(request):
    storefront_products = Product.objects.filter(is_active=True).select_related('brand', 'category')
    featured = storefront_products.filter(is_featured=True).prefetch_related('images', 'variants', 'reviews')[:8]
    new_arrivals = storefront_products.filter(is_new_arrival=True).prefetch_related('images', 'variants', 'reviews')[:8]
    bestsellers = storefront_products.filter(is_bestseller=True).prefetch_related('images', 'variants', 'reviews')[:8]
    flash_sale = storefront_products.filter(is_flash_sale=True).prefetch_related('images', 'variants', 'reviews')[:6]
    categories = active_categories()[:3]
    hero_products = [
        storefront_products.filter(category=cat).prefetch_related('images', 'variants', 'reviews').first()
        for cat in categories
    ]
    hero_products = [product for product in hero_products if product]
    brands = Brand.objects.filter(
        is_active=True,
        products__is_active=True,
    ).distinct()[:10]
    flash_sale_obj = FlashSale.objects.filter(is_active=True).first()
    hero_panels = HeroPanel.objects.filter(is_active=True)
    
    wishlist_product_ids = []
    if request.user.is_authenticated:
        wishlist_product_ids = list(Wishlist.objects.filter(user=request.user).values_list('product_id', flat=True))
    
    return render(request, 'store/home.html', {
        'featured': featured,
        'hero_products': hero_products,
        'new_arrivals': new_arrivals,
        'bestsellers': bestsellers,
        'flash_sale': flash_sale,
        'categories': categories,
        'brands': brands,
        'flash_sale_end_time': flash_sale_obj.end_time.isoformat() if flash_sale_obj else None,
        'hero_panels': hero_panels,
        'wishlist_product_ids': wishlist_product_ids,
    })


def product_list(request):
    products = Product.objects.filter(is_active=True).select_related('brand', 'category').prefetch_related('images', 'variants', 'reviews')
    categories = active_categories()
    brands = Brand.objects.filter(
        is_active=True,
        products__is_active=True,
    ).distinct()

    q = request.GET.get('q', '')
    cat_slug = request.GET.get('category', '')
    brand_slug = request.GET.get('brand', '')
    min_price_raw = request.GET.get('min_price', '').strip()
    max_price_raw = request.GET.get('max_price', '').strip()
    rating = request.GET.get('rating', '')
    shade = request.GET.get('shade', '')
    finish = request.GET.get('finish', '')
    sort = request.GET.get('sort', '-created_at')
    discount = request.GET.get('discount', '')
    metal_purity = request.GET.get('metal_purity', '')

    if q:
        products = products.filter(Q(name__icontains=q) | Q(brand__name__icontains=q) | Q(description__icontains=q))
    if cat_slug:
        products = products.filter(category__slug=cat_slug)
    if brand_slug:
        products = products.filter(brand__slug=brand_slug)
    def _to_decimal(value):
        if not value:
            return None
        try:
            return Decimal(value)
        except (InvalidOperation, ValueError, TypeError):
            return None

    min_price = _to_decimal(min_price_raw)
    max_price = _to_decimal(max_price_raw)
    if min_price is not None and max_price is not None and min_price > max_price:
        min_price, max_price = max_price, min_price

    if min_price is not None:
        products = products.filter(base_price__gte=min_price)
    if max_price is not None:
        products = products.filter(base_price__lte=max_price)
    if finish:
        products = products.filter(finish=finish)
    if discount:
        products = products.filter(discount_percent__gte=discount)
    if metal_purity:
        products = products.filter(metal_purity__iexact=metal_purity)

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
    query_without_page = request.GET.copy()
    query_without_page.pop('page', None)

    selected_category_name = None
    if cat_slug:
        matched_cat = next((c for c in categories if c.slug == cat_slug), None)
        if matched_cat:
            selected_category_name = matched_cat.name
            
    metal_purities = Product.objects.filter(is_active=True).exclude(metal_purity='').values_list('metal_purity', flat=True).distinct().order_by('metal_purity')

    return render(request, 'store/product_list.html', {
        'page_obj': page_obj,
        'products': page_obj,
        'categories': categories,
        'brands': brands,
        'q': q,
        'selected_category': cat_slug,
        'selected_category_name': selected_category_name,
        'selected_brand': brand_slug,
        'selected_discount': discount,
        'selected_metal_purity': metal_purity,
        'selected_min_price': min_price_raw,
        'selected_max_price': max_price_raw,
        'sort': sort,
        'query_without_page': query_without_page.urlencode(),
        'discount_opts': ['10', '20', '30', '40', '50'],
        'metal_purities': metal_purities,
    })


def product_detail(request, slug):
    product = get_object_or_404(
        Product,
        slug=slug,
        is_active=True,
    )
    try:
        product.view_count += 1
        product.save(update_fields=['view_count'])
    except Exception:
        pass  # Vercel read-only filesystem: view_count increment is non-critical

    variants = product.variants.filter(is_active=True)
    images = product.images.all()
    reviews = product.reviews.filter(is_approved=True).select_related('user')
    similar = Product.objects.filter(
        is_active=True, category=product.category
    ).exclude(id=product.id).prefetch_related('images', 'variants', 'reviews')[:6]

    user_review = None
    user_in_wishlist = False
    if request.user.is_authenticated:
        user_review = reviews.filter(user=request.user).first()
        user_in_wishlist = Wishlist.objects.filter(user=request.user, product=product).exists()

    review_form = ReviewForm()
    if request.method == 'POST':
        if 'question' in request.POST and 'email' in request.POST:
            ProductQuestion.objects.create(
                product=product,
                question=request.POST.get('question'),
                email=request.POST.get('email'),
                display_name=request.POST.get('display_name')
            )
            messages.success(request, 'Your question has been submitted successfully!')
            return redirect('product_detail', slug=slug)
            
        elif request.user.is_authenticated:
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
    category = get_object_or_404(
        Category,
        slug=slug,
        is_active=True,
    )
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
            is_active=True,
        ).values('name', 'slug', 'brand__name')[:6]
        for p in products:
            results.append({'name': p['name'], 'brand': p['brand__name'], 'slug': p['slug']})
    return JsonResponse({'results': results})


def signup_view(request):
    try:
        if request.user.is_authenticated:
            return redirect('home')
        form = SignupForm(request.POST or None)
        if request.method == 'POST' and form.is_valid():
            user = form.save(commit=False)
            user.username = form.cleaned_data['email']
            user.set_password(form.cleaned_data['password'])
            user.is_email_verified = False
            user.is_active = False
            otp = generate_otp()
            user.otp = otp
            user.otp_created_at = timezone.now()
            user.save()
            
            session_country_id = request.session.get('selected_country_id')
            if session_country_id:
                if not CountrySetting.objects.filter(id=session_country_id).exists():
                    first_country = CountrySetting.objects.first()
                    session_country_id = first_country.id if first_country else None
            else:
                first_country = CountrySetting.objects.first()
                session_country_id = first_country.id if first_country else None

            session_lang = request.session.get('django_language', 'en')
            UserProfile.objects.create(
                user=user,
                country_id=session_country_id,
                preferred_language=session_lang
            )
            
            send_otp_email(user.email, otp, purpose='verification')
            request.session['verify_email'] = user.email
            
            if is_console_email_backend() or getattr(settings, 'DEBUG', False):
                request.session['reset_otp_preview'] = otp
            
            return redirect('verify_otp')
        return render(request, 'auth/signup.html', {'form': form})
    except Exception as e:
        import traceback
        return HttpResponseServerError(f"SIGNUP ERROR: {str(e)}\n\n{traceback.format_exc()}")


def verify_otp_view(request):
    try:
        email = request.session.get('verify_email')
        if not email:
            return redirect('signup')
            
        if request.user.is_authenticated:
            return redirect('home')
            
        otp_preview = request.session.get('reset_otp_preview')
        
        if request.method == 'POST':
            otp = ''.join(ch for ch in request.POST.get('otp', '') if ch.isdigit())
            user = get_object_or_404(User, email=email)
            if user.otp and otp == user.otp:
                # Check if OTP has expired (10 minutes = 600 seconds)
                if user.otp_created_at and (timezone.now() - user.otp_created_at).total_seconds() > 600:
                    messages.error(request, 'OTP has expired. Please sign up again to request a new OTP.')
                else:
                    user.is_email_verified = True
                    user.is_active = True
                    user.otp = ''
                    user.save()
                    request.session.pop('verify_email', None)
                    request.session.pop('reset_otp_preview', None)
                    
                    user.backend = 'django.contrib.auth.backends.ModelBackend'
                    login(request, user)
                    merge_anonymous_cart(request, user)
                    messages.success(request, 'Email verified successfully. You are now logged in.')
                    return redirect('home')
            else:
                messages.error(request, 'Invalid OTP.')
            
        return render(request, 'auth/verify_otp.html', {'email': email, 'otp_preview': otp_preview})
    except Exception as e:
        import traceback
        return HttpResponseServerError(f"VERIFY_OTP ERROR: {str(e)}\n\n{traceback.format_exc()}")


def login_view(request):
    if request.user.is_authenticated:
        if request.user.is_staff:
            return redirect('admin_dashboard')
        return redirect('home')
    notice = request.GET.get('notice', '')
    if request.method == 'GET':
        notice_messages = {
            'order_required': 'Order karva mate pehla login karo.',
            'cart_required': 'Cart continue karva mate pehla login karo.',
        }
        if notice in notice_messages:
            messages.info(request, notice_messages[notice])
    form = LoginForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.cleaned_data['user']
        login(request, user)
        merge_anonymous_cart(request, user)
        next_url = request.GET.get('next', '')
        messages.success(request, f'Welcome back, {user.first_name or user.email}!')
        if next_url and url_has_allowed_host_and_scheme(next_url, {request.get_host()}):
            return redirect(next_url)
        if user.is_staff:
            return redirect('admin_dashboard')
        return redirect('home')
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
        request.session.pop('reset_otp_preview', None)
        sent = send_otp_email(email, otp, purpose='password_reset')
        if sent and not is_console_email_backend():
            messages.info(request, f'Password reset OTP sent to {email}.')
        else:
            if settings.DEBUG:
                print(f"[Reset OTP for {email}]: {otp}")
            request.session['reset_otp_preview'] = otp
            if is_console_email_backend():
                messages.warning(
                    request,
                    'Email service is not configured. Use the OTP shown on the next screen.'
                )
            else:
                messages.warning(
                    request,
                    f'Could not send reset OTP email to {email}. Use the OTP shown on the next screen.'
                )
        return redirect('reset_otp')
    return render(request, 'auth/forgot_password.html', {'form': form})


def reset_otp_view(request):
    email = request.session.get('reset_email')
    if not email:
        return redirect('forgot_password')
    user = get_object_or_404(User, email=email)
    otp_preview = request.session.get('reset_otp_preview')
    if request.method == 'POST':
        otp = ''.join(ch for ch in request.POST.get('otp', '') if ch.isdigit())
        if user.otp and otp == user.otp:
            # Check if OTP has expired (10 minutes = 600 seconds)
            if user.otp_created_at and (timezone.now() - user.otp_created_at).total_seconds() > 600:
                messages.error(request, 'OTP has expired. Please request another password reset.')
            else:
                request.session['reset_verified'] = True
                request.session.pop('reset_otp_preview', None)
                return redirect('reset_password')
        else:
            messages.error(request, 'Invalid OTP.')
    return render(request, 'auth/reset_otp.html', {'email': email, 'otp_preview': otp_preview})


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
        request.session.pop('reset_otp_preview', None)
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
def settings_view(request):
    prefs, _ = UserPreference.objects.get_or_create(user=request.user)
    form = UserPreferenceForm(request.POST or None, instance=prefs)

    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Settings updated successfully.')
        return redirect('settings')

    return render(request, 'store/settings.html', {'form': form})


@login_required
def address_list(request):
    addresses = Address.objects.filter(user=request.user)
    return render(request, 'store/addresses.html', {'addresses': addresses})


@login_required
def add_address(request):
    form = AddressForm(request.POST or None)
    next_url = request.GET.get('next') or request.POST.get('next')
    if request.method == 'POST' and form.is_valid():
        addr = form.save(commit=False)
        addr.user = request.user
        if addr.is_default:
            Address.objects.filter(user=request.user).update(is_default=False)
        addr.save()
        messages.success(request, 'Address added!')
        if next_url:
            return redirect(next_url)
        return redirect('address_list')
    return render(request, 'store/address_form.html', {'form': form, 'title': 'Add Address', 'next': next_url})


@login_required
def edit_address(request, pk):
    addr = get_object_or_404(Address, pk=pk, user=request.user)
    form = AddressForm(request.POST or None, instance=addr)
    next_url = request.GET.get('next') or request.POST.get('next')
    if request.method == 'POST' and form.is_valid():
        updated = form.save(commit=False)
        if updated.is_default:
            Address.objects.filter(user=request.user).exclude(pk=pk).update(is_default=False)
        updated.save()
        messages.success(request, 'Address updated!')
        if next_url:
            return redirect(next_url)
        return redirect('address_list')
    return render(request, 'store/address_form.html', {'form': form, 'title': 'Edit Address', 'next': next_url})


@login_required
def delete_address(request, pk):
    addr = get_object_or_404(Address, pk=pk, user=request.user)
    addr.delete()
    messages.success(request, 'Address removed.')
    return redirect('address_list')


@login_required
def cart_view(request):
    cart = get_or_create_cart(request)
    items = cart.items.select_related('product', 'variant').all()
    return render(request, 'store/cart.html', {'cart': cart, 'items': items})

def cart_drawer_view(request):
    cart = get_or_create_cart(request)
    items = cart.items.select_related('product', 'variant').all()
    cart_product_ids = [item.product_id for item in items]
    suggested_products = Product.objects.filter(is_active=True).exclude(id__in=cart_product_ids).order_by('-is_bestseller', '-view_count')[:8]
    return render(request, 'store/cart_drawer.html', {
        'cart': cart, 
        'items': items,
        'suggested_products': suggested_products
    })


@require_POST
def add_to_cart(request):
    if not request.user.is_authenticated:
        return JsonResponse({
            'success': False,
            'requires_login': True,
            'redirect': build_login_redirect_url(request, notice='cart_required'),
            'message': 'Please login first to add products to cart.',
        }, status=401)

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
    if not request.user.is_authenticated:
        return JsonResponse({
            'success': False,
            'requires_login': True,
            'redirect': build_login_redirect_url(request, fallback='/cart/', notice='cart_required'),
            'message': 'Please login first to update cart.',
        }, status=401)

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
        elif action == 'remove':
            item.delete()
            
        if request.headers.get('HX-Request'):
            cart = get_or_create_cart(request)
            items = cart.items.select_related('product', 'variant').all()
            return render(request, 'store/cart.html', {'cart': cart, 'items': items})

        if action in ['decrease', 'remove'] and getattr(item, 'id', None) is None:
            return JsonResponse({
                'success': True, 'removed': True,
                'cart_count': cart.total_items,
                'cart_subtotal': float(cart.subtotal),
                'cart_total': float(cart.grand_total),
                'delivery_charge': float(cart.delivery_charge),
            })
    except CartItem.DoesNotExist:
        if request.headers.get('HX-Request'):
            cart = get_or_create_cart(request)
            items = cart.items.select_related('product', 'variant').all()
            return render(request, 'store/cart.html', {'cart': cart, 'items': items})
        return JsonResponse({'success': False, 'message': 'Item not found'})

    if request.headers.get('HX-Request'):
        cart = get_or_create_cart(request)
        items = cart.items.select_related('product', 'variant').all()
        return render(request, 'store/cart.html', {'cart': cart, 'items': items})

    return JsonResponse({
        'success': True,
        'quantity': item.quantity,
        'item_total': float(item.total_price),
        'cart_subtotal': float(cart.subtotal),
        'cart_total': float(cart.grand_total),
        'cart_count': cart.total_items,
        'delivery_charge': float(cart.delivery_charge),
    })


@require_POST
def apply_coupon(request):
    if not request.user.is_authenticated:
        return JsonResponse({
            'success': False,
            'requires_login': True,
            'redirect': build_login_redirect_url(request, fallback='/cart/', notice='cart_required'),
            'message': 'Please login first to apply coupon.',
        }, status=401)

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
        
        if request.headers.get('HX-Request'):
            items = cart.items.select_related('product', 'variant').all()
            return render(request, 'store/cart.html', {'cart': cart, 'items': items, 'coupon_msg': f'Coupon applied! You save ₹{cart.discount_amount}'})

        return JsonResponse({
            'success': True,
            'message': f'Coupon applied! You save ₹{cart.discount_amount}',
            'discount': float(cart.discount_amount),
            'grand_total': float(cart.grand_total),
        })
    except Coupon.DoesNotExist:
        if request.headers.get('HX-Request'):
            items = cart.items.select_related('product', 'variant').all()
            return render(request, 'store/cart.html', {'cart': cart, 'items': items, 'coupon_error': 'Invalid coupon code.'})
        return JsonResponse({'success': False, 'message': 'Invalid coupon code.'})


@require_POST
def remove_coupon(request):
    if not request.user.is_authenticated:
        return JsonResponse({
            'success': False,
            'requires_login': True,
            'redirect': build_login_redirect_url(request, fallback='/cart/', notice='cart_required'),
            'message': 'Please login first to update coupon.',
        }, status=401)

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


from django.views.decorators.cache import never_cache

@never_cache
def checkout_view(request):
    messages.info(request, 'Checkout is now handled directly from the cart.')
    return redirect('cart')


@require_POST
def place_order(request):
    if not request.user.is_authenticated:
        return JsonResponse({
            'success': False,
            'requires_login': True,
            'redirect': build_login_redirect_url(request, fallback='/checkout/', notice='order_required'),
            'message': 'Order karva mate pehla login karo.',
        }, status=401)

    data = json.loads(request.body) if request.content_type == 'application/json' else request.POST
    address_id = data.get('address_id')
    payment_method = data.get('payment_method', 'cod')

    if not address_id:
        return JsonResponse({'success': False, 'message': 'Please select a delivery address.'})

    address = get_object_or_404(Address, id=address_id, user=request.user)
    cart = get_or_create_cart(request)

    if not cart.items.exists():
        return JsonResponse({'success': False, 'message': 'Cart is empty.'})

    # Create order in pending status
    order = Order.objects.create(
        user=request.user,
        address=address,
        subtotal=cart.subtotal,
        discount_amount=cart.discount_amount,
        delivery_charge=cart.delivery_charge,
        grand_total=cart.grand_total,
        coupon=cart.coupon,
        status='pending',
    )

    # Create OrderItems
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

    # Create Payment log
    payment = Payment.objects.create(
        order=order,
        method=payment_method,
        amount=order.grand_total,
        status='pending',
    )

    if payment_method == 'cod':
        return JsonResponse({'success': False, 'message': 'Cash on Delivery is no longer available. Please use online payment.'})

    if payment_method == 'razorpay':
        import razorpay
        try:
            client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
            amount_in_paise = int(order.grand_total * 100)
            
            # Create Razorpay Order
            razorpay_order = client.order.create(data={
                'amount': amount_in_paise,
                'currency': 'INR',
                'receipt': str(order.order_id),
            })
            
            payment.gateway_response = {
                'razorpay_order_id': razorpay_order['id'],
                'amount': amount_in_paise,
                'currency': 'INR'
            }
            payment.save()
            
            customer_name = f"{request.user.first_name} {request.user.last_name}".strip() or request.user.email
            
            return JsonResponse({
                'success': True,
                'payment_method': 'razorpay',
                'razorpay_order_id': razorpay_order['id'],
                'razorpay_key_id': settings.RAZORPAY_KEY_ID,
                'amount': amount_in_paise,
                'order_id': order.order_id,
                'customer_name': customer_name,
                'customer_email': request.user.email,
                'customer_phone': address.phone or '',
            })
        except Exception as e:
            logger.error(f"Razorpay order creation failed: {str(e)}")
            order.delete() # cleanup order on failure
            return JsonResponse({
                'success': False,
                'message': 'Failed to initiate Razorpay payment. Please try again.'
            })

    return JsonResponse({'success': False, 'message': 'Invalid payment method.'})

@require_POST
def razorpay_direct_checkout(request):
    try:
        data = json.loads(request.body) if request.content_type == 'application/json' else request.POST
    except Exception:
        data = {}
        
    user = request.user
    if not user.is_authenticated:
        from django.contrib.auth import get_user_model
        User = get_user_model()
        user, _ = User.objects.get_or_create(
            username='guest_checkout',
            defaults={
                'email': 'guest@hypehavenhub.com',
                'first_name': 'Guest',
                'last_name': 'User',
            }
        )
        
    product_id = data.get('product_id')
    variant_id = data.get('variant_id')
    quantity = int(data.get('quantity', 1))

    subtotal = Decimal('0.00')
    discount_amount = Decimal('0.00')
    delivery_charge = Decimal('0.00')
    coupon = None
    items_to_create = []

    if product_id:
        # Buy Now flow
        product = get_object_or_404(Product, id=product_id, is_active=True)
        variant = None
        if variant_id:
            variant = get_object_or_404(ProductVariant, id=variant_id, product=product)
        
        unit_price = product.selling_price
        if variant:
            unit_price += variant.additional_price
        
        total_price = unit_price * quantity
        subtotal = total_price
        # Basic delivery charge for Buy Now (0 for now to match Cart behavior)
        delivery_charge = Decimal('0.00')

        items_to_create.append({
            'product': product,
            'variant': variant,
            'product_name': product.name,
            'variant_label': variant.label if variant else '',
            'quantity': quantity,
            'unit_price': unit_price,
            'total_price': total_price
        })
    else:
        # Cart Checkout flow
        cart = get_or_create_cart(request)
        if not cart.items.exists():
            return JsonResponse({'success': False, 'message': 'Cart is empty.'})
            
        subtotal = cart.subtotal
        discount_amount = cart.discount_amount
        delivery_charge = cart.delivery_charge
        coupon = cart.coupon
        
        for item in cart.items.all():
            items_to_create.append({
                'product': item.product,
                'variant': item.variant,
                'product_name': item.product.name,
                'variant_label': item.variant.label if item.variant else '',
                'quantity': item.quantity,
                'unit_price': item.unit_price,
                'total_price': item.total_price
            })

    grand_total = subtotal - discount_amount + delivery_charge

    # Create Order without address
    order = Order.objects.create(
        user=user,
        address=None,
        subtotal=subtotal,
        discount_amount=discount_amount,
        delivery_charge=delivery_charge,
        grand_total=grand_total,
        coupon=coupon,
        status='pending',
    )

    for item_data in items_to_create:
        OrderItem.objects.create(order=order, **item_data)

    payment = Payment.objects.create(
        order=order,
        method='razorpay',
        amount=order.grand_total,
        status='pending',
    )

    import razorpay
    try:
        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
        amount_in_paise = int(order.grand_total * 100)
        
        razorpay_order = client.order.create(data={
            'amount': amount_in_paise,
            'currency': 'INR',
            'receipt': str(order.order_id),
        })
        
        payment.gateway_response = {
            'razorpay_order_id': razorpay_order['id'],
            'amount': amount_in_paise,
            'currency': 'INR'
        }
        payment.save()
        
        customer_name = f"{user.first_name} {user.last_name}".strip() if user.username != 'guest_checkout' else ''
        
        rzp_line_items = []
        for item_data in items_to_create:
            rzp_line_items.append({
                "name": item_data['product_name'][:250] + (" - " + item_data['variant_label'] if item_data['variant_label'] else ""),
                "price": int(item_data['unit_price'] * 100),
                "currency": "INR",
                "quantity": item_data['quantity']
            })
            
        return JsonResponse({
            'success': True,
            'payment_method': 'razorpay',
            'razorpay_order_id': razorpay_order['id'],
            'razorpay_key_id': settings.RAZORPAY_KEY_ID,
            'amount': amount_in_paise,
            'line_items_total': amount_in_paise,
            'line_items': rzp_line_items,
            'order_id': order.order_id,
            'customer_name': customer_name,
            'customer_email': user.email if user.username != 'guest_checkout' else '',
            'customer_phone': getattr(user, 'phone', '') if user.username != 'guest_checkout' else '',
        })
    except Exception as e:
        logger.error(f"Razorpay order creation failed: {str(e)}")
        order.delete()
        return JsonResponse({
            'success': False,
            'message': 'Failed to initiate Razorpay payment. Please try again.'
        })


@require_POST
def verify_payment(request):
    from django.db import transaction
    from store.exceptions import InventoryConflictError

    try:
        data = json.loads(request.body)
        razorpay_payment_id = data.get('razorpay_payment_id')
        razorpay_order_id = data.get('razorpay_order_id')
        razorpay_signature = data.get('razorpay_signature')
        local_order_id = data.get('order_id')

        if not all([razorpay_payment_id, razorpay_order_id, razorpay_signature, local_order_id]):
            return JsonResponse({'success': False, 'message': 'Missing payment credentials.'})

        with transaction.atomic():
            order = Order.objects.select_for_update().get(order_id=local_order_id)
            if request.user.is_authenticated and order.user != request.user and order.user.username != 'guest_checkout':
                return JsonResponse({'success': False, 'message': 'Unauthorized access.'}, status=403)
            
            payment = order.payment

            # Verify signature
            import razorpay
            client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
            
            params_dict = {
                'razorpay_order_id': razorpay_order_id,
                'razorpay_payment_id': razorpay_payment_id,
                'razorpay_signature': razorpay_signature
            }

            try:
                client.utility.verify_payment_signature(params_dict)
            except Exception as e:
                logger.error(f"Razorpay signature verification failed: {str(e)}")
                payment.status = 'failed'
                payment.save()
                return JsonResponse({'success': False, 'message': 'Payment verification signature mismatch.'})

            # Payment successful - complete transaction
            payment.status = 'success'
            payment.payment_id = razorpay_payment_id
            payment.gateway_response = params_dict
            payment.save()

            if order.user.username == 'guest_checkout':
                try:
                    rzp_order = client.order.fetch(razorpay_order_id)
                    shipping_address = rzp_order.get('shipping_address') or rzp_order.get('notes', {}).get('shipping_address')
                    if not shipping_address:
                        rzp_payment = client.payment.fetch(razorpay_payment_id)
                        shipping_address = rzp_payment.get('notes', {}).get('shipping_address')
                        contact = rzp_payment.get('contact', '')
                        email = rzp_payment.get('email', 'guest@hypehavenhub.com')
                    else:
                        contact = rzp_order.get('customer_details', {}).get('contact', '')
                        email = rzp_order.get('customer_details', {}).get('email', 'guest@hypehavenhub.com')

                    if shipping_address:
                        from store.models import Address
                        address_obj, _ = Address.objects.get_or_create(
                            user=order.user,
                            street_address=shipping_address.get('line1', shipping_address.get('street_address', '')),
                            city=shipping_address.get('city', ''),
                            state=shipping_address.get('state', ''),
                            postal_code=shipping_address.get('zipcode', ''),
                            country=shipping_address.get('country', 'IN'),
                            defaults={
                                'name': shipping_address.get('name', 'Guest User'),
                                'phone_number': contact
                            }
                        )
                        order.address = address_obj
                except Exception as e:
                    logger.error(f"Error fetching Magic Checkout address: {e}")

            # Update order status
            order.status = 'confirmed'
            order.save()

            # Decrement stock with row locking (select_for_update)
            for item in order.items.all():
                if item.variant:
                    variant = ProductVariant.objects.select_for_update().get(id=item.variant.id)
                    if variant.stock < item.quantity:
                        raise InventoryConflictError(f"Insufficient stock for {item.product.name} ({variant.label}).")
                    variant.stock -= item.quantity
                    variant.save()

            # Create tracking entry
            OrderTracking.objects.create(
                order=order,
                status='confirmed',
                description='Payment verified successfully. Order confirmed.'
            )

            cart = get_or_create_cart(request)
            if cart.coupon:
                cart.coupon.used_count += 1
                cart.coupon.save()

            # Clear cart
            cart.items.all().delete()
            cart.coupon = None
            cart.save()

            # Create notification
            Notification.objects.create(
                user=request.user,
                type='order',
                title='Order Paid & Placed!',
                message=f'Your payment for order #{order.order_id} has been verified successfully.',
                link=f'/orders/{order.order_id}/'
            )

        # Send billing notifications
        email_sent = send_order_bill_email(order)
        sms_sent = send_order_bill_sms(order)

        # Trigger Shiprocket booking for prepaid order
        shipment_id = None
        try:
            from .shipping import ShiprocketService
            shipment_id = ShiprocketService.create_shipment(order)
            if shipment_id:
                order.shipping_tracking_id = str(shipment_id)
                order.save()
        except Exception as e:
            logger.error(f"Error booking Shiprocket for prepaid order {order.order_id}: {str(e)}")

        return JsonResponse({
            'success': True,
            'order_id': order.order_id,
            'redirect': f'/orders/{order.order_id}/',
            'shipment_id': shipment_id,
            'email_sent': email_sent,
            'sms_sent': sms_sent
        })

    except Exception as e:
        logger.error(f"Error during payment verification: {str(e)}")
        from store.exceptions import InventoryConflictError
        if isinstance(e, InventoryConflictError):
            return JsonResponse({'success': False, 'message': str(e)})
        return JsonResponse({'success': False, 'message': f'An internal error occurred: {str(e)}'})


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
    from django.db import transaction
    from datetime import datetime, timezone as datetime_timezone
    
    try:
        with transaction.atomic():
            order = Order.objects.select_for_update().get(order_id=order_id, user=request.user)
            if not order.is_cancellable:
                return JsonResponse({'success': False, 'message': 'Order cannot be cancelled.'})
                
            # Restore stock with locking
            for item in order.items.all():
                if item.variant:
                    variant = ProductVariant.objects.select_for_update().get(id=item.variant.id)
                    variant.stock += item.quantity
                    variant.save()
                    
            # Process automatic Razorpay refund if prepaid
            from .utils import process_razorpay_refund
            refund_status, refund_msg = process_razorpay_refund(order, "Customer cancelled order")
            
            # Cancel order and tracking log
            order.status = 'cancelled'
            order.save()
            OrderTracking.objects.create(order=order, status='cancelled', description='Order cancelled by customer.')
            
            # Construct notification message
            notif_message = f'Your order #{order.order_id} has been cancelled.'
            if refund_status == "processed":
                payment = getattr(order, 'payment', None)
                if payment:
                    notif_message += f' A refund of INR {payment.amount:.2f} has been initiated to your payment account.'
            elif refund_status == "failed":
                notif_message += ' We encountered an issue initiating your automatic refund. Our support team will process it manually.'
                
            Notification.objects.create(
                user=request.user, 
                type='order', 
                title='Order Cancelled',
                message=notif_message,
            )
            
            success_message = 'Order cancelled successfully.'
            if refund_status == "processed":
                payment = getattr(order, 'payment', None)
                if payment:
                    success_message += f' Refund of INR {payment.amount:.2f} initiated.'
            elif refund_status == "failed":
                success_message += ' Automatic refund failed; support will process it manually.'
                
            return JsonResponse({'success': True, 'message': success_message})
            
    except Order.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Order not found.'}, status=404)
    except Exception as e:
        logger.error(f"Error during order cancellation: {str(e)}")
        return JsonResponse({'success': False, 'message': f'Failed to cancel order: {str(e)}'}, status=500)


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


def quick_view(request, product_id):
    from store.templatetags.localization_tags import get_localized_price, get_localized_base_price
    product = get_object_or_404(Product, id=product_id)
    variants = [{
        'id': v.id,
        'label': v.label,
        'stock': v.stock,
        'in_stock': v.is_in_stock,
        'price': float(product.selling_price) + float(v.additional_price)
    } for v in product.variants.all()]
    
    localized_selling_price = get_localized_price(product, request)
    localized_base_price = get_localized_base_price(product, request) if product.discount_percent > 0 else None
    
    return JsonResponse({
        'id': product.id,
        'name': product.name,
        'selling_price': float(product.selling_price),
        'base_price': float(product.base_price) if product.discount_percent > 0 else None,
        'discount_percent': float(product.discount_percent) if product.discount_percent > 0 else 0,
        'localized_selling_price': localized_selling_price,
        'localized_base_price': localized_base_price,
        'description': product.description,
        'image': product.display_image_url,
        'variants': variants,
        'slug': product.slug,
        'material': product.material or '',
        'metal_purity': product.metal_purity or '',
        'artisan_story': product.artisan_story or '',
    })


def run_migrations_view(request):
    from django.http import HttpResponseForbidden
    from django.contrib.auth import get_user_model
    User = get_user_model()
    
    if not settings.DEBUG and not request.user.is_superuser:
        return HttpResponseForbidden("Forbidden: This endpoint is only available to superusers in production.")
    
    if settings.DEBUG and User.objects.filter(is_superuser=True).exists() and not request.user.is_superuser:
        return HttpResponseForbidden("Forbidden: A superuser already exists. Please log in first.")

    import io
    from django.core.management import call_command
    from django.http import HttpResponse
    
    out = io.StringIO()
    err = io.StringIO()
    
    try:
        # Run migrations
        call_command('migrate', '--run-syncdb', no_input=True, stdout=out, stderr=err)
        
        # Load fixture data
        call_command('loaddata', 'store/fixtures/initial_data.json', stdout=out, stderr=err)
        
        # Create default superuser
        if not User.objects.filter(is_superuser=True).exists():
            User.objects.create_superuser(
                username='admin',
                email='admin@hypehavenhub.com',
                password='HypeAdmin@2024'
            )
            out.write("\nSuperuser admin created successfully.")
            
        result = f"Migrations and Seeding Output:\n\n{out.getvalue()}\n\nErrors:\n\n{err.getvalue()}"
    except Exception as e:
        result = f"Failed to run migrations: {str(e)}\n\nOutput so far:\n{out.getvalue()}\n\nErrors so far:\n{err.getvalue()}"
        
    return HttpResponse(result, content_type="text/plain")


def set_country_session(request):
    if request.method == 'POST':
        country_id = request.POST.get('country_id')
        if country_id:
            request.session['selected_country_id'] = int(country_id)
            request.session['django_language'] = 'en'
            
            # If user is logged in, also update their profile
            if request.user.is_authenticated:
                profile, created = UserProfile.objects.get_or_create(user=request.user)
                profile.country_id = int(country_id)
                profile.preferred_language = 'en'
                profile.save()
                
    return redirect(request.META.get('HTTP_REFERER', 'home'))

def set_language(request):
    if request.method == 'POST':
        language = request.POST.get('language')
        valid_codes = {code for code, _ in LANGUAGE_CHOICES}
        if language and language in valid_codes:
            request.session['django_language'] = language
            # Update profile if logged in
            if request.user.is_authenticated:
                profile, created = UserProfile.objects.get_or_create(user=request.user)
                profile.preferred_language = language
                profile.save()
    return redirect(request.META.get('HTTP_REFERER', 'home'))


import urllib3
import requests

def pincode_lookup(request):
    pincode = request.GET.get('pincode', '').strip()
    if not pincode or len(pincode) < 6:
        return JsonResponse({'success': False, 'message': 'Invalid pincode.'})
    
    import logging
    logger = logging.getLogger(__name__)
    
    # Try using Shiprocket Courier Serviceability
    try:
        from .shipping import ShiprocketService
        token = ShiprocketService._get_token()
        if token:
            url = "https://apiv2.shiprocket.in/v1/external/courier/serviceability/"
            params = {
                'pickup_postcode': '360004',  # Default warehouse pickup location (Rajkot, Gujarat)
                'delivery_postcode': pincode,
                'weight': '0.5',
                'cod': '0'  # Prepaid order serviceability check only (no COD)
            }
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {token}"
            }
            response = requests.get(url, params=params, headers=headers, timeout=8)
            if response.status_code == 200:
                res_data = response.json()
                if res_data.get('status') == 200:
                    data = res_data.get('data', {})
                    available_couriers = data.get('available_courier_companies', [])
                    if available_couriers:
                        # Extract ETD and location info
                        etds = []
                        city = ""
                        state = ""
                        for courier in available_couriers:
                            etd = courier.get('etd')
                            if etd:
                                etds.append(etd)
                            # Get city and state if available
                            if not city:
                                city = courier.get('city', '')
                            if not state:
                                state = courier.get('state', '')
                        
                        etd_str = "3-5 Days"
                        if etds:
                            try:
                                from datetime import datetime
                                parsed_dates = []
                                for e in etds:
                                    try:
                                        parsed_dates.append(datetime.strptime(e.split()[0], "%Y-%m-%d"))
                                    except:
                                        pass
                                if parsed_dates:
                                    fastest_date = min(parsed_dates)
                                    etd_str = fastest_date.strftime("%d %b, %Y")
                            except:
                                etd_str = etds[0]
                                
                        return JsonResponse({
                            'success': True,
                            'serviceable': True,
                            'city': city,
                            'state': state,
                            'etd': etd_str,
                            'message': f'Serviceable. Estimated delivery by {etd_str}.'
                        })
                    else:
                        return JsonResponse({
                            'success': False,
                            'serviceable': False,
                            'message': 'Pincode not serviceable by Shiprocket.'
                        })
    except Exception as e:
        logger.error(f"Shiprocket serviceability API error: {str(e)}")
        # Continue to fallback below

    # Fallback to Postal Pincode API if Shiprocket is unconfigured/offline
    try:
        url = f"https://api.postalpincode.in/pincode/{pincode}"
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        
        response = requests.get(url, headers=headers, verify=False, timeout=8)
        if response.status_code == 200:
            data = response.json()
            if data and data[0].get('Status') == 'Success':
                post_offices = data[0].get('PostOffice', [])
                city = ""
                state = ""
                if post_offices:
                    city = post_offices[0].get('District', '')
                    state = post_offices[0].get('State', '')
                
                # Mock a delivery date of 3-5 days
                from datetime import datetime, timedelta
                etd_date = datetime.now() + timedelta(days=4)
                etd_str = etd_date.strftime("%d %b, %Y")
                
                return JsonResponse({
                    'success': True,
                    'serviceable': True,
                    'city': city,
                    'state': state,
                    'etd': etd_str,
                    'message': f'Serviceable. Estimated delivery by {etd_str}.'
                })
            else:
                return JsonResponse({'success': False, 'message': 'Pincode not found.'})
        else:
            return JsonResponse({'success': False, 'message': 'Unable to verify pincode serviceability.'})
    except Exception as e:
        logger.error(f"Pincode lookup fallback error: {str(e)}")
        return JsonResponse({'success': False, 'message': f'Error checking pincode: {str(e)}'})


# ==========================================
# Shiprocket Checkout (Fastrr) Integration
# ==========================================

from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator
import decimal
import json
import logging
import uuid
from datetime import datetime, timezone as datetime_timezone
from store.shiprocket_checkout import generate_checkout_token, verify_webhook_signature

logger = logging.getLogger(__name__)

def shiprocket_auth_required(view_func):
    from store.shiprocket_checkout import get_checkout_credentials
    def wrapped_view(request, *args, **kwargs):
        api_key, _ = get_checkout_credentials()
        request_api_key = request.headers.get('X-Api-Key') or request.META.get('HTTP_X_API_KEY')
        if not request_api_key or request_api_key != api_key:
            return JsonResponse({"error": "Unauthorized"}, status=401)
        return view_func(request, *args, **kwargs)
    return wrapped_view

def get_paginated_response(request, queryset, serializer_class, key_name):
    page_num = request.GET.get('page', 1)
    limit_num = request.GET.get('limit', 100)
    
    try:
        page_num = int(page_num)
    except ValueError:
        page_num = 1
        
    try:
        limit_num = int(limit_num)
    except ValueError:
        limit_num = 100
        
    paginator = Paginator(queryset, limit_num)
    try:
        page_obj = paginator.page(page_num)
    except:
        page_obj = paginator.page(paginator.num_pages)
        
    host_uri = f"{request.scheme}://{request.get_host()}"
    serialized_items = serializer_class(page_obj.object_list, many=True, context={'host_uri': host_uri}).data
    
    return JsonResponse({
        "data": {
            "total": paginator.count,
            key_name: serialized_items
        }
    })

@csrf_exempt
@shiprocket_auth_required
def shiprocket_fetch_products(request):
    from .serializers import ProductSerializer
    queryset = Product.objects.filter(is_active=True).prefetch_related('images', 'variants', 'reviews').order_by('id')
    return get_paginated_response(request, queryset, ProductSerializer, "products")

@csrf_exempt
@shiprocket_auth_required
def shiprocket_fetch_collections(request):
    from .serializers import CategorySerializer
    queryset = Category.objects.filter(is_active=True).order_by('id')
    return get_paginated_response(request, queryset, CategorySerializer, "collections")

@csrf_exempt
@shiprocket_auth_required
def shiprocket_fetch_collection_products(request):
    collection_id = request.GET.get('collection_id')
    if not collection_id:
        return JsonResponse({"error": "Missing collection_id"}, status=400)
    from .serializers import ProductSerializer
    queryset = Product.objects.filter(category_id=collection_id, is_active=True).prefetch_related('images', 'variants', 'reviews').order_by('id')
    return get_paginated_response(request, queryset, ProductSerializer, "products")

@csrf_exempt
def shiprocket_initiate_checkout(request):
    if request.method != 'POST':
        return JsonResponse({"error": "Only POST allowed"}, status=405)
        
    try:
        if request.content_type == 'application/json':
            data = json.loads(request.body)
        else:
            data = request.POST
    except Exception:
        data = {}
        
    items = []
    
    product_id = data.get('product_id')
    variant_id = data.get('variant_id')
    quantity = int(data.get('quantity', 1))
    
    if product_id:
        product = get_object_or_404(Product, id=product_id, is_active=True)
        variant = None
        if variant_id:
            variant = get_object_or_404(ProductVariant, id=variant_id, product=product)
        v_id = str(variant.id) if variant else f"prod-{product.id}"
        items.append({
            "variant_id": v_id,
            "quantity": quantity
        })
    else:
        cart = get_or_create_cart(request)
        cart_items = cart.items.select_related('product', 'variant').all()
        if not cart_items.exists():
            return JsonResponse({"success": False, "message": "Your cart is empty"}, status=400)
            
        for item in cart_items:
            v_id = str(item.variant.id) if item.variant else f"prod-{item.product.id}"
            items.append({
                "variant_id": v_id,
                "quantity": item.quantity
            })
            
    redirect_url = f"{request.scheme}://{request.get_host()}/orders/?status=SUCCESS"
    timestamp_str = datetime.now(datetime_timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")
    
    res = generate_checkout_token(items, redirect_url, timestamp_str)
    return JsonResponse(res)

@csrf_exempt
def shiprocket_order_webhook(request):
    if request.method != 'POST':
        return JsonResponse({"error": "Only POST allowed"}, status=405)
        
    signature = request.headers.get('X-Api-HMAC-SHA256')
    if not verify_webhook_signature(request.body, signature):
        logger.warning("Shiprocket webhook signature verification failed.")
        return JsonResponse({"ok": False, "errorCode": "INVALID_SIGNATURE", "result": False}, status=401)
        
    try:
        payload = json.loads(request.body)
    except Exception:
        return JsonResponse({"ok": False, "errorCode": "INVALID_JSON", "result": False}, status=400)
        
    # Process order creation
    email = payload.get('email')
    phone = payload.get('phone') or "9999999999"
    status = payload.get('status')
    
    if status != 'SUCCESS':
        return JsonResponse({"ok": True, "errorCode": None, "result": True})
        
    shipping_address_data = payload.get('shipping_address') or {}
    
    # 1. Resolve User
    user = None
    if email:
        user = User.objects.filter(email=email).first()
    if not user and phone:
        user = User.objects.filter(phone=phone).first()
        
    if not user:
        # Create a guest user
        username = (email.split('@')[0] if email else "guest") + "_" + uuid.uuid4().hex[:4]
        user = User.objects.create(
            email=email or f"{username}@hypehavenhub.in",
            username=username,
            phone=phone,
            first_name=shipping_address_data.get('first_name', 'Guest'),
            last_name=shipping_address_data.get('last_name', '')
        )
        
    # 2. Resolve Shipping Address
    addr = Address.objects.create(
        user=user,
        type='other',
        full_name=f"{shipping_address_data.get('first_name', '')} {shipping_address_data.get('last_name', '')}".strip() or "Guest Customer",
        phone=phone,
        address_line1=shipping_address_data.get('line1', ''),
        address_line2=shipping_address_data.get('line2', '') or '',
        city=shipping_address_data.get('city', ''),
        state=shipping_address_data.get('state', ''),
        pincode=shipping_address_data.get('pincode', ''),
    )
    
    # 3. Resolve Order totals
    subtotal = decimal.Decimal(payload.get('subtotal_price') or payload.get('total_amount_payable') or 0)
    grand_total = decimal.Decimal(payload.get('total_amount_payable') or 0)
    discount = decimal.Decimal(payload.get('total_discount') or payload.get('coupon_discount') or 0)
    shipping_charges = decimal.Decimal(payload.get('shipping_charges') or 0)
    
    # Create Order
    order = Order.objects.create(
        user=user,
        address=addr,
        status='confirmed',
        subtotal=subtotal,
        discount_amount=discount,
        delivery_charge=shipping_charges,
        grand_total=grand_total,
        notes=f"Shiprocket Order ID: {payload.get('order_id')}"
    )
    
    # 4. Resolve Order Items
    cart_items = payload.get('cart_data', {}).get('items', [])
    for item in cart_items:
        variant_id = item.get('variant_id')
        quantity = int(item.get('quantity', 1))
        
        product = None
        variant = None
        
        # Check if the variant_id is encoded as "prod-<product_id>"
        if isinstance(variant_id, str) and variant_id.startswith('prod-'):
            try:
                prod_id = int(variant_id.split('-')[1])
                product = Product.objects.filter(id=prod_id).first()
            except (IndexError, ValueError):
                pass
        else:
            try:
                variant = ProductVariant.objects.filter(id=variant_id).first()
                if variant:
                    product = variant.product
            except (ValueError, TypeError):
                pass
                
        if not product and not variant:
            product = Product.objects.filter(is_active=True).first()
            
        unit_price = float(product.selling_price) if product else 0.0
        if variant:
            unit_price += float(variant.additional_price)
            
        OrderItem.objects.create(
            order=order,
            product=product,
            variant=variant,
            product_name=product.name if product else "Product",
            variant_label=variant.label if variant else "",
            quantity=quantity,
            unit_price=unit_price,
            total_price=unit_price * quantity
        )
        
    # 5. Create Payment record
    payment_type = payload.get('payment_type', 'PREPAID')
    payment_method = 'cod' if payment_type in ['CASH_ON_DELIVERY', 'COD'] else 'upi'
    payment_status = 'pending' if payment_method == 'cod' else 'success'
    
    Payment.objects.create(
        order=order,
        method=payment_method,
        status=payment_status,
        amount=grand_total,
        gateway_response=payload
    )
    
    # 6. Clear user's cart
    cart = Cart.objects.filter(user=user).first()
    if cart:
        cart.items.all().delete()
        
    return JsonResponse({"ok": True, "result": True})

import hmac
import hashlib

@csrf_exempt
@require_POST
def razorpay_webhook(request):
    """Webhook for Razorpay events like refund.processed or refund.failed."""
    webhook_secret = getattr(settings, 'RAZORPAY_WEBHOOK_SECRET', None)
    webhook_signature = request.headers.get('X-Razorpay-Signature')
    
    if not webhook_secret or not webhook_signature:
        return JsonResponse({"error": "Missing signature or secret"}, status=400)
        
    try:
        body = request.body
        expected_signature = hmac.new(
            webhook_secret.encode('utf-8'),
            body,
            hashlib.sha256
        ).hexdigest()
        
        if not hmac.compare_digest(expected_signature, webhook_signature):
            return JsonResponse({"error": "Invalid signature"}, status=400)
            
        payload = json.loads(body)
        event = payload.get('event')
        
        if event in ['refund.processed', 'refund.failed']:
            refund_obj = payload.get('payload', {}).get('refund', {}).get('entity', {})
            payment_id = refund_obj.get('payment_id')
            
            try:
                payment = Payment.objects.get(payment_id=payment_id)
                order = payment.order
                
                if event == 'refund.processed':
                    payment.status = 'refunded'
                    payment.save()
                    OrderTracking.objects.create(
                        order=order,
                        status='refunded',
                        description=f"Razorpay Webhook: Refund of INR {refund_obj.get('amount', 0)/100:.2f} processed successfully."
                    )
                elif event == 'refund.failed':
                    OrderTracking.objects.create(
                        order=order,
                        status='refund_failed',
                        description="Razorpay Webhook: Refund processing failed."
                    )
            except Payment.DoesNotExist:
                logger.warning(f"Webhook received for unknown payment_id: {payment_id}")
                
        elif event == 'order.paid':
            logger.info(f"Order paid webhook received: {payload}")
            # Magic checkout success handling can be done here if needed
        elif event == 'checkout.abandoned':
            logger.info(f"Abandoned checkout webhook received: {payload}")
            # Track abandoned carts for retargeting here
                
        return JsonResponse({"status": "ok"})
    except Exception as e:
        logger.error(f"Error processing webhook: {str(e)}")
        return JsonResponse({"error": str(e)}, status=500)

def contact_us(request):
    return render(request, 'store/contact_us.html')

def about_us(request):
    return render(request, 'store/about_us.html')

def privacy_policy(request):
    return render(request, 'store/privacy_policy.html')

def terms_conditions(request):
    return render(request, 'store/terms_conditions.html')

def refund_policy(request):
    return render(request, 'store/refund_policy.html')

def shipping_policy(request):
    return render(request, 'store/shipping_policy.html')
