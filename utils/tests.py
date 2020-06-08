from django.test import SimpleTestCase, TestCase

from utils.utils import add_url_params


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
