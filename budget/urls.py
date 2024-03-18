from django.urls import path
from rest_framework.authtoken.views import obtain_auth_token
from rest_framework.routers import DefaultRouter

from . import views

urlpatterns = [
    path("users/register/", views.RegisterUserView.as_view(), name="register"),
    path("users/auth-token/", obtain_auth_token, name="token"),
]
router = DefaultRouter()

router.register(r"budgets", views.BudgetViewSet, basename="budget")
router.register(r"categories", views.CategoryViewSet, basename="category")
router.register(r"transactions", views.TransactionViewSet, basename="transaction")

urlpatterns += router.urls
