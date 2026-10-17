from rest_framework.permissions import BasePermission


class IsTicketParticipantOrStaff(BasePermission):
    message = "You do not have permission to access this ticket."

    def has_permission(self, request, view):
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        user = request.user

        if user.role in {"admin", "manager"}:
            return True

        if request.method == "DELETE":
            self.message = "Only admin or manager users can delete tickets."
            return False

        if user.role == "agent":
            return obj.assigned_to_id == user.id

        if user.role == "customer":
            return obj.created_by_id == user.id

        return False