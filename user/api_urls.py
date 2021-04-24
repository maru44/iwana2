from django.urls import path
from . import api_views as views
from rest_framework_simplejwt import views as jwt_views

app_name = "user_api"
urlpatterns = [
    # path("login/", jwt_views.TokenObtainPairView.as_view()),
    path("login/", views.TokenObtainPair.as_view()),
    # path("refresh/", jwt_views.TokenRefreshView.as_view()),
    path("refresh/", views.refresh_get),
    path("refresh/token/", views.TokenRefresh.as_view()),  # @TODO
    path("logout/", views.delete_jwt),
    path("profile/<pk>/", views.ProfileDetailView.as_view()),
    path("", views.UserAPIView.as_view()),
    # change profile
    path("token/", views.UserInformationAPIView.as_view()),
    # user auth register
    path("register/", views.UserCreateAPIView.as_view()),
    # complete register
    path("register/<token>/", views.user_complete_api, name="complete"),
]
