from typing import Generator, Optional
from rest_framework import generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.request import Request
from django.http import StreamingHttpResponse, HttpResponse
from django.utils import timezone
import time
import json
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from rest_framework_simplejwt.tokens import AccessToken

from .models import Notification
from .serializers import NotificationSerializer


class NotificationListView(generics.ListAPIView):
    """List notifications for the authenticated user, newest first."""
    serializer_class = NotificationSerializer

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user).order_by("-created_at")


class NotificationReadUpdateView(generics.UpdateAPIView):
    """Mark a notification as read/unread for the owner only."""
    serializer_class = NotificationSerializer

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user)


def _sse_event(data: str) -> bytes:
    """Format a payload as an SSE 'data' event."""
    return f"data: {data}\n\n".encode("utf-8")


def _stream_notifications(user: User, last_seen_id: int = 0, timeout_seconds: int = 30) -> Generator[bytes, None, None]:
    """Yield SSE events for new notifications for a limited time window.

    This is a simple polling loop suitable for development. For production,
    consider pushing from signals into a queue and streaming promptly.
    """
    start = time.time()
    while time.time() - start < timeout_seconds:
        qs = Notification.objects.filter(user=user, id__gt=last_seen_id).order_by("id")
        for n in qs:
            payload = json.dumps(NotificationSerializer(n).data)
            yield _sse_event(payload)
            last_seen_id = n.id
        time.sleep(1)


@api_view(["GET"])
@permission_classes([permissions.AllowAny])
def sse_notifications(request: Request) -> HttpResponse:
    """Server-Sent Events stream of notifications.

    Auth priority:
    1. Existing session/header auth
    2. JWT via `?access=` query
    3. DRF token via `?token=` query
    """
    user = getattr(request, "user", None)

    # If not authenticated, allow token in query for SSE convenience
    if not (user and user.is_authenticated):
        access = request.GET.get("access")  # JWT access token
        api_token = request.GET.get("token")  # DRF token
        if access:
            try:
                token = AccessToken(access)
                user_id = token.get("user_id")
                user = User.objects.get(id=user_id)
            except Exception:
                return StreamingHttpResponse(_sse_event(json.dumps({"detail": "Invalid access token"})), status=401, content_type="text/event-stream")
        elif api_token:
            try:
                t = Token.objects.get(key=api_token)
                user = t.user
            except Token.DoesNotExist:
                return StreamingHttpResponse(_sse_event(json.dumps({"detail": "Invalid token"})), status=401, content_type="text/event-stream")
        else:
            return StreamingHttpResponse(_sse_event(json.dumps({"detail": "Authentication required"})), status=401, content_type="text/event-stream")

    last_id = int(request.GET.get("last_id", 0))
    response = StreamingHttpResponse(
        _stream_notifications(user, last_seen_id=last_id),
        content_type="text/event-stream",
    )
    response["Cache-Control"] = "no-cache"
    return response

# Create your views here.
