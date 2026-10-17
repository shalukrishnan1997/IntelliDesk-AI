from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIRequestFactory

from tickets.models import Category, Ticket
from tickets.serializers import (
    CategorySerializer,
    TicketSerializer,
)


User = get_user_model()


class CategorySerializerTests(TestCase):
    def test_category_serializer_creates_category(self):
        serializer = CategorySerializer(
            data={
                "name": "Technical Support",
                "description": "Technical support tickets",
            }
        )

        self.assertTrue(serializer.is_valid(), serializer.errors)

        category = serializer.save()

        self.assertEqual(category.name, "Technical Support")
        self.assertEqual(
            category.description,
            "Technical support tickets",
        )
        self.assertTrue(category.is_active)

    def test_category_serializer_rejects_duplicate_name(self):
        Category.objects.create(
            name="Billing",
            description="Billing-related tickets",
        )

        serializer = CategorySerializer(
            data={
                "name": "Billing",
                "description": "Duplicate category",
            }
        )

        self.assertFalse(serializer.is_valid())
        self.assertIn("name", serializer.errors)


class TicketSerializerTests(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()

        self.customer = User.objects.create_user(
            username="ticket_customer",
            email="ticket_customer@example.com",
            password="StrongPassword@123",
            role="customer",
        )
        self.agent = User.objects.create_user(
            username="ticket_agent",
            email="ticket_agent@example.com",
            password="StrongPassword@123",
            role="agent",
        )
        self.category = Category.objects.create(
            name="Account Support",
            description="Account-related support tickets",
        )

    def test_ticket_serializer_creates_ticket(self):
        serializer = TicketSerializer(
            data={
                "title": "Unable to update profile",
                "description": "Profile update is failing.",
                "assigned_to": self.agent.id,
                "category": self.category.id,
                "priority": Ticket.Priority.HIGH,
            }
        )

        self.assertTrue(serializer.is_valid(), serializer.errors)

        ticket = serializer.save(created_by=self.customer)

        self.assertEqual(ticket.created_by, self.customer)
        self.assertEqual(ticket.assigned_to, self.agent)
        self.assertEqual(ticket.category, self.category)
        self.assertEqual(ticket.status, Ticket.Status.OPEN)
        self.assertEqual(ticket.priority, Ticket.Priority.HIGH)

    def test_ticket_serializer_returns_related_names(self):
        ticket = Ticket.objects.create(
            title="Password reset issue",
            description="Password reset email was not received.",
            created_by=self.customer,
            assigned_to=self.agent,
            category=self.category,
        )

        data = TicketSerializer(ticket).data

        self.assertEqual(
            data["created_by_username"],
            "ticket_customer",
        )
        self.assertEqual(
            data["assigned_to_username"],
            "ticket_agent",
        )
        self.assertEqual(
            data["category_name"],
            "Account Support",
        )

    def test_created_by_is_read_only(self):
        serializer = TicketSerializer(
            data={
                "title": "Read-only creator test",
                "description": "The creator must come from the request.",
                "created_by": self.agent.id,
            }
        )

        self.assertTrue(serializer.is_valid(), serializer.errors)
        self.assertNotIn("created_by", serializer.validated_data)

        ticket = serializer.save(created_by=self.customer)

        self.assertEqual(ticket.created_by, self.customer)

    def test_ticket_requires_title_and_description(self):
        serializer = TicketSerializer(data={})

        self.assertFalse(serializer.is_valid())
        self.assertIn("title", serializer.errors)
        self.assertIn("description", serializer.errors)

    def test_customer_cannot_assign_ticket_or_change_status(self):
        request = self.factory.post("/api/tickets/")
        request.user = self.customer

        serializer = TicketSerializer(
            data={
                "title": "Restricted fields test",
                "description": "Customer must not control staff fields.",
                "assigned_to": self.agent.id,
                "status": Ticket.Status.RESOLVED,
            },
            context={"request": request},
        )

        self.assertFalse(serializer.is_valid())
        self.assertIn("assigned_to", serializer.errors)
        self.assertIn("status", serializer.errors)

    def test_agent_cannot_reassign_ticket(self):
        other_agent = User.objects.create_user(
            username="other_ticket_agent",
            email="other_ticket_agent@example.com",
            password="StrongPassword@123",
            role="agent",
        )
        request = self.factory.patch("/api/tickets/test/")
        request.user = self.agent

        serializer = TicketSerializer(
            data={
                "assigned_to": other_agent.id,
            },
            partial=True,
            context={"request": request},
        )

        self.assertFalse(serializer.is_valid())
        self.assertIn("assigned_to", serializer.errors)

    def test_ticket_cannot_be_assigned_to_non_agent(self):
        serializer = TicketSerializer(
            data={
                "title": "Invalid assignment test",
                "description": "Customer cannot be an assigned agent.",
                "assigned_to": self.customer.id,
            }
        )

        self.assertFalse(serializer.is_valid())
        self.assertIn("assigned_to", serializer.errors)