import pytest
from django.urls import reverse

@pytest.mark.django_db
def test_health(client):
    resp = client.get(reverse('health'))
    assert resp.status_code == 200
    assert resp.json().get('status') == 'ok'


