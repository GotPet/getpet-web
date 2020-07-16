from django.test import SimpleTestCase

from utils.models import PageInfoEntry, PaginationInfo
from utils.utils import PaginatorWithPageLink, add_url_params


class AddUrlParamsTest(SimpleTestCase):

    def test_adding_empty_get_params_to_url(self):
        starting_url = 'https://www.getpet.lt/gyvunai/'
        full_url = add_url_params(starting_url, {})

        self.assertEqual(full_url, 'https://www.getpet.lt/gyvunai/')

    def test_adding_get_params_to_url(self):
        starting_url = 'gyvunai?page=2'
        full_url = add_url_params(starting_url, {'good': 1})

        self.assertEqual(full_url, 'gyvunai?page=2&good=1')

    def test_adding_get_params_to_full_url(self):
        starting_url = 'https://www.getpet.lt/gyvunai/?page=2'
        full_url = add_url_params(starting_url, {'good': 1})

        self.assertEqual(full_url, 'https://www.getpet.lt/gyvunai/?page=2&good=1')

    def test_modifying_get_param(self):
        starting_url = 'https://www.getpet.lt/gyvunai?page=2'
        full_url = add_url_params(starting_url, {'page': 3})

        self.assertEqual(full_url, 'https://www.getpet.lt/gyvunai?page=3')

    def test_deleting_get_param(self):
        starting_url = 'https://www.getpet.lt/gyvunai?page=2'
        full_url = add_url_params(starting_url, {'page': None})

        self.assertEqual(full_url, 'https://www.getpet.lt/gyvunai')


# noinspection PyUnresolvedReferences
class PaginationTest(SimpleTestCase):

    def test_empty_pagination(self):
        paginator = PaginatorWithPageLink([], 1,
                                          page_link_function=lambda x: f"page={x}")
        expected_result = PaginationInfo(
            previous_url=None, next_url=None,
            entries=[
                PageInfoEntry(text='1', url=None, is_active=True),
            ]
        )

        self.assertEqual(paginator.page(1).pagination_info(), expected_result)

    def test_pagination(self):
        paginator = PaginatorWithPageLink(list(range(20)), 1,
                                          page_link_function=lambda x: f"page={x}")
        expected_result = PaginationInfo(
            previous_url='page=4', next_url='page=6',
            entries=[
                PageInfoEntry(text='1', url='page=1', is_active=False),
                PageInfoEntry(text='...', url=None, is_active=False),
                PageInfoEntry(text='3', url='page=3', is_active=False),
                PageInfoEntry(text='4', url='page=4', is_active=False),
                PageInfoEntry(text='5', url=None, is_active=True),
                PageInfoEntry(text='6', url='page=6', is_active=False),
                PageInfoEntry(text='7', url='page=7', is_active=False),
                PageInfoEntry(text='...', url=None, is_active=False),
                PageInfoEntry(text='20', url='page=20', is_active=False)
            ]
        )

        self.assertEqual(paginator.page(5).pagination_info(), expected_result)
