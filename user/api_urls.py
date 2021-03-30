from django.urls import path, include
from . import api_views as views
from rest_framework_jwt import views as jwt_views

app_name = 'user_api'
urlpatterns = [
    path('login/', jwt_views.obtain_jwt_token),
]