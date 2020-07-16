import re
from html import escape

from django.template import Library
from django.template.defaultfilters import stringfilter
from django.utils.safestring import mark_safe

register = Library()


@register.filter(is_safe=True)
@stringfilter
def urltel(phone):
    phone_only_digits_or_plus = re.sub('[^0-9+]', '', phone)
    escaped_phone = escape(phone.replace(' ', '-'), quote=True)
    return mark_safe(f'<a href="tel:{phone_only_digits_or_plus}">{escaped_phone}</a>')
