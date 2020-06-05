from html import escape

from django.template import Library
from django.template.defaultfilters import stringfilter
from django.utils.safestring import mark_safe

register = Library()


@register.filter(is_safe=True)
@stringfilter
def urltel(phone):
    escaped_phone = escape(phone)
    return mark_safe(f'<a href="tel:{escaped_phone}">{escaped_phone}</a>')
