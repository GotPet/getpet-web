from typing import Optional

from django.db.models import ImageField
from django.template import Library

from getpet.settings import MEDIA_URL, DEBUG

register = Library()


# noinspection PyUnresolvedReferences
@register.simple_tag
def resized_image(image: ImageField, width: int, height: Optional[int] = None):
    if image:
        if DEBUG:
            return image.url

        if width and height:
            return image.url.replace(MEDIA_URL, f'/{width}x{height}{MEDIA_URL}')
        elif width:
            return image.url.replace(MEDIA_URL, f'/w-{width}{MEDIA_URL}')

    return None
