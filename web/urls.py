from django.urls import path
from django.views.generic import RedirectView

from web.views import PetProfileView, health_check, index

urlpatterns = [
    path('', index, name="index"),
    path('pet/<int:pk>/', PetProfileView.as_view(), name="pet_profile"),
    path('favicon.ico/', RedirectView.as_view(url='/static/favicon/favicon.ico', permanent=False)),
    path('health/', health_check, name="health_check"),
]
