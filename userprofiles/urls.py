from django.urls import path
from rest_framework.authtoken.views import obtain_auth_token
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from .views import register, me, verify_email, password_reset_request, password_reset_confirm

urlpatterns = [
    path("register/", register, name="register"),
    path("login/", obtain_auth_token, name="login"),
    path("jwt/login/", TokenObtainPairView.as_view(), name="jwt-login"),
    path("jwt/refresh/", TokenRefreshView.as_view(), name="jwt-refresh"),
    path("me/", me, name="me"),
    path("verify-email/", verify_email, name="verify-email"),
    path("password-reset-request/", password_reset_request, name="password-reset-request"),
    path("password-reset-confirm/", password_reset_confirm, name="password-reset-confirm"),
]


