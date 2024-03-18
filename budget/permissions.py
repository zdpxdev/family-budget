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
