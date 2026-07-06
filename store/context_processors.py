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
    ).order_by('name')
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

CURRENCY_NAMES = {
    'AED': 'United Arab Emirates Dirham',
    'ARS': 'Argentine Peso',
    'AUD': 'Australian Dollar',
    'BDT': 'Bangladeshi Taka',
    'BRL': 'Brazilian Real',
    'CAD': 'Canadian Dollar',
    'CHF': 'Swiss Franc',
    'CLP': 'Chilean Peso',
    'CNY': 'Chinese Yuan',
    'COP': 'Colombian Peso',
    'CZK': 'Czech Koruna',
    'DKK': 'Danish Krone',
    'EGP': 'Egyptian Pound',
    'EUR': 'Euro',
    'GBP': 'British Pound',
    'HKD': 'Hong Kong Dollar',
    'IDR': 'Indonesian Rupiah',
    'ILS': 'Israeli Shekel',
    'INR': 'Indian Rupee',
    'JPY': 'Japanese Yen',
    'KRW': 'South Korean Won',
    'MXN': 'Mexican Peso',
    'MYR': 'Malaysian Ringgit',
    'NOK': 'Norwegian Krone',
    'NZD': 'New Zealand Dollar',
    'PHP': 'Philippine Peso',
    'PKR': 'Pakistani Rupee',
    'PLN': 'Polish Zloty',
    'RUB': 'Russian Ruble',
    'SAR': 'Saudi Riyal',
    'SGD': 'Singapore Dollar',
    'THB': 'Thai Baht',
    'TRY': 'Turkish Lira',
    'TWD': 'Taiwan Dollar',
    'USD': 'United States Dollar',
    'VND': 'Vietnamese Dong',
    'ZAR': 'South African Rand'
}

def global_country_context(request):
    # Force language to English always
    request.session['django_language'] = 'en'
    
    if 'selected_country_id' not in request.session:
        try:
            ip = request.META.get('HTTP_X_FORWARDED_FOR', request.META.get('REMOTE_ADDR'))
            response = requests.get(f'http://ip-api.com/json/{ip}', timeout=2).json()
            country_code = response.get('countryCode', 'IN')
            
            country = CountrySetting.objects.filter(code=country_code).first()
            if country:
                request.session['selected_country_id'] = country.id
            else:
                request.session['selected_country_id'] = 1 # Fallback to 1
        except:
            request.session['selected_country_id'] = 1 # Fallback
            
    # Session se data templates me bhejna
    try:
        current_country = CountrySetting.objects.get(id=request.session.get('selected_country_id', 1))
    except CountrySetting.DoesNotExist:
        current_country = CountrySetting.objects.first()

    # Collect unique currencies
    unique_currencies = []
    seen_currencies = set()
    for country in CountrySetting.objects.all().order_by('name'):
        if country.currency_code not in seen_currencies:
            seen_currencies.add(country.currency_code)
            country.currency_name = CURRENCY_NAMES.get(country.currency_code, '')
            unique_currencies.append(country)
    unique_currencies.sort(key=lambda x: x.currency_code)

    return {
        'current_country': current_country,
        'unique_currencies': unique_currencies,
        'active_country': current_country.name if current_country else 'GLOBAL',
    }
