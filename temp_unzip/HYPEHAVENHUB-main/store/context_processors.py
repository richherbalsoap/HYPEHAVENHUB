import requests
from .models import Category, Cart, Wishlist, CountrySetting, LANGUAGE_CHOICES


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

def global_country_context(request):
    if 'selected_country_id' not in request.session:
        try:
            ip = request.META.get('HTTP_X_FORWARDED_FOR', request.META.get('REMOTE_ADDR'))
            response = requests.get(f'http://ip-api.com/json/{ip}', timeout=2).json()
            country_code = response.get('countryCode', 'IN')
            
            country = CountrySetting.objects.filter(code=country_code).first()
            if country:
                request.session['selected_country_id'] = country.id
                request.session['django_language'] = country.default_language
            else:
                request.session['selected_country_id'] = 1 # Fallback to 1
        except:
            request.session['selected_country_id'] = 1 # Fallback
            
    # Session se data templates me bhejna
    try:
        current_country = CountrySetting.objects.get(id=request.session.get('selected_country_id', 1))
    except CountrySetting.DoesNotExist:
        current_country = CountrySetting.objects.first()

    return {
        'current_country': current_country,
        'all_countries': CountrySetting.objects.all().order_by('name'),
        'active_country': current_country.name if current_country else 'GLOBAL',
        'all_languages': LANGUAGE_CHOICES,
    }
