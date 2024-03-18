from decimal import Decimal

import pytest
from django.urls import reverse
from rest_framework import status

from budget.fixtures import (
    BudgetFactory,
    CategoryFactory,
    TransactionFactory,
    UserFactory,
)

from ...enums import TransactionType
from ...models import Transaction

pytestmark = pytest.mark.django_db

TRANSACTION_LIST_URL = reverse("transaction-list")


def test_list_transactions_not_authenticated(api_client):
    response = api_client.get(TRANSACTION_LIST_URL)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_list_transactions_permissions(api_client):
    user_with_budget_transactions = UserFactory.create()
    user_without_budget_transactions = UserFactory.create()
    transactions_count = 10
    TransactionFactory.create_batch(size=10, budget__user=user_with_budget_transactions)

    api_client.force_login(user_without_budget_transactions)
    user_without_transactions = api_client.get(TRANSACTION_LIST_URL)

    api_client.force_login(user_with_budget_transactions)
    user_with_transactions = api_client.get(TRANSACTION_LIST_URL)

    assert user_without_transactions.status_code == status.HTTP_200_OK
    assert user_without_transactions.data["count"] == 0
    assert user_with_transactions.status_code == status.HTTP_200_OK
    assert user_with_transactions.data["count"] == transactions_count


def test_create_transaction(api_client):
    user = UserFactory.create()
    budget = BudgetFactory.create(user=user)
    category = CategoryFactory.create()
    api_client.force_login(user)

    data = {
        "budget": budget.id,
        "name": "dog food",
        "value": 200,
        "currency": "PLN",
        "type": TransactionType.expense.value,
        "category": category.id,
    }
    response = api_client.post(TRANSACTION_LIST_URL, data)
    assert response.status_code == status.HTTP_201_CREATED
    assert Transaction.objects.filter(budget=budget, name=data["name"]).exists()


def test_update_transaction(api_client):
    user = UserFactory.create()
    budget = BudgetFactory.create(user=user)
    transaction = TransactionFactory.create(budget=budget)
    api_client.force_login(user)

    data = {
        "name": "new name",
        "value": 666,
    }
    response = api_client.patch(
        reverse("transaction-detail", args=(transaction.id,)), data
    )
    transaction.refresh_from_db()
    assert response.status_code == status.HTTP_200_OK
    assert transaction.name == data["name"]
    assert transaction.value == Decimal(data["value"])


def test_update_transaction_no_permissions(api_client):
    user = UserFactory.create()
    user_without_permission = UserFactory.create()
    budget = BudgetFactory.create(user=user)
    transaction = TransactionFactory.create(budget=budget)
    api_client.force_login(user_without_permission)

    data = {
        "name": "new name",
    }
    response = api_client.patch(
        reverse("transaction-detail", args=(transaction.id,)), data
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND
    transaction.refresh_from_db()
    assert transaction.name != data["name"]


def test_transactions_from_shared_budgets_returned_to_user(api_client):
    budget_owner = UserFactory.create()
    budget_collaborator = UserFactory.create()
    budget = BudgetFactory(user=budget_owner)

    TransactionFactory.create_batch(size=10, budget=budget)
    api_client.force_login(budget_collaborator)
    response = api_client.get(TRANSACTION_LIST_URL)
    assert response.status_code == status.HTTP_200_OK
    assert response.data["count"] == 0

    budget.shared_with.add(budget_collaborator)
    response = api_client.get(TRANSACTION_LIST_URL)
    assert response.status_code == status.HTTP_200_OK
    assert response.data["count"] == 10


def test_transactions_value_filter(api_client):
    user = UserFactory.create()
    budget = BudgetFactory(user=user)
    TransactionFactory.create(value=100, budget=budget)
    TransactionFactory.create(value=300, budget=budget)
    api_client.force_login(user)

    response = api_client.get(TRANSACTION_LIST_URL, {"min_value": 300})
    assert response.status_code == status.HTTP_200_OK
    assert response.data["count"] == 1

    response = api_client.get(TRANSACTION_LIST_URL, {"max_value": 50})
    assert response.status_code == status.HTTP_200_OK
    assert response.data["count"] == 0


def test_transactions_budget_filter(api_client):
    user = UserFactory.create()
    api_client.force_login(user)

    budget_with_2_transactions = BudgetFactory(user=user)
    budget_with_4_transactions = BudgetFactory(user=user)
    TransactionFactory.create_batch(size=2, budget=budget_with_2_transactions)
    TransactionFactory.create_batch(size=4, budget=budget_with_4_transactions)

    response = api_client.get(
        TRANSACTION_LIST_URL, {"budget": budget_with_2_transactions.id}
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.data["count"] == 2

    response = api_client.get(
        TRANSACTION_LIST_URL, {"budget": budget_with_4_transactions.id}
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.data["count"] == 4

    response = api_client.get(
        TRANSACTION_LIST_URL,
        {"budget": f"{budget_with_2_transactions.id},{budget_with_4_transactions.id}"},
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.data["count"] == 6


def test_db_queries_constant(api_client, django_assert_max_num_queries):
    # Ensure there is no issue with N+1 queries
    user = UserFactory.create()
    TransactionFactory.create_batch(size=100, budget__user=user)

    api_client.force_login(user)

    with django_assert_max_num_queries(4):
        api_client.get(TRANSACTION_LIST_URL)
