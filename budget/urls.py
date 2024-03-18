from rest_framework.routers import DefaultRouter

from . import views

urlpatterns = []
router = DefaultRouter()

router.register(r"budgets", views.BudgetViewSet, basename="budget")
router.register(r"categories", views.CategoryViewSet, basename="category")
router.register(r"transactions", views.TransactionViewSet, basename="transaction")

urlpatterns += router.urls
