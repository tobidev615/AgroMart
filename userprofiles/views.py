from rest_framework import permissions, status
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.models import User
from notifications.utils import notify_user

from .serializers import (
    RegistrationSerializer,
    UserProfileSerializer,
    UserSerializer,
)


@api_view(["POST"])
@permission_classes([permissions.AllowAny])
def register(request):
    serializer = RegistrationSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user = serializer.save()
    token, _ = Token.objects.get_or_create(user=user)
    user_data = UserSerializer(user).data
    profile_data = UserProfileSerializer(user.profile).data
    profile_data.pop("user", None)
    # email verification link
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    vtoken = default_token_generator.make_token(user)
    verification_link = f"/api/accounts/verify-email/?uid={uid}&token={vtoken}"
    notify_user(user, title="Verify your email", message=f"Click to verify: {verification_link}")
    return Response({
        "token": token.key,
        "user": user_data,
        "profile": profile_data,
    }, status=status.HTTP_201_CREATED)


@api_view(["GET", "PATCH"])
def me(request):
    if request.method == "GET":
        serializer = UserProfileSerializer(request.user.profile)
        return Response(serializer.data)

    serializer = UserProfileSerializer(
        request.user.profile, data=request.data, partial=True
    )
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(serializer.data)

@api_view(["GET"]) 
@permission_classes([permissions.AllowAny])
def verify_email(request):
    uidb64 = request.GET.get("uid")
    token = request.GET.get("token")
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uid)
    except Exception:
        return Response({"detail": "Invalid link."}, status=status.HTTP_400_BAD_REQUEST)
    if default_token_generator.check_token(user, token):
        if hasattr(user, "profile"):
            user.profile.email_verified = True
            user.profile.save(update_fields=["email_verified"])
        return Response({"detail": "Email verified."})
    return Response({"detail": "Invalid or expired token."}, status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"]) 
@permission_classes([permissions.AllowAny])
def password_reset_request(request):
    email = request.data.get("email")
    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        return Response({"detail": "If the email exists, a reset link will be sent."})
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    rtoken = default_token_generator.make_token(user)
    reset_link = f"/api/accounts/password-reset-confirm/?uid={uid}&token={rtoken}"
    notify_user(user, title="Password reset", message=f"Reset your password: {reset_link}")
    return Response({"detail": "If the email exists, a reset link will be sent."})


@api_view(["POST"]) 
@permission_classes([permissions.AllowAny])
def password_reset_confirm(request):
    uidb64 = request.data.get("uid")
    token = request.data.get("token")
    new_password = request.data.get("new_password")
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uid)
    except Exception:
        return Response({"detail": "Invalid link."}, status=status.HTTP_400_BAD_REQUEST)
    if not default_token_generator.check_token(user, token):
        return Response({"detail": "Invalid or expired token."}, status=status.HTTP_400_BAD_REQUEST)
    if not new_password or len(new_password) < 8:
        return Response({"new_password": ["Password must be at least 8 characters."]}, status=status.HTTP_400_BAD_REQUEST)
    user.set_password(new_password)
    user.save()
    return Response({"detail": "Password updated."})
