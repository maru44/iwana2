from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

app_name = "user"
urlpatterns = [
    path(
        "logout/",
        auth_views.LogoutView.as_view(template_name="user/logout.html"),
        name="logout",
    ),
    path(
        "login/",
        auth_views.LoginView.as_view(template_name="user/login.html"),
        name="login",
    ),
    path("register/", views.UserCreate.as_view(), name="register"),
    path("register/done/", views.UserCreateDone.as_view(), name="register_done"),
    path(
        "register/complete/<token>/",
        views.user_create_complete,
        name="register_complete",
    ),
    path("password/reset/", views.PasswordReset.as_view(), name="reset"),
    path("password/reset/done/", views.PasswordResetDone.as_view(), name="reset_done"),
    path(
        "password/reset/confirm/<str:uidb64>/<str:token>/",
        views.PasswordResetConfirm.as_view(),
        name="reset_confirm",
    ),
    path(
        "password/reset/complete/",
        views.PasswordResetComplete.as_view(),
        name="reset_complete",
    ),
    path("profile/", views.profile, name="profile"),
    # path('delete/<username>', views.delete, name='user_delete'),
    # path('delete/confirm/<username>', views.delete_conf, name='delete_conf'),
]