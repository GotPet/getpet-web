from django.urls import path
from django.views.generic import RedirectView

from web.views import AllPetsListView, AllSheltersListView, IndexView, PetProfileView, ShelterPetsListView, \
    health_check, index

app_name = 'web'

urlpatterns = [
    path('', index, name="index"),
    path('demo/', IndexView.as_view(), name="demo"),
    path('gyvunai/', AllPetsListView.as_view(), name="all_pets"),
    path('gyvunai/<int:pk>-<slug:slug>/', PetProfileView.as_view(), name="pet_profile"),

    path('istaigos/', AllSheltersListView.as_view(), name="all_shelters"),
    path('istaigos/<slug:slug>/', ShelterPetsListView.as_view(), name="shelter_profile"),

    path('favicon.ico/', RedirectView.as_view(url='/static/favicon/favicon.ico', permanent=False)),
    path('health/', health_check, name="health_check"),
]
