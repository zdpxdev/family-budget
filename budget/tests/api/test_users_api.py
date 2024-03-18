import pytest
from django.urls import reverse
from rest_framework import status

pytestmark = pytest.mark.django_db


def test_can_create_user_and_fetch_token(api_client):
    user_data = {
        "username": "testuser",
        "email": "testuser@example.com",
        "password": "test",
    }
    register_url = reverse("register")
    response = api_client.post(register_url, user_data)
    assert response.status_code == status.HTTP_201_CREATED

    token_url = reverse("token")
    response = api_client.post(
        token_url,
        {
            "username": user_data["username"],
            "password": user_data["password"],
        },
    )
    assert response.status_code == status.HTTP_200_OK
    assert "token" in response.data
