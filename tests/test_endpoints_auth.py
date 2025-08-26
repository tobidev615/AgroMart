import pytest
from django.contrib.auth.models import User

@pytest.mark.django_db
def test_requires_auth_for_cart(client):
    resp = client.get("/api/cart/")
    assert resp.status_code in (401, 403)

@pytest.mark.django_db
def test_login_and_me(client):
    user = User.objects.create_user(username="bob", password="secret12345")
    # JWT login
    resp = client.post("/api/accounts/jwt/login/", {"username": "bob", "password": "secret12345"}, content_type="application/json")
    assert resp.status_code == 200
    access = resp.json()["access"]
    resp = client.get("/api/accounts/me/", HTTP_AUTHORIZATION=f"Bearer {access}")
    assert resp.status_code == 200


