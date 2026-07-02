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
