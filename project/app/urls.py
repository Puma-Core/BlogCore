"""
URL configuration for the app Django project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.1/topics/http/urls/
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
from typing import cast

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

from app.router import router

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
]

if settings.ENVIRONMENT != 'production':
    # Browsable API and OpenAPI schema are development-only tooling.
    # drf-spectacular is a dev dependency, so import it lazily here.
    from drf_spectacular.views import SpectacularAPIView

    urlpatterns += [
        path('api/auth/', include('rest_framework.urls')),
        path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    ]

    urlpatterns += cast(list, static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT))
