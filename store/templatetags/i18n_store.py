from django import template
from django.utils.safestring import mark_safe
from store.translations import translate as _translate

register = template.Library()


@register.simple_tag(takes_context=True)
def t(context, key):
    """
    Translate a UI string key into the visitor's selected language.
    Usage: {% load i18n_store %}  then  {% t "add_to_cart" %}
    """
    try:
        request = context.get('request')
        if not request:
            return key
        return mark_safe(_translate(request, key))
    except Exception:
        return key


@register.simple_tag(takes_context=True)
def format_price(context, amount):
    """
    Format a generic amount with the active country's currency symbol.
    """
    try:
        if amount is None:
            amount = 0
        country = context.get('current_country')
        symbol = getattr(country, 'currency_symbol', '₹') if country else '₹'
        return f"{symbol}{amount}"
    except Exception:
        return f"₹{amount or 0}"


@register.simple_tag(takes_context=True)
def display_product_price(context, product):
    """
    Display a product's price for the active country, considering discounts.
    """
    try:
        if not product:
            return "₹0"
        country = context.get('current_country')
        symbol = getattr(country, 'currency_symbol', '₹') if country else '₹'
        
        selling_price = getattr(product, 'selling_price', 0) or 0
        if not country or not hasattr(product, 'get_price_for_country'):
            return f"{symbol}{selling_price}"
            
        country_price = product.get_price_for_country(getattr(country, 'id', 1))
        discount_percent = getattr(product, 'discount_percent', 0) or 0
        if discount_percent > 0:
            country_price = round(country_price * (1 - discount_percent / 100), 2)
        return f"{symbol}{country_price}"
    except Exception:
        return "₹0"


@register.simple_tag(takes_context=True)
def get_cart_subtotal(context, cart):
    try:
        if not cart:
            return 0.0
        country = context.get('current_country')
        if not country or not hasattr(country, 'id'):
            return float(getattr(cart, 'subtotal', 0) or 0.0)
        
        subtotal = 0
        for item in cart.items.all():
            if not item.product:
                continue
            p = item.product.get_price_for_country(country.id)
            discount_percent = getattr(item.product, 'discount_percent', 0) or 0
            if discount_percent > 0:
                p = round(p * (1 - discount_percent / 100), 2)
            if item.variant and getattr(item.variant, 'additional_price', None):
                p += item.variant.additional_price
            subtotal += p * item.quantity
        return float(subtotal)
    except Exception:
        return float(getattr(cart, 'subtotal', 0) if cart else 0.0)


@register.simple_tag(takes_context=True)
def get_cart_total(context, cart, subtotal):
    try:
        subtotal = float(subtotal or 0.0)
        country = context.get('current_country')
        discount_amount = 0.0
        if cart and getattr(cart, 'coupon', None) and cart.coupon.is_valid():
            discount_val = float(cart.coupon.discount_value or 0)
            if cart.coupon.discount_type == 'percent':
                disc = subtotal * discount_val / 100
                if cart.coupon.max_discount_amount:
                    disc = min(disc, float(cart.coupon.max_discount_amount))
                discount_amount = round(disc, 2)
            else:
                discount_amount = min(discount_val, subtotal)
        
        delivery = float(getattr(country, 'shipping_charge', 0.0) or 0.0) if country else 0.0
        return float(subtotal - discount_amount + delivery)
    except Exception:
        return float(subtotal or 0.0)


@register.simple_tag(takes_context=True)
def get_cart_item_total(context, item):
    try:
        if not item or not item.product:
            return 0.0
        country = context.get('current_country')
        if not country or not hasattr(country, 'id'):
            return float(getattr(item, 'total_price', 0) or 0.0)
        
        p = item.product.get_price_for_country(country.id)
        discount_percent = getattr(item.product, 'discount_percent', 0) or 0
        if discount_percent > 0:
            p = round(p * (1 - discount_percent / 100), 2)
        if item.variant and getattr(item.variant, 'additional_price', None):
            p += item.variant.additional_price
        return float(p * item.quantity)
    except Exception:
        return float(getattr(item, 'total_price', 0) if item else 0.0)


@register.simple_tag(takes_context=True)
def get_cart_item_price(context, item):
    try:
        if not item or not item.product:
            return 0.0
        country = context.get('current_country')
        if not country or not hasattr(country, 'id'):
            return float(getattr(item, 'unit_price', 0) or 0.0)
        
        p = item.product.get_price_for_country(country.id)
        discount_percent = getattr(item.product, 'discount_percent', 0) or 0
        if discount_percent > 0:
            p = round(p * (1 - discount_percent / 100), 2)
        if item.variant and getattr(item.variant, 'additional_price', None):
            p += item.variant.additional_price
        return float(p)
    except Exception:
        return float(getattr(item, 'unit_price', 0) if item else 0.0)
