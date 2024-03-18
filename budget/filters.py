import django_filters

from .models import Category


class CategoryFilter(django_filters.FilterSet):
    class Meta:
        model = Category
        fields = {"name": ["exact", "icontains"]}
