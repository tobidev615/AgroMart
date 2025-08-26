import pytest
from django.urls import reverse

@pytest.mark.django_db
@pytest.mark.parametrize("path", ["/api/health/", "/api/readiness/"])
def test_basic_endpoints_ok(client, path):
    resp = client.get(path)
    assert resp.status_code in (200, 503)


