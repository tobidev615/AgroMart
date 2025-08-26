from django.urls import path
from .views import health, readiness_probe

urlpatterns = [
    path("health/", health, name="health"),
    path("readiness/", readiness_probe, name="readiness"),
]


