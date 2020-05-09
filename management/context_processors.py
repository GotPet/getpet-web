from django.http import HttpRequest

from management.constants import Constants
from management.utils import try_parse_int


def user_shelters(request: HttpRequest):
    from web.models import Shelter
    user = request.user
    selected_shelter_id = try_parse_int(request.COOKIES.get(Constants.SELECTED_SHELTER_COOKIE_ID))

    user_available_shelters = Shelter.user_associated_shelters(user)
    user_selected_shelter = Shelter.user_selected_shelter(user, selected_shelter_id)

    return {
        'user_selected_shelter': user_selected_shelter,
        'user_available_shelters': user_available_shelters,
    }
