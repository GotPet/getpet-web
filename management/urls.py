from django.urls import path

from management.views import ShelterPetsListView, no_associated_shelter

urlpatterns = [
    path('', ShelterPetsListView.as_view(), name="management_pets_list"),
    path('no-shelter/', no_associated_shelter, name="management_no_associated_shelter"),
]
