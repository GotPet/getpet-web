from typing import Optional

from django.db.models.fields.files import ImageFieldFile
from django.template import Library

from getpet.settings import MEDIA_URL, DEBUG

register = Library()


# noinspection PyUnresolvedReferences
@register.simple_tag
def resized_image(image, width: int, height: Optional[int] = None):
    if image is None:
        return None

    if isinstance(image, str):
        url = image
    elif isinstance(image, ImageFieldFile):
        url = image.url
    else:
        raise TypeError(f"Unsupported type of image {type(image)}")

    if DEBUG:
        return url

    if width and height:
        return url.replace(MEDIA_URL, f'/{width}x{height}{MEDIA_URL}')
    elif width:
        return url.replace(MEDIA_URL, f'/w-{width}{MEDIA_URL}')

    return None
