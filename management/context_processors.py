from django.http import HttpRequest


def user_shelters(request: HttpRequest):
    if hasattr(request, 'user_selected_shelter'):
        return {
            'user_selected_shelter': request.user_selected_shelter,
        }

    return {}
