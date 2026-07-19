import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework_simplejwt.tokens import RefreshToken

from .models import LoginEvent, User


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


@pytest.mark.django_db
def test_register_returns_tokens_and_allows_profile_update(api_client):
    response = api_client.post(
        reverse("password-register"),
        {
            "username": "home-cook",
            "nickname": "家庭主厨",
            "password": "strong-pass-123",
            "password_confirm": "strong-pass-123",
        },
        format="json",
    )

    assert response.status_code == 201
    assert response.data["access"]
    assert response.data["user"]["nickname"] == "家庭主厨"
    assert LoginEvent.objects.filter(method="password_register", succeeded=True).exists()

    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {response.data['access']}")
    profile = api_client.patch(
        reverse("users-me"),
        {"nickname": "今天我掌勺", "username": "cannot-change"},
        format="json",
    )

    assert profile.status_code == 200
    assert profile.data["nickname"] == "今天我掌勺"
    assert profile.data["username"] == "home-cook"


@pytest.mark.django_db
def test_locked_user_cannot_login(api_client):
    User.objects.create_user(
        username="locked-cook",
        password="strong-pass-123",
        status=User.Status.LOCKED,
    )

    response = api_client.post(
        reverse("password-login"),
        {"username": "locked-cook", "password": "strong-pass-123"},
        format="json",
    )

    assert response.status_code == 400


@pytest.mark.django_db
def test_locked_user_cannot_refresh_token(api_client):
    user = User.objects.create_user(
        username="refresh-locked-cook",
        password="strong-pass-123",
    )
    refresh = str(RefreshToken.for_user(user))
    user.status = User.Status.LOCKED
    user.save(update_fields=["status"])

    response = api_client.post(
        reverse("token-refresh"),
        {"refresh": refresh},
        format="json",
    )

    assert response.status_code == 401
