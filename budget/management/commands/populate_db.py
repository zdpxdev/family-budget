from itertools import cycle

from django.core.management.base import BaseCommand
from django.db import IntegrityError

from budget.fixtures import (
    BudgetFactory,
    CategoryFactory,
    TransactionFactory,
    UserFactory,
)


class Command(BaseCommand):
    help = "Populates db with exemplary data"

    def handle(self, *args, **options):
        try:
            categories = cycle(CategoryFactory.create_batch(size=5))
            users = UserFactory.create_batch(size=10)
            for user in users:
                budgets = BudgetFactory.create_batch(size=5, user=user)
                for budget in budgets:
                    TransactionFactory.create_batch(
                        size=10, budget=budget, category=next(categories)
                    )
        except IntegrityError:
            print("Exemplary data already exists")
