from django.contrib.auth import get_user_model
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

    transactions = serializers.SerializerMethodField()

    def get_transactions(self, obj):
        return TransactionSerializer(obj.transactions.all(), many=True).data


class CategorySerializer(ModelSerializer):
    class Meta:
        model = Category
        fields = ("id", "name")


class TransactionSerializer(ModelSerializer):
    class Meta:
        model = Transaction
        fields = ("id", "name", "value", "currency", "type", "category", "budget")


class ShareWithSerializer(Serializer):
    emails = ListSerializer(child=EmailField(), required=True)


User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    email = serializers.EmailField(required=True)

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data["username"],
            password=validated_data["password"],
            email=validated_data["email"],
        )

        return user

    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "email",
            "password",
        )
