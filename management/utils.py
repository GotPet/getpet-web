import logging
from json import dumps
from urllib.parse import urlencode, unquote, urlparse, parse_qsl, ParseResult

from django.core.paginator import Page, Paginator

logger = logging.getLogger(__name__)


def image_url_with_size_params(url: str, size: int) -> str:
    return add_url_params(url, {'w': size, 'h': size})


class PageWithPageLink(Page):
    def __init__(self, page_link_function, object_list, number, paginator):
        self._page_link_function = page_link_function
        super().__init__(object_list, number, paginator)

    def previous_page_link(self):
        if self.has_previous():
            return self.page_link(self.previous_page_number())

    def next_page_link(self):
        if self.has_next():
            return self.page_link(self.next_page_number())

    def page_link(self, page_number):
        return self._page_link_function(page_number)


class PaginatorWithPageLink(Paginator):
    def _get_page(self, *args, **kwargs):
        return PageWithPageLink(self._page_link_function, *args, **kwargs)

    def __init__(self, object_list, per_page, page_link_function, orphans=0, allow_empty_first_page=True):
        super().__init__(object_list, per_page, orphans, allow_empty_first_page)
        self._page_link_function = page_link_function


def add_url_params(url, params):
    """ Add GET params to provided URL being aware of existing.
    :param url: string of target URL
    :param params: dict containing requested params to be added
    :return: string with updated URL
    >> url = 'http://stackoverflow.com/test?answers=true'
    >> new_params = {'answers': False, 'data': ['some','values']}
    >> add_url_params(url, new_params)
    'http://stackoverflow.com/test?data=some&data=values&answers=false'
    """
    # Unquoting URL first so we don't loose existing args
    url = unquote(url)
    # Extracting url info
    parsed_url = urlparse(url)
    # Extracting URL arguments from parsed URL
    get_args = parsed_url.query
    # Converting URL arguments to dict
    parsed_get_args = dict(parse_qsl(get_args))
    # Merging URL arguments dict with new params
    parsed_get_args.update(params)

    parsed_get_args = {k: v for k, v in parsed_get_args.items() if v is not None}

    # Bool and Dict values should be converted to json-friendly values
    # you may throw this part away if you don't like it :)
    parsed_get_args.update(
        {k: dumps(v) for k, v in parsed_get_args.items()
         if isinstance(v, (bool, dict))}
    )

    # Converting URL argument to proper query string
    encoded_get_args = urlencode(parsed_get_args, doseq=True)
    # Creating new parsed result object based on provided with new
    # URL arguments. Same thing happens inside of urlparse.
    new_url = ParseResult(
        parsed_url.scheme, parsed_url.netloc, parsed_url.path,
        parsed_url.params, encoded_get_args, parsed_url.fragment
    ).geturl()

    return new_url
