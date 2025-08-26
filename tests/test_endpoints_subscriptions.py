import pytest

@pytest.mark.django_db
def test_list_plans(client):
    resp = client.get("/api/plans/")
    assert resp.status_code == 200


