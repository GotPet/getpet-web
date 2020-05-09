from django.urls import path

from management.views import ShelterInfoUpdateView, ShelterPetCreateView, ShelterPetUpdateView, ShelterPetsListView, \
    SheltersListView, no_associated_shelter

urlpatterns = [
    path('', ShelterPetsListView.as_view(), name="management_pets_list"),
    path('pets/<int:pk>/', ShelterPetUpdateView.as_view(), name="management_pet_update"),
    path('pets/create/', ShelterPetCreateView.as_view(), name="management_pet_create"),
    path('shelters/', SheltersListView.as_view(), name="management_shelters_list"),
    path('shelters/<int:pk>/', ShelterInfoUpdateView.as_view(), name="management_shelter_info_update"),
    path('no-shelter/', no_associated_shelter, name="no_associated_shelter"),
]
