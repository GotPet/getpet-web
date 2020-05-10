from django.http import HttpRequest, HttpResponse

from management.constants import Constants


class AssociateSheltersMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        from web.models import Shelter

        user = request.user

        user_selected_shelter = Shelter.user_selected_shelter(user=user, request=request)

        if user_selected_shelter:
            request.COOKIES[Constants.SELECTED_SHELTER_COOKIE_ID] = str(user_selected_shelter.id)
        else:
            request.COOKIES.pop(Constants.SELECTED_SHELTER_COOKIE_ID, None)

        request.user_selected_shelter = user_selected_shelter

        response: HttpResponse = self.get_response(request)

        # Cookie was changed in get_response
        if response_shelter_cookie := response.cookies.pop(Constants.SELECTED_SHELTER_COOKIE_ID, None):
            user_selected_shelter = Shelter.user_associated_shelter_by_id(
                user=user,
                shelter_id=response_shelter_cookie.value
            )

        if user_selected_shelter:
            user_selected_shelter.switch_shelter(response)
        else:
            response.delete_cookie(Constants.SELECTED_SHELTER_COOKIE_ID)

        return response
