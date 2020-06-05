from html import escape

from django.template import Library
from django.template.defaultfilters import stringfilter
from django.utils.safestring import mark_safe

register = Library()


@register.filter(is_safe=True)
@stringfilter
def urltel(phone):
    phone = phone.replace(' ', '-')
    escaped_phone = escape(phone, quote=True)
    return mark_safe(f'<a href="tel:{escaped_phone}">{escaped_phone}</a>')
