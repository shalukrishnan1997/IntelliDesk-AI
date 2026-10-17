from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from .models import Category, Ticket
from .permissions import IsTicketParticipantOrStaff
from .serializers import CategorySerializer, TicketSerializer


def get_tickets_for_user(user):
    queryset = Ticket.objects.select_related(
        "created_by",
        "assigned_to",
        "category",
    )

    if user.role in {"admin", "manager"}:
        return queryset

    if user.role == "agent":
        return queryset.filter(assigned_to=user)

    if user.role == "customer":
        return queryset.filter(created_by=user)

    return queryset.none()


class CategoryListView(generics.ListAPIView):
    queryset = Category.objects.filter(is_active=True)
    serializer_class = CategorySerializer
    permission_classes = (IsAuthenticated,)


class TicketListCreateView(generics.ListCreateAPIView):
    serializer_class = TicketSerializer
    permission_classes = (IsTicketParticipantOrStaff,)

    def get_queryset(self):
        return get_tickets_for_user(self.request.user)

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class TicketDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = TicketSerializer
    permission_classes = (IsTicketParticipantOrStaff,)

    def get_queryset(self):
        return get_tickets_for_user(self.request.user)