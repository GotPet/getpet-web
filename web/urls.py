from django.urls import path
from django.views.generic import RedirectView

from web import views

app_name = 'web'

urlpatterns = [
    path('', views.index, name="index"),
    path('demo/', views.IndexView.as_view(), name="demo"),
    path('sunys/', views.AllDogsListView.as_view(), name="all_dogs"),
    path('sunys/<int:pk>-<slug:slug>/', views.DogProfileView.as_view(), name="dog_profile"),

    path('istaigos/', views.AllSheltersListView.as_view(), name="all_shelters"),
    path('istaigos/<slug:slug>/', views.ShelterPetsListView.as_view(), name="shelter_profile"),

    path('favicon.ico/', RedirectView.as_view(url='/static/favicon/favicon.ico', permanent=False)),

    # Documents
    path('privatumo-politika/', views.privacy_policy, name="privacy_policy"),
    path('saziningo-naudojimosi-taisykles/', views.fair_use_rules, name="fair_use_rules"),
    path('apie-getpet/', views.about_getpet, name="about_getpet"),

    # Health check
    path('health/', views.health_check, name="health_check"),
]
