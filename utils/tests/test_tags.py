from django.test import SimpleTestCase

from utils.templatetags.tel_tags import urltel


class TelephoneTagTest(SimpleTestCase):

    def test_regular_phone(self):
        phone = urltel("+37080766215")

        self.assertEqual(phone, """<a href="tel:+37080766215">+37080766215</a>""")

    def test_phone_with_spaces(self):
        phone = urltel("+370 807 66215")

        self.assertEqual(phone, """<a href="tel:+37080766215">+370-807-66215</a>""")

    def test_phone_with_spaces_and_parentheses(self):
        phone = urltel("+(370) 807 66215")

        self.assertEqual(phone, """<a href="tel:+37080766215">+(370)-807-66215</a>""")
