from django.http import HttpRequest


def user_shelters(request: HttpRequest):
    from web.models import Shelter
    user = request.user

    user_selected_shelter = None
    user_available_shelters = Shelter.objects.none()
    if user.is_authenticated:
        user_available_shelters = Shelter.objects.filter(authenticated_users=user)
        user_selected_shelter = user_available_shelters.first()

    return {
        'user_selected_shelter': user_selected_shelter,
        'user_available_shelters': user_available_shelters,
    }
