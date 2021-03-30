from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('blog.urls')),
    path('user/', include('user.urls', namespace='user')),
    path('auth/', include('social_django.urls', namespace='auth')),
    path('api/user/', include('user.api_urls', namespace='user_api')),
    path('api/', include('blog.api_urls', namespace='api')),
]

import os
if os.environ.get("ENVIRONMENT") is not "local":
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)