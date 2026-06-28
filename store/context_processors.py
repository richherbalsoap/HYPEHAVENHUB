from .models import Category, Cart, Wishlist


def cart_count(request):
    count = 0
    if request.user.is_authenticated:
        try:
            cart = Cart.objects.get(user=request.user)
            count = cart.total_items
        except Cart.DoesNotExist:
            count = 0
    else:
        session_key = request.session.session_key
        if session_key:
            try:
                cart = Cart.objects.get(session_key=session_key)
                count = cart.total_items
            except Cart.DoesNotExist:
                count = 0
    return {'cart_count': count}


def wishlist_count(request):
    count = 0
    if request.user.is_authenticated:
        count = Wishlist.objects.filter(user=request.user).count()
    return {'wishlist_count': count}


def categories_list(request):
    categories = Category.objects.filter(
        is_active=True,
    ).order_by('name').prefetch_related('subcategories')
    return {'all_categories': categories}


def company_dashboard_access(request):
    can_access = False
    if request.user.is_authenticated:
        can_access = (
            request.user.is_superuser or
            request.user.is_staff or
            request.user.groups.filter(name='Company').exists()
        )
    return {'can_access_company_dashboard': can_access}


def shiprocket_settings(request):
    from django.conf import settings
    return {
        'SHIPROCKET_CHECKOUT_API_KEY': getattr(settings, 'SHIPROCKET_CHECKOUT_API_KEY', ''),
    }

