from typing import Never

from rest_framework import serializers
from rest_framework.serializers import (
    EmailField,
    ListSerializer,
    ModelSerializer,
    Serializer,
)

from .models import Budget, Category, Transaction


class BudgetSerializer(ModelSerializer):
    class Meta:
        model = Budget
        fields = ("id", "name", "transactions")

    entries = serializers.SerializerMethodField()

    def get_transactions(self, obj):
        return TransactionSerializer(obj.entries.all(), many=True).data


class CategorySerializer(ModelSerializer):
    class Meta:
        model = Category
        fields = ("id", "name")


class TransactionSerializer(ModelSerializer):
    class Meta:
        model = Transaction
        fields = ("id", "name", "value", "currency", "type", "category", "budget")


class ShareWithSerializer(Serializer):
    emails: ListSerializer[Never] = ListSerializer(child=EmailField(), required=True)
