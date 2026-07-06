from django import template
from store.translations import translate as _translate

register = template.Library()


@register.simple_tag(takes_context=True)
def t(context, key):
    """
    Translate a UI string key into the visitor's selected language.
    Usage: {% load i18n_store %}  then  {% t "add_to_cart" %}
    """
    request = context.get('request')
    if not request:
        return key
    return _translate(request, key)


@register.simple_tag(takes_context=True)
def format_price(context, amount):
    """
    Format a generic amount with the active country's currency symbol.
    """
    country = context.get('current_country')
    if country:
        return f"{country.currency_symbol}{amount}"
    return f"₹{amount}"

@register.simple_tag(takes_context=True)
def display_product_price(context, product):
    """
    Display a product's price for the active country, considering discounts.
    """
    country = context.get('current_country')
    if not country:
        return f"₹{product.selling_price}"
        
    country_price = product.get_price_for_country(country.id)
    # Apply discount
    if product.discount_percent > 0:
        country_price = round(country_price * (1 - product.discount_percent / 100), 2)
    return f"{country.currency_symbol}{country_price}"


@register.simple_tag(takes_context=True)
def get_cart_subtotal(context, cart):
    country = context.get('current_country')
    if not country:
        return float(cart.subtotal)
    
    subtotal = 0
    for item in cart.items.all():
        p = item.product.get_price_for_country(country.id)
        if item.product.discount_percent > 0:
            p = round(p * (1 - item.product.discount_percent / 100), 2)
        if item.variant:
            p += item.variant.additional_price
        subtotal += p * item.quantity
    return float(subtotal)

@register.simple_tag(takes_context=True)
def get_cart_total(context, cart, subtotal):
    country = context.get('current_country')
    discount_amount = 0.0
    if cart.coupon and cart.coupon.is_valid():
        discount_val = float(cart.coupon.discount_value)
        if cart.coupon.discount_type == 'percent':
            disc = float(subtotal) * discount_val / 100
            if cart.coupon.max_discount_amount:
                disc = min(disc, float(cart.coupon.max_discount_amount))
            discount_amount = round(disc, 2)
        else:
            discount_amount = min(discount_val, float(subtotal))
    
    delivery = float(country.shipping_charge) if country else 0.0
    return float(float(subtotal) - discount_amount + delivery)

@register.simple_tag(takes_context=True)
def get_cart_item_total(context, item):
    country = context.get('current_country')
    if not country:
        return float(item.total_price)
    
    p = item.product.get_price_for_country(country.id)
    if item.product.discount_percent > 0:
        p = round(p * (1 - item.product.discount_percent / 100), 2)
    if item.variant:
        p += item.variant.additional_price
    return float(p * item.quantity)

@register.simple_tag(takes_context=True)
def get_cart_item_price(context, item):
    country = context.get('current_country')
    if not country:
        return float(item.unit_price)
    
    p = item.product.get_price_for_country(country.id)
    if item.product.discount_percent > 0:
        p = round(p * (1 - item.product.discount_percent / 100), 2)
    if item.variant:
        p += item.variant.additional_price
    return float(p)
