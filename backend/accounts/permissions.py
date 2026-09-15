from rest_framework.permissions import BasePermission


class IsAdminRole(BasePermission):
    message = "Only users with the admin role can perform this action."

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.role == "admin"
        )


class IsAdminOrManagerRole(BasePermission):
    message = "Only admin or manager users can perform this action."

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.role in {"admin", "manager"}
        )