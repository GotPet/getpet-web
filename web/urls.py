from django.http import HttpResponse
from django.urls import path

from web import views

app_name = 'web'

urlpatterns = [
    path('', views.IndexView.as_view(), name="index"),

    path('sunys/', views.AllDogsListView.as_view(), name="all_dogs"),
    path('sunys/<int:pk>-<slug:slug>/', views.DogProfileView.as_view(), name="dog_profile"),

    path('globos-organizacijos/', views.AllSheltersListView.as_view(), name="all_shelters"),
    path('globos-organizacijos/<slug:slug>/', views.ShelterPetsListView.as_view(), name="shelter_profile"),

    path('mentoriai/', views.MentorListView.as_view(), name="mentors"),

    # Documents
    path('privatumo-politika/', views.PrivacyPolicyDocumentView.as_view(), name="document_privacy_policy"),
    path('saziningo-naudojimosi-taisykles/', views.FairUseRulesDocumentView.as_view(), name="document_fair_use_rules"),
    path('kas-yra-getpet/', views.AboutGetPetDocumentView.as_view(), name="document_about_getpet"),

    path(
        'robots.txt/',
        lambda x: HttpResponse(
            "User-Agent: *\nDisallow: /accounts/\nDisallow: /api/\nDisallow: /admin/\nDisallow: "
            "/administration/\nSitemap: https://www.getpet.lt/sitemap.xml/",
            content_type="text/plain"
        ),
        name="robots_file"
    ),

    # Health check
    path('health/', views.health_check, name="health_check"),
]
