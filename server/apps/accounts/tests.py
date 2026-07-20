import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse


@pytest.mark.django_db
def test_password_login(api_client):
    get_user_model().objects.create_user(username="admin", password="strong-pass-123")
    response = api_client.post(
        reverse("password-login"),
        {"username": "admin", "password": "strong-pass-123"},
        format="json",
    )
    assert response.status_code == 200
    assert response.data["access"]
