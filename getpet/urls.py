"""getpet URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

from getpet import settings
from utils.utils import sitemap_with_images
from web import sitemap

urlpatterns = [
                  path('administration/', admin.site.urls),

                  path('api/', include('api.urls')),
                  path('admin/', include('management.urls', namespace='management')),
                  path('accounts/', include('allauth.urls')),

                  path('', include('web.urls', namespace='web')),

                  # Sitemaps
                  path(
                      'sitemap.xml/',
                      sitemap_with_images,
                      {
                          'sitemaps': {
                              'static': sitemap.StaticSitemap,
                              'shelter': sitemap.ShelterSitemap,
                              'dogs': sitemap.DogSitemap,
                              'cats': sitemap.CatSitemap,
                          }
                      },
                      name='django.contrib.sitemaps.views.index'
                  ),
              ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG and settings.ENABLE_DEBUG_DRAWER_IN_DEBUG:
    import debug_toolbar

    urlpatterns = [
                      path('__debug__/', include(debug_toolbar.urls)),
                  ] + urlpatterns

handler400 = 'web.views.handler400'
handler403 = 'web.views.handler403'
handler404 = 'web.views.handler404'
handler500 = 'web.views.handler500'
