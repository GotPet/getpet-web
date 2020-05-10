from django.urls import path

from management import views

urlpatterns = [
    path('', views.IndexView.as_view(), name="management_index"),
    path('pets/', views.ShelterPetsListView.as_view(), name="management_pets_list"),
    path('pets/<int:pk>/', views.ShelterPetUpdateView.as_view(), name="management_pet_update"),
    path('pets/create/', views.ShelterPetCreateView.as_view(), name="management_pet_create"),
    path('shelters/', views.SheltersListView.as_view(), name="management_shelters_list"),
    path('shelters/<int:pk>/', views.ShelterInfoUpdateView.as_view(), name="management_shelter_info_update"),
    path('shelters/<int:pk>/switch/', views.ShelterSwitchView.as_view(), name="management_shelters_switch"),
    path('no-shelter/', views.no_associated_shelter, name="no_associated_shelter"),
]
