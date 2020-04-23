from django.urls import path

from management.views import ShelterPetUpdateView, ShelterPetsListView, no_associated_shelter

urlpatterns = [
    path('', ShelterPetsListView.as_view(), name="management_pets_list"),
    path('pets/<int:pk>/', ShelterPetUpdateView.as_view(), name="management_pet_update"),
    path('no-shelter/', no_associated_shelter, name="no_associated_shelter"),
]
