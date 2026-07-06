from django import template
from store.models import ProductPrice, CountrySetting

register = template.Library()

@register.simple_tag
def get_localized_price(product, request):
    country_id = request.session.get('selected_country_id')

    if country_id:
        try:
            country = CountrySetting.objects.get(id=country_id)
            try:
                country_price = product.country_prices.get(country=country)
                price = country_price.price
            except ProductPrice.DoesNotExist:
                price = product.base_price
            
            # Check for discount
            if product.discount_percent > 0:
                discounted = price * (1 - product.discount_percent / 100)
                return f"{country.currency_symbol}{discounted:.2f}"
                
            return f"{country.currency_symbol}{price}"
        except CountrySetting.DoesNotExist:
            pass
            
    # Default fallback
    if product.discount_percent > 0:
        return f"₹{product.selling_price}"
    return f"₹{product.base_price}"

@register.simple_tag
def get_localized_base_price(product, request):
    country_id = request.session.get('selected_country_id')

    if country_id:
        try:
            country = CountrySetting.objects.get(id=country_id)
            try:
                price = product.country_prices.get(country=country).price
            except ProductPrice.DoesNotExist:
                price = product.base_price
            return f"{country.currency_symbol}{price}"
        except CountrySetting.DoesNotExist:
            pass
            
    return f"₹{product.base_price}"

@register.simple_tag
def has_localized_discount(product):
    return product.discount_percent > 0
