import pytest
from django.urls import reverse
from rest_framework import status

from ...fixtures import CategoryFactory

pytestmark = pytest.mark.django_db


def test_can_create_category(api_client):
    url = reverse("category-list")
    data = {"name": "foo"}
    response = api_client.post(url, data)
    assert response.status_code == status.HTTP_201_CREATED
    assert response.data["name"] == data["name"].lower()


def test_cant_create_category_with_already_existing_name(api_client):
    category_name = "foo"
    CategoryFactory.create(name=category_name)
    url = reverse("category-list")
    data = {"name": category_name}
    response = api_client.post(url, data)
    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_get_category_by_id(api_client):
    category = CategoryFactory.create()
    url = reverse("category-detail", args=(category.id,))

    response = api_client.get(url)

    assert response.status_code == 200


def test_get_category_list(api_client):
    page_size = 10
    categories_count = 100
    CategoryFactory.create_batch(categories_count)
    url = reverse("category-list")
    response = api_client.get(url, {"limit": page_size})

    assert response.status_code == status.HTTP_200_OK
    assert response.data["count"] == categories_count
    assert len(response.data["results"]) == page_size


def test_get_category_list_filters(api_client):
    CategoryFactory.create(name="food")
    CategoryFactory.create(name="shopping")
    CategoryFactory.create(name="car fuel")
    CategoryFactory.create(name="car mechanic")
    url = reverse("category-list")

    car_response = api_client.get(url, {"name__icontains": "car"})
    food_response = api_client.get(url, {"name": "food"})

    assert car_response.status_code == status.HTTP_200_OK
    assert car_response.data["count"] == 2
    assert food_response.status_code == status.HTTP_200_OK
    assert food_response.data["count"] == 1
