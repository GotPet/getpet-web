from django.contrib.auth.decorators import user_passes_test
from django.urls import reverse

from web.models import Shelter


def associated_shelter_required(function=None, login_url=None):
    """
    Decorator for views that checks that the user is logged in and belongs to one of the shelters, redirecting
    to the log-in page if necessary or no associated shelter view.
    """

    actual_decorator = user_passes_test(
        lambda u: u.is_authenticated and Shelter.user_selected_shelter(u) is not None,
        login_url=login_url,
        redirect_field_name='management_no_associated_shelter'
    )
    if function:
        return actual_decorator(function)
    return actual_decorator
