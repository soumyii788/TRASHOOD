"""
Custom DRF permission classes shared across apps.
"""
from rest_framework.permissions import BasePermission


class IsCustomer(BasePermission):
    """Allows access only to users with the CUSTOMER role."""
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated
                    and request.user.role == 'CUSTOMER')


class IsCollector(BasePermission):
    """Allows access only to users with the COLLECTOR role."""
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated
                    and request.user.role == 'COLLECTOR')


class IsAdmin(BasePermission):
    """Allows access only to users with the ADMIN role."""
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated
                    and request.user.role == 'ADMIN')
