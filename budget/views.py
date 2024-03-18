from django.contrib.auth.models import User
from django.db.models import Q
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .filters import CategoryFilter, TransactionFilter
from .models import Budget, Category, Transaction
from .permissions import HasBudgetAccess, HasTransactionAccess
from .serializers import (
    BudgetSerializer,
    CategorySerializer,
    ShareWithSerializer,
    TransactionSerializer,
)


class BudgetViewSet(viewsets.ModelViewSet):
    queryset = Budget.objects.all()
    serializer_class = BudgetSerializer
    permission_classes = [IsAuthenticated & HasBudgetAccess]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return Budget.objects.none()
        return (
            Budget.objects.filter(
                Q(user=self.request.user) | Q(shared_with__in=[self.request.user])
            )
            .prefetch_related("transactions")
            .distinct()
        )

    @action(detail=True, methods=["post"])
    def share(self, request, pk):
        serializer = ShareWithSerializer(data=request.data)
        if serializer.is_valid():
            users = User.objects.filter(
                email__in=serializer.validated_data.get("emails", [])
            )
            if users.exists():
                obj = get_object_or_404(Budget, id=pk)
                obj.shared_with.add(*users)
                return Response({"status": "success"})
            else:
                return Response({"status": "no matching users found"})
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CategoryViewSet(
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    filterset_class = CategoryFilter


class TransactionViewSet(viewsets.ModelViewSet):
    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated & HasTransactionAccess]
    filterset_class = TransactionFilter

    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return Budget.objects.none()
        return Transaction.objects.filter(
            Q(budget__user=self.request.user)
            | Q(budget__shared_with__in=[self.request.user])
        ).distinct()
