from django.contrib.auth.decorators import login_required, permission_required, user_passes_test

from web.models import Shelter

rec_associated_shelter_required = user_passes_test(lambda u: Shelter.user_selected_shelter(u) is not None)

def associated_shelter_required(func=None, login_url=None):

    return login_required(rec_associated_shelter_required(), login_url=login_url)
