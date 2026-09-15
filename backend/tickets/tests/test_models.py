import uuid

from django.contrib.auth import get_user_model
from django.test import TestCase

from tickets.models import Category, Ticket


User = get_user_model()


class CategoryModelTests(TestCase):
    def test_category_uses_uuid_as_primary_key(self):
        category = Category.objects.create(
            name="Technical Support",
            description="Technical issues and troubleshooting.",
        )

        self.assertIsInstance(category.id, uuid.UUID)

    def test_category_string_representation_is_name(self):
        category = Category.objects.create(
            name="Billing",
        )

        self.assertEqual(str(category), "Billing")


class TicketModelTests(TestCase):
    def setUp(self):
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
            name="Account Access",
        )

    def create_ticket(self, **kwargs):
        ticket_data = {
            "title": "Unable to access account",
            "description": "The customer cannot log in.",
            "created_by": self.customer,
            "assigned_to": self.agent,
            "category": self.category,
        }
        ticket_data.update(kwargs)

        return Ticket.objects.create(**ticket_data)

    def test_ticket_uses_uuid_and_default_values(self):
        ticket = self.create_ticket()

        self.assertIsInstance(ticket.id, uuid.UUID)
        self.assertEqual(ticket.status, Ticket.Status.OPEN)
        self.assertEqual(ticket.priority, Ticket.Priority.MEDIUM)

    def test_ticket_string_representation_is_title(self):
        ticket = self.create_ticket()

        self.assertEqual(str(ticket), "Unable to access account")

    def test_ticket_relationships_are_saved(self):
        ticket = self.create_ticket()

        self.assertEqual(ticket.created_by, self.customer)
        self.assertEqual(ticket.assigned_to, self.agent)
        self.assertEqual(ticket.category, self.category)

    def test_deleting_category_does_not_delete_ticket(self):
        ticket = self.create_ticket()

        self.category.delete()
        ticket.refresh_from_db()

        self.assertIsNone(ticket.category)

    def test_deleting_assigned_agent_does_not_delete_ticket(self):
        ticket = self.create_ticket()

        self.agent.delete()
        ticket.refresh_from_db()

        self.assertIsNone(ticket.assigned_to)

    def test_deleting_creator_deletes_ticket(self):
        ticket = self.create_ticket()
        ticket_id = ticket.id

        self.customer.delete()

        self.assertFalse(
            Ticket.objects.filter(id=ticket_id).exists()
        )