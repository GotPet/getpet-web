from django.http import HttpRequest, HttpResponse

from management.constants import Constants
from management.utils import try_parse_int


class AssociateSheltersMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        from web.models import Shelter

        user = request.user
        selected_shelter_id = try_parse_int(request.COOKIES.pop(Constants.SELECTED_SHELTER_COOKIE_ID, None))
        selected_shelter = None

        if user.is_authenticated:
            selected_shelter = Shelter.user_selected_shelter(user=user, request=None, shelter_id=selected_shelter_id)

            if selected_shelter_id and not selected_shelter:
                selected_shelter = Shelter.user_selected_shelter(user=user, request=None)

            if selected_shelter:
                request.COOKIES[Constants.SELECTED_SHELTER_COOKIE_ID] = str(selected_shelter.id)

        response: HttpResponse = self.get_response(request)

        # Cookie was changed in get_response
        if response_shelter_cookie := response.cookies.pop(Constants.SELECTED_SHELTER_COOKIE_ID, None):
            selected_shelter = Shelter.user_selected_shelter(user=user, request=None, shelter_id=response_shelter_cookie.value)

        if selected_shelter:
            response = selected_shelter.switch_shelter(response)
        else:
            response.delete_cookie(Constants.SELECTED_SHELTER_COOKIE_ID)

        return response
