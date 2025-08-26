from django.urls import path

from .views import MyDistributorProfileView

urlpatterns = [
    path("me/", MyDistributorProfileView.as_view(), name="distributor-me"),
]





