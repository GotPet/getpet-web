from django.template import Library
from django.template.defaultfilters import stringfilter

register = Library()


@register.filter(is_safe=True)
@stringfilter
def lower_first(value):
    """Lowercase the first character of the value."""
    return value and value[0].lower() + value[1:]
