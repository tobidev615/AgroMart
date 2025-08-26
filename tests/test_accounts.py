import pytest
from django.urls import reverse

@pytest.mark.django_db
def test_register_creates_user(client):
    data = {
        'username': 'alice',
        'email': 'alice@example.com',
        'password': 'passw0rd123',
        'first_name': 'Alice',
        'last_name': 'Smith',
        'role': 'CONSUMER',
    }
    resp = client.post(reverse('register'), data, content_type='application/json')
    assert resp.status_code == 201
    body = resp.json()
    assert 'token' in body
    assert body['user']['username'] == 'alice'


