from django.template import Library

from getpet import settings

register = Library()


@register.simple_tag
def settings_value(name):
    return getattr(settings, name, None)
