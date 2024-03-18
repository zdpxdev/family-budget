import factory
from django.contrib.auth.models import User

from .models import TRANSACTION_TYPE_CHOICES, Budget, Category, Transaction


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    username = factory.Sequence(lambda n: f"username{n}")
    email = factory.LazyAttribute(lambda obj: f"{obj.username}@example.com")
    _password = factory.PostGenerationMethodCall("set_password", "password")


class CategoryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Category

    name = factory.Sequence(lambda n: f"Category {n}")


class BudgetFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Budget

    name = factory.Sequence(lambda n: f"Budget {n}")
    user = factory.SubFactory(UserFactory)


class TransactionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Transaction

    name = factory.Sequence(lambda n: f"Transaction {n}")
    value = factory.Faker("pydecimal", left_digits=3, right_digits=2, positive=True)
    currency = "PLN"
    category = factory.SubFactory(CategoryFactory)
    budget = factory.SubFactory(BudgetFactory)
    type = factory.Iterator([choice[0] for choice in TRANSACTION_TYPE_CHOICES])
