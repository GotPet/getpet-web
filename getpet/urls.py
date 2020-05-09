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
from django.urls import path, include

from getpet import settings

urlpatterns = [
                  path('admin/', admin.site.urls),

                  path('api/', include('api.urls')),
                  path('administravimas/', include('management.urls'), ),
                  path('accounts/', include('allauth.urls')),

                  path('', include('web.urls')),
              ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG and settings.ENABLE_DEBUG_DRAWER_IN_DEBUG:
    import debug_toolbar

    urlpatterns = [
                      path('__debug__/', include(debug_toolbar.urls)),
                  ] + urlpatterns

handler400 = 'management.views.handler400'
handler403 = 'management.views.handler403'
handler404 = 'management.views.handler404'
handler500 = 'management.views.handler500'
