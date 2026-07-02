from django import template
from store.models import ProductCountryPrice

register = template.Library()

@register.simple_tag
def get_localized_price(product, request):
    country = request.session.get('user_country', '')
    if not country and request.user.is_authenticated:
        country = getattr(request.user, 'country', '')

    if country:
        try:
            # Check if there is a custom price for this country
            country_price = product.country_prices.get(country_code=country)
            
            # Check for discount
            if product.discount_percent > 0:
                discounted = country_price.price * (1 - product.discount_percent / 100)
                return f"{country_price.currency} {discounted:.2f}"
                
            return f"{country_price.currency} {country_price.price}"
        except ProductCountryPrice.DoesNotExist:
            pass
            
    # Default fallback
    if product.discount_percent > 0:
        return f"₹{product.selling_price}"
    return f"₹{product.base_price}"

@register.simple_tag
def get_localized_base_price(product, request):
    country = request.session.get('user_country', '')
    if not country and request.user.is_authenticated:
        country = getattr(request.user, 'country', '')

    if country:
        try:
            country_price = product.country_prices.get(country_code=country)
            return f"{country_price.currency} {country_price.price}"
        except ProductCountryPrice.DoesNotExist:
            pass
            
    return f"₹{product.base_price}"

@register.simple_tag
def has_localized_discount(product):
    return product.discount_percent > 0
