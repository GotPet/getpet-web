from django.template import Library
from django.templatetags.static import static

from utils.utils import full_path as make_full_path

register = Library()


@register.simple_tag
def static_full(path: str) -> str:
    return make_full_path(static(path))


@register.simple_tag
def full_path(path: str) -> str:
    return make_full_path(path)
