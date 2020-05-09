from django.http import HttpRequest

from django.http import HttpRequest

from management.constants import Constants
from management.utils import try_parse_int


class AssociateSheltersMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request: HttpRequest):
        from web.models import Shelter

        user = request.user
        selected_shelter_id = try_parse_int(request.COOKIES.pop(Constants.SELECTED_SHELTER_COOKIE_ID, None))
        selected_shelter = None

        if user.is_authenticated:
            selected_shelter = Shelter.user_selected_shelter(user, shelter_id=selected_shelter_id)

            if selected_shelter_id and not selected_shelter:
                selected_shelter = Shelter.user_selected_shelter(user)

            if selected_shelter:
                request.COOKIES[Constants.SELECTED_SHELTER_COOKIE_ID] = str(selected_shelter.id)

        response = self.get_response(request)

        if selected_shelter:
            response = selected_shelter.switch_shelter(response)
        else:
            response.delete_cookie(Constants.SELECTED_SHELTER_COOKIE_ID)

        return response
