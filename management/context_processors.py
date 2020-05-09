from django.http import HttpRequest


def user_shelters(request: HttpRequest):
    from web.models import Shelter
    user = request.user

    user_available_shelters = Shelter.user_associated_shelters(user)
    user_selected_shelter = Shelter.user_selected_shelter(user=user, request=request)

    return {
        'user_selected_shelter': user_selected_shelter,
        'user_available_shelters': user_available_shelters,
    }
