from django.http import HttpRequest


def user_shelters(request: HttpRequest):
    # noinspection PyUnresolvedReferences
    return {
        'user_selected_shelter': request.user_selected_shelter,
    }
