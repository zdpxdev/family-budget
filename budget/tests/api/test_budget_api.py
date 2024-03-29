import pytest
from django.urls import reverse
from rest_framework import status

from budget.fixtures import BudgetFactory, TransactionFactory, UserFactory

from ...models import Budget

pytestmark = pytest.mark.django_db

BUDGET_LIST_URL = reverse("budget-list")


def test_list_budget_not_authenticated(api_client):
    response = api_client.get(BUDGET_LIST_URL)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_list_budget_permissions(api_client):
    user_without_budgets = UserFactory.create()
    user_with_budgets = UserFactory.create()
    budgets_count = 10
    BudgetFactory.create_batch(size=budgets_count, user=user_with_budgets)

    api_client.force_login(user_without_budgets)
    user_without_budgets_response = api_client.get(BUDGET_LIST_URL)

    api_client.force_login(user_with_budgets)
    user_with_budgets_response = api_client.get(BUDGET_LIST_URL)

    assert user_without_budgets_response.status_code == status.HTTP_200_OK
    assert user_without_budgets_response.data["count"] == 0
    assert user_with_budgets_response.status_code == status.HTTP_200_OK
    assert user_with_budgets_response.data["count"] == budgets_count


def test_create_budget(api_client):
    user = UserFactory.create()
    api_client.force_login(user)
    data = {"name": "My budget"}

    response = api_client.post(BUDGET_LIST_URL, data)

    assert response.status_code == status.HTTP_201_CREATED
    assert Budget.objects.filter(user=user, name=data["name"]).exists()


def test_update_budget(api_client):
    user = UserFactory.create()
    budget = BudgetFactory.create(user=user, name="Old name")
    api_client.force_login(user)
    url = reverse("budget-detail", args=(budget.id,))
    data = {"name": "New name"}

    response = api_client.patch(url, data)

    budget.refresh_from_db()
    assert response.status_code == status.HTTP_200_OK
    assert budget.name == data["name"]


def test_update_budget_no_permissions(api_client):
    user = UserFactory.create()
    budget = BudgetFactory.create(user=user, name="Old name")
    user_without_permission = UserFactory.create()

    api_client.force_login(user_without_permission)
    url = reverse("budget-detail", args=(budget.id,))
    response = api_client.patch(url, {"name": "New name"})

    budget.refresh_from_db()
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert budget.name == "Old name"


def test_share_budget(api_client):
    budget_owner = UserFactory.create()
    budget = BudgetFactory(user=budget_owner)
    budget_collaborator = UserFactory.create()

    # Budget not shared yet, not visible.
    api_client.force_authenticate(budget_collaborator)
    response = api_client.get(reverse("budget-detail", args=(budget.id,)))
    assert response.status_code == status.HTTP_404_NOT_FOUND

    # Budget owner shares it with budget_collaborator
    api_client.force_authenticate(budget_owner)
    response = api_client.post(
        reverse("budget-share", args=(budget.id,)),
        {"emails": [budget_collaborator.email]},
        format="json",
    )
    assert response.status_code == status.HTTP_200_OK

    # budget_collaborator has an access to budget
    api_client.force_authenticate(budget_collaborator)
    response = api_client.get(reverse("budget-detail", args=(budget.id,)))
    assert response.status_code == status.HTTP_200_OK


def test_db_queries_constant(api_client, django_assert_max_num_queries):
    # Ensure there is no issue with N+1 queries
    user = UserFactory.create()

    TransactionFactory.create_batch(size=100, budget__user=user)
    api_client.force_login(user)

    with django_assert_max_num_queries(5):
        api_client.get(BUDGET_LIST_URL)
