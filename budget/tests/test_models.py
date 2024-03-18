from decimal import Decimal

import pytest
from django.db.utils import IntegrityError

from ..enums import TransactionType
from ..fixtures import BudgetFactory, CategoryFactory, TransactionFactory, UserFactory
from ..models import Budget, Category, Transaction

pytestmark = pytest.mark.django_db


class TestCategory:
    def test_category_name_is_normalized(self):
        category = Category.objects.create(name="Foo")

        assert category.name == "foo"

    def test_category_name_is_unique(self):
        Category.objects.create(name="Foo")

        with pytest.raises(IntegrityError):
            Category.objects.create(name="Foo")


class TestBudget:
    def test_budget_can_be_created(self):
        user = UserFactory.create()
        Budget.objects.create(name="Holidays", user=user)

        assert Budget.objects.filter(name="Holidays", user=user).exists()

    def test_budget_cant_be_created_without_user(self):
        with pytest.raises(IntegrityError):
            Budget.objects.create(name="Holidays")

    def test_transactions_can_be_added_to_budget(self):
        budget = BudgetFactory.create()
        transactions_count = 5

        TransactionFactory.create_batch(size=transactions_count, budget=budget)
        budget.refresh_from_db()

        assert budget.transactions.count() == transactions_count


class TestTransaction:
    def test_transaction_can_be_created(self):
        budget = BudgetFactory.create()
        category = CategoryFactory.create()

        assert Transaction.objects.create(
            name="Test",
            value=Decimal("21.37"),
            category=category,
            budget=budget,
            type=TransactionType.income,
        )

    def test_transaction_exists_if_related_category_removed(self):
        category = CategoryFactory.create()

        transaction = TransactionFactory.create(category=category)
        category.delete()
        transaction.refresh_from_db()

        assert transaction
        assert transaction.category is None
