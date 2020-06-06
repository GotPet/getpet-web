from django.urls import path
from django.views.generic import RedirectView

from web.views import AllPetsListView, IndexView, PetProfileView, health_check, index

app_name = 'web'

urlpatterns = [
    path('', index, name="index"),
    path('demo/', IndexView.as_view(), name="demo"),
    path('pet/<int:pk>/', PetProfileView.as_view(), name="pet_profile"),
    path('pets/', AllPetsListView.as_view(), name="all_pets"),
    path('favicon.ico/', RedirectView.as_view(url='/static/favicon/favicon.ico', permanent=False)),
    path('health/', health_check, name="health_check"),
]
