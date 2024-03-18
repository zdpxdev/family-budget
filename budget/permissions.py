from rest_framework import permissions


class HasBudgetAccess(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if not request.user.is_authenticated:
            return False
        if request.user == obj.user:
            return True
        if obj.shared_with.filter(id=request.user.id).exists():
            return True
        return False


class HasTransactionAccess(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if not request.user.is_authenticated:
            return False
        if request.user == obj.budget.user:
            return True
        if obj.budget.shared_with.filter(id=request.user.id).exists():
            return True
        return False
