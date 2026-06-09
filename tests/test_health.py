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
    data = res.json()
    assert data["status"] == "ready"
    assert "checks" in data
    assert data["checks"]["database"] == "ok"


@pytest.mark.django_db
def test_metrics_endpoint(client, settings):
    # Fuera de DEBUG el endpoint exige METRICS_TOKEN (cerrado por defecto).
    settings.METRICS_TOKEN = "test-metrics-token"
    res = client.get("/metrics", HTTP_AUTHORIZATION="Bearer test-metrics-token")
    assert res.status_code == 200
    assert b"django_http_requests_total" in res.content


@pytest.mark.django_db
def test_custom_user_model():
    User = get_user_model()
    user = User.objects.create_user(username="demo", email="demo@example.com", password="pass1234")
    assert user.email == "demo@example.com"
