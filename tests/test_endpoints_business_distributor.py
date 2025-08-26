import pytest
from django.contrib.auth.models import User

@pytest.mark.django_db
def test_business_profile_me(client):
    u = User.objects.create_user(username="biz", password="secret12345")
    # Login and call business me
    resp = client.post("/api/accounts/jwt/login/", {"username": "biz", "password": "secret12345"}, content_type="application/json")
    assert resp.status_code == 200
    access = resp.json()["access"]
    resp = client.get("/api/business/me/", HTTP_AUTHORIZATION=f"Bearer {access}")
    assert resp.status_code in (200, 403)

@pytest.mark.django_db
def test_distributor_profile_me(client):
    u = User.objects.create_user(username="dist", password="secret12345")
    resp = client.post("/api/accounts/jwt/login/", {"username": "dist", "password": "secret12345"}, content_type="application/json")
    assert resp.status_code == 200
    access = resp.json()["access"]
    resp = client.get("/api/distributors/me/", HTTP_AUTHORIZATION=f"Bearer {access}")
    assert resp.status_code in (200, 403)


