from django.conf import settings
from django.db import models
from model_utils.models import TimeStampedModel

from .enums import TransactionType

TRANSACTION_TYPE_CHOICES = [(e.value, e.value) for e in TransactionType]


class Category(TimeStampedModel):
    name = models.CharField(max_length=50, unique=True)

    def save(self, *args, **kwargs):
        self.name = self.name.lower()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Budget(TimeStampedModel):
    name = models.CharField(max_length=30)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    shared_with = models.ManyToManyField(
        settings.AUTH_USER_MODEL, related_name="shared_budgets"
    )

    def __str__(self):
        return self.name


class Transaction(TimeStampedModel):
    name = models.CharField(max_length=30)
    value = models.DecimalField(max_digits=7, decimal_places=2)
    currency = models.CharField(max_length=3, null=False, default="PLN")
    category = models.ForeignKey(
        Category, related_name="transactions", on_delete=models.SET_NULL, null=True
    )
    budget = models.ForeignKey(
        Budget, related_name="transactions", on_delete=models.CASCADE
    )
    type = models.CharField(choices=TRANSACTION_TYPE_CHOICES, max_length=10)

    def __str__(self):
        sign = "+" if self.type == TransactionType.income else "-"
        return f"{self.name}: {sign}{self.value} {self.currency}"
