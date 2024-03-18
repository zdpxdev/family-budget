import django_filters

from .models import Category, Transaction


class NumberInFilter(django_filters.BaseInFilter, django_filters.NumberFilter):
    pass


class CategoryFilter(django_filters.FilterSet):
    class Meta:
        model = Category
        fields = {"name": ["exact", "icontains"]}


class TransactionFilter(django_filters.FilterSet):
    min_value = django_filters.NumberFilter(field_name="value", lookup_expr="gte")
    max_value = django_filters.NumberFilter(field_name="value", lookup_expr="lte")

    budget = NumberInFilter(field_name="budget_id", lookup_expr="in")

    class Meta:
        model = Transaction
        fields = ["value", "budget"]
