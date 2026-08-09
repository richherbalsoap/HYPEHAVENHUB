import logging
from .models import Category, Cart, Wishlist, CountrySetting, LANGUAGE_CHOICES, SiteSetting

logger = logging.getLogger(__name__)

CURRENCY_NAMES = {
    'INR': 'Indian Rupee',
    'USD': 'US Dollar',
    'EUR': 'Euro',
    'GBP': 'British Pound',
    'CAD': 'Canadian Dollar',
    'AUD': 'Australian Dollar',
    'AED': 'UAE Dirham',
    'SGD': 'Singapore Dollar',
}


def site_settings(request):
    try:
        settings = SiteSetting.objects.first()
        if not settings:
            settings = SiteSetting.objects.create()
        return {'site_settings': settings}
    except Exception as e:
        logger.warning(f"site_settings context processor error: {e}")
        return {'site_settings': None}


def cart_count(request):
    count = 0
    try:
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
    except Exception as e:
        logger.warning(f"cart_count context processor error: {e}")
        count = 0
    return {'cart_count': count}


def wishlist_count(request):
    count = 0
    try:
        if request.user.is_authenticated:
            count = Wishlist.objects.filter(user=request.user).count()
    except Exception as e:
        logger.warning(f"wishlist_count context processor error: {e}")
        count = 0
    return {'wishlist_count': count}


def categories_processor(request):
    try:
        categories = Category.objects.filter(
            is_active=True,
            products__is_active=True
        ).distinct()
    except Exception as e:
        logger.warning(f"categories_processor error: {e}")
        categories = []
    return {'all_categories': categories, 'categories': categories}

categories_list = categories_processor


def company_dashboard_access(request):
    return {
        'has_company_access': request.user.is_authenticated and (request.user.is_staff or request.user.is_superuser)
    }


def country_settings(request):
    try:
        if 'selected_country_id' not in request.session:
            first_country = CountrySetting.objects.first()
            if first_country:
                request.session['selected_country_id'] = first_country.id

        selected_id = request.session.get('selected_country_id')
        current_country = None
        if selected_id:
            current_country = CountrySetting.objects.filter(id=selected_id).first()
        if not current_country:
            current_country = CountrySetting.objects.first()

        all_countries = list(CountrySetting.objects.all().order_by('name'))
        unique_currencies = []
        seen_currencies = set()
        for country in all_countries:
            if country.currency_code not in seen_currencies:
                seen_currencies.add(country.currency_code)
                country.currency_name = CURRENCY_NAMES.get(country.currency_code, '')
                unique_currencies.append(country)
        unique_currencies.sort(key=lambda x: x.currency_code)

        return {
            'current_country': current_country,
            'all_countries': all_countries,
            'unique_currencies': unique_currencies,
            'all_languages': LANGUAGE_CHOICES,
            'current_language': request.session.get('django_language', 'en'),
        }
    except Exception as e:
        logger.warning(f"country_settings context processor error: {e}")
        return {
            'current_country': None,
            'all_countries': [],
            'unique_currencies': [],
            'all_languages': LANGUAGE_CHOICES,
            'current_language': 'en',
        }

global_country_context = country_settings
