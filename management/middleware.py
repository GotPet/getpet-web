import datetime

from django.http import HttpRequest

from management.utils import django_now, try_parse_int


class AssociateSheltersMiddleware:
    SELECTED_SHELTER_COOKIE_ID = 'selected_shelter_id'
    _SHELTER_COOKIE_MAX_AGE = 365 * 24 * 60 * 60

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request: HttpRequest):
        from web.models import Shelter

        user = request.user
        selected_shelter_id = try_parse_int(request.COOKIES.pop(self.SELECTED_SHELTER_COOKIE_ID, None))
        selected_shelter = None

        if user.is_authenticated:
            selected_shelter = Shelter.user_selected_shelter(user, shelter_id=selected_shelter_id)

            if selected_shelter_id and not selected_shelter:
                selected_shelter = Shelter.user_selected_shelter(user)

            if selected_shelter:
                request.COOKIES[self.SELECTED_SHELTER_COOKIE_ID] = str(selected_shelter.id)

        response = self.get_response(request)

        if selected_shelter:
            expires = django_now() + datetime.timedelta(seconds=self._SHELTER_COOKIE_MAX_AGE)

            response.set_cookie(
                self.SELECTED_SHELTER_COOKIE_ID,
                str(selected_shelter.id),
                expires=expires.utctimetuple()
            )
        else:
            response.delete_cookie(self.SELECTED_SHELTER_COOKIE_ID)

        return response
