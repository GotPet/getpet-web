from typing import Optional
from urllib.parse import urljoin

from django.db.models.fields.files import ImageFieldFile
from django.template import Library

from getpet.settings import BASE_REAL_DOMAIN, DEBUG

register = Library()


@register.simple_tag
def resized_image(image, width: int, height: Optional[int] = None) -> Optional[str]:
    if image is None:
        return None

    if isinstance(image, str):
        url = image
    elif isinstance(image, ImageFieldFile):
        url = image.url
    else:
        raise TypeError(f"Unsupported type of image {type(image)}")

    options = f'width={width},quality=85,fit=cover,f=auto,metadata=none'

    if height:
        options += f',height={height}'

    optimized_url = f'/cdn-cgi/image/{options}{url}'

    if DEBUG:
        return urljoin(BASE_REAL_DOMAIN, optimized_url)

    return optimized_url
