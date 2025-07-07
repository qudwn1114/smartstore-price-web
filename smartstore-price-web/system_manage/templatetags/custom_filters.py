from decimal import Decimal
from django import template

register = template.Library()

@register.filter
def strip_decimal(value, max_places=5):
    if not isinstance(value, Decimal):
        return value
    return ('{0:.%df}' % max_places).format(value).rstrip('0').rstrip('.')