from http.cookies import SimpleCookie

from django.contrib.auth.models import AnonymousUser
from django.http import HttpRequest, HttpResponse
from django.test import RequestFactory, TestCase

from management.constants import Constants
from management.middleware import AssociateSheltersMiddleware
from web.tests.factories import ShelterFactory, UserFactory


class AssociateSheltersMiddlewareTest(TestCase):
    SELECTED_SHELTER_COOKIE_ID = Constants.SELECTED_SHELTER_COOKIE_ID

    def setUp(self):
        self.request_factory = RequestFactory()

        self.user_with_no_associated_shelters = UserFactory()
        self.user_associated_to_shelter1 = UserFactory()

        self.shelter1 = ShelterFactory.create(authenticated_users=[self.user_associated_to_shelter1])
        self.shelter2 = ShelterFactory.create()

    def _make_request(self, user, cookies_dict, path=None) -> HttpRequest:
        path = path or '/admin/test/'
        self.request_factory.cookies = SimpleCookie(cookies_dict)
        request = self.request_factory.get(path)
        request.user = user

        return request

    # noinspection PyMethodMayBeStatic
    def _make_get_response_func(self):
        response = HttpResponse("OK")
        get_response = lambda r: response

        return get_response

    def test_non_admin_endpoint(self):
        request = self._make_request(
            user=AnonymousUser(),
            cookies_dict={},
            path='/test/'
        )
        get_response = self._make_get_response_func()

        response = AssociateSheltersMiddleware(get_response)(request)

        self.assertIsNone(response.cookies.get(self.SELECTED_SHELTER_COOKIE_ID, None))

    def test_anonymous_user(self):
        request = self._make_request(
            user=AnonymousUser(),
            cookies_dict={},
        )
        get_response = self._make_get_response_func()

        response = AssociateSheltersMiddleware(get_response)(request)

        self.assertEqual(response.cookies[self.SELECTED_SHELTER_COOKIE_ID].value, "")

    def test_anonymous_user_with_cookie(self):
        request = self._make_request(
            user=AnonymousUser(),
            cookies_dict={self.SELECTED_SHELTER_COOKIE_ID: str(self.shelter1.pk)},
        )
        get_response = self._make_get_response_func()

        response = AssociateSheltersMiddleware(get_response)(request)

        self.assertEqual(response.cookies[self.SELECTED_SHELTER_COOKIE_ID].value, "")
        self.assertFalse(self.SELECTED_SHELTER_COOKIE_ID in request.COOKIES)
        self.assertIsNone(getattr(request, "user_selected_shelter", "default_value"))

    def test_user_no_associated_shelter(self):
        request = self._make_request(
            user=self.user_with_no_associated_shelters,
            cookies_dict={},
        )
        get_response = self._make_get_response_func()

        response = AssociateSheltersMiddleware(get_response)(request)

        self.assertEqual(response.cookies[self.SELECTED_SHELTER_COOKIE_ID].value, "")
        self.assertFalse(self.SELECTED_SHELTER_COOKIE_ID in request.COOKIES)
        self.assertIsNone(getattr(request, "user_selected_shelter", "default_value"))

    def test_user_no_associated_shelter_with_cookie(self):
        request = self._make_request(
            user=self.user_with_no_associated_shelters,
            cookies_dict={self.SELECTED_SHELTER_COOKIE_ID: str(self.shelter1.pk)},
        )
        get_response = self._make_get_response_func()

        response = AssociateSheltersMiddleware(get_response)(request)

        self.assertEqual(response.cookies[self.SELECTED_SHELTER_COOKIE_ID].value, "")
        self.assertFalse(self.SELECTED_SHELTER_COOKIE_ID in request.COOKIES)
        self.assertIsNone(getattr(request, "user_selected_shelter", "default_value"))

    def test_user_no_associated_shelter_invalid_cookie(self):
        request = self._make_request(
            user=self.user_with_no_associated_shelters,
            cookies_dict={self.SELECTED_SHELTER_COOKIE_ID: "something wrong"},
        )
        get_response = self._make_get_response_func()

        response = AssociateSheltersMiddleware(get_response)(request)

        self.assertEqual(response.cookies[self.SELECTED_SHELTER_COOKIE_ID].value, "")
        self.assertFalse(self.SELECTED_SHELTER_COOKIE_ID in request.COOKIES)
        self.assertIsNone(getattr(request, "user_selected_shelter", "default_value"))

    def test_user_with_associated_shelter_no_cookie(self):
        request = self._make_request(
            user=self.user_associated_to_shelter1,
            cookies_dict={},
        )
        get_response = self._make_get_response_func()

        response = AssociateSheltersMiddleware(get_response)(request)

        shelter1_cookie_str = str(self.shelter1.pk)
        self.assertEqual(response.cookies[self.SELECTED_SHELTER_COOKIE_ID].value, shelter1_cookie_str)
        self.assertEqual(request.COOKIES.get(self.SELECTED_SHELTER_COOKIE_ID, "Incorrct"), shelter1_cookie_str)
        self.assertEqual(getattr(request, "user_selected_shelter", "default_value"), self.shelter1)

    def test_user_with_associated_shelter_other_shelter_cookie(self):
        request = self._make_request(
            user=self.user_associated_to_shelter1,
            cookies_dict={self.SELECTED_SHELTER_COOKIE_ID: str(self.shelter2.pk)},
        )
        get_response = self._make_get_response_func()

        response = AssociateSheltersMiddleware(get_response)(request)

        shelter1_cookie_str = str(self.shelter1.pk)
        self.assertEqual(response.cookies[self.SELECTED_SHELTER_COOKIE_ID].value, shelter1_cookie_str)
        self.assertEqual(request.COOKIES.get(self.SELECTED_SHELTER_COOKIE_ID, "Incorrct"), shelter1_cookie_str)
        self.assertEqual(getattr(request, "user_selected_shelter", "default_value"), self.shelter1)

    def test_user_with_associated_shelter_correct_cookie(self):
        request = self._make_request(
            user=self.user_associated_to_shelter1,
            cookies_dict={self.SELECTED_SHELTER_COOKIE_ID: str(self.shelter1.pk)},
        )
        get_response = self._make_get_response_func()

        response = AssociateSheltersMiddleware(get_response)(request)

        shelter1_cookie_str = str(self.shelter1.pk)
        self.assertEqual(response.cookies[self.SELECTED_SHELTER_COOKIE_ID].value, shelter1_cookie_str)
        self.assertEqual(request.COOKIES.get(self.SELECTED_SHELTER_COOKIE_ID, "Incorrct"), shelter1_cookie_str)
        self.assertEqual(getattr(request, "user_selected_shelter", "default_value"), self.shelter1)
