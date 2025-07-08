from decimal import Decimal
from django import template
from django.utils import timezone, timesince

register = template.Library()

@register.filter
def strip_decimal(value, max_places=5):
    if not isinstance(value, Decimal):
        return value
    return ('{0:.%df}' % max_places).format(value).rstrip('0').rstrip('.')


@register.filter
def is_birthday(birthday):
    if not birthday:
        return False
    today = timezone.localdate()
    return birthday.month == today.month and birthday.day == today.day

@register.filter
def timesince_custom(value):
    if not value:
        return ''
    delta = timezone.now() - value
    if delta.total_seconds() < 60:
        return "방금 전"
    return timesince.timesince(value) + " 전"