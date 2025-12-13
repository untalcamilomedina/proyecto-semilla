import pytest
from django.contrib.auth import get_user_model


@pytest.mark.django_db
def test_healthz(client):
    res = client.get("/healthz")
    assert res.status_code == 200
    assert res.json() == {"status": "ok"}


@pytest.mark.django_db
def test_readyz(client):
    res = client.get("/readyz")
    assert res.status_code == 200
    assert res.json() == {"status": "ready"}


@pytest.mark.django_db
def test_metrics_endpoint(client):
    res = client.get("/metrics")
    assert res.status_code == 200
    assert b"django_http_requests_total" in res.content


@pytest.mark.django_db
def test_custom_user_model():
    User = get_user_model()
    user = User.objects.create_user(username="demo", email="demo@example.com", password="pass1234")
    assert user.email == "demo@example.com"
