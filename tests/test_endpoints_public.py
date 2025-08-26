import pytest

@pytest.mark.parametrize("path,statuses", [
    ("/api/health/", {200}),
    ("/api/readiness/", {200, 503}),
    ("/api/farmers/public/produce/", {200}),
    ("/api/docs/", {200}),
    ("/api/redoc/", {200}),
])
def test_public_endpoints(client, path, statuses):
    resp = client.get(path)
    assert resp.status_code in statuses


