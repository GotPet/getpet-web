from django.http import HttpResponse
from django.urls import path
from django.contrib.sitemaps.views import sitemap as SitemapView

from web import sitemap, views

app_name = 'web'

urlpatterns = [
    path('', views.index, name="index"),
    path('demo/', views.IndexView.as_view(), name="demo"),
    path('sunys/', views.AllDogsListView.as_view(), name="all_dogs"),
    path('sunys/<int:pk>-<slug:slug>/', views.DogProfileView.as_view(), name="dog_profile"),

    path('globos-organizacijos/', views.AllSheltersListView.as_view(), name="all_shelters"),
    path('globos-organizacijos/<slug:slug>/', views.ShelterPetsListView.as_view(), name="shelter_profile"),

    # Documents
    path('privatumo-politika/', views.PrivacyPolicyDocumentView.as_view(), name="document_privacy_policy"),
    path('saziningo-naudojimosi-taisykles/', views.FairUseRulesDocumentView.as_view(), name="document_fair_use_rules"),
    path('apie-getpet/', views.AboutGetPetDocumentView.as_view(), name="document_about_getpet"),

    # Sitemaps
    path(
        'sitemap.xml/',
        SitemapView,
        {
            'sitemaps': {
                'static': sitemap.StaticSitemap,
                'pets': sitemap.PetSitemap,
                'shelter': sitemap.ShelterSitemap,
            }
        },
        name='django.contrib.sitemaps.views.sitemap'
    ),

    path(
        'robots.txt/',
        lambda x: HttpResponse(
            "User-Agent: *\nSitemap: https://www.getpet.lt/sitemap.xml/",
            content_type="text/plain"
        ),
        name="robots_file"
    ),

    # Health check
    path('health/', views.health_check, name="health_check"),
]
