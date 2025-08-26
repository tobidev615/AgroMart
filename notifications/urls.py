from django.urls import path

from .views import NotificationListView, NotificationReadUpdateView, sse_notifications

urlpatterns = [
    path("notifications/", NotificationListView.as_view(), name="notifications"),
    path("notifications/<int:pk>/", NotificationReadUpdateView.as_view(), name="notification-detail"),
    path("notifications/stream/", sse_notifications, name="notifications-stream"),
]

