from django.urls import path

from management.views import ShelterInfoUpdateView, ShelterPetUpdateView, ShelterPetsListView, no_associated_shelter

urlpatterns = [
    path('', ShelterPetsListView.as_view(), name="management_pets_list"),
    path('pets/<int:pk>/', ShelterPetUpdateView.as_view(), name="management_pet_update"),
    path('shelter/<int:pk>/', ShelterInfoUpdateView.as_view(), name="management_shelter_info_update"),
    path('no-shelter/', no_associated_shelter, name="no_associated_shelter"),
]
