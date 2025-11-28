from rest_framework.permissions import BasePermission


class AllowAnyUser(BasePermission):
    """
    Permission allowing any user to access a view.
    """

    def has_permission(self, request, view) -> bool:
        return True
