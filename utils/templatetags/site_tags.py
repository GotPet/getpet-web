from urllib.parse import urljoin

from django.template import Library
from django.templatetags.static import static

from getpet import settings

register = Library()


@register.simple_tag
def static_full(path):
    return urljoin(settings.BASE_DOMAIN, static(path))


@register.simple_tag
def full_path(path):
    return urljoin(settings.BASE_DOMAIN, path)
