from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from tickets.models import Category, Ticket


User = get_user_model()


class TicketAPITests(APITestCase):
    def setUp(self):
        self.admin = User.objects.create_user(
            username="api_admin",
            email="api_admin@example.com",
            password="StrongPassword@123",
            role="admin",
        )
        self.manager = User.objects.create_user(
            username="api_manager",
            email="api_manager@example.com",
            password="StrongPassword@123",
            role="manager",
        )
        self.agent = User.objects.create_user(
            username="api_agent",
            email="api_agent@example.com",
            password="StrongPassword@123",
            role="agent",
        )
        self.other_agent = User.objects.create_user(
            username="api_other_agent",
            email="api_other_agent@example.com",
            password="StrongPassword@123",
            role="agent",
        )
        self.customer = User.objects.create_user(
            username="api_customer",
            email="api_customer@example.com",
            password="StrongPassword@123",
            role="customer",
        )
        self.other_customer = User.objects.create_user(
            username="api_other_customer",
            email="api_other_customer@example.com",
            password="StrongPassword@123",
            role="customer",
        )

        self.category = Category.objects.create(
            name="Technical Support",
            description="Technical support requests",
        )
        self.inactive_category = Category.objects.create(
            name="Archived Category",
            description="Inactive category",
            is_active=False,
        )

        self.customer_ticket = Ticket.objects.create(
            title="Customer ticket",
            description="Created by the primary customer.",
            created_by=self.customer,
            assigned_to=self.agent,
            category=self.category,
            priority=Ticket.Priority.HIGH,
        )
        self.other_ticket = Ticket.objects.create(
            title="Other customer ticket",
            description="Created by another customer.",
            created_by=self.other_customer,
            assigned_to=self.other_agent,
            category=self.category,
        )

    def authenticate(self, user):
        self.client.force_authenticate(user=user)

    def test_anonymous_user_cannot_list_tickets(self):
        response = self.client.get("/api/tickets/")

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    def test_customer_can_create_ticket(self):
        self.authenticate(self.customer)

        response = self.client.post(
            "/api/tickets/",
            {
                "title": "New support request",
                "description": "I need help with my account.",
                "category": str(self.category.id),
                "priority": Ticket.Priority.URGENT,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        ticket = Ticket.objects.get(
            id=response.data["id"],
        )

        self.assertEqual(ticket.created_by, self.customer)
        self.assertEqual(ticket.status, Ticket.Status.OPEN)
        self.assertEqual(ticket.priority, Ticket.Priority.URGENT)

    def test_customer_lists_only_own_tickets(self):
        self.authenticate(self.customer)

        response = self.client.get("/api/tickets/")

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )
        self.assertEqual(len(response.data), 1)
        self.assertEqual(
            response.data[0]["id"],
            str(self.customer_ticket.id),
        )

    def test_agent_lists_only_assigned_tickets(self):
        self.authenticate(self.agent)

        response = self.client.get("/api/tickets/")

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )
        self.assertEqual(len(response.data), 1)
        self.assertEqual(
            response.data[0]["id"],
            str(self.customer_ticket.id),
        )

    def test_manager_can_list_all_tickets(self):
        self.authenticate(self.manager)

        response = self.client.get("/api/tickets/")

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )
        self.assertEqual(len(response.data), 2)

    def test_admin_can_list_all_tickets(self):
        self.authenticate(self.admin)

        response = self.client.get("/api/tickets/")

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )
        self.assertEqual(len(response.data), 2)

    def test_customer_can_retrieve_own_ticket(self):
        self.authenticate(self.customer)

        response = self.client.get(
            f"/api/tickets/{self.customer_ticket.id}/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )
        self.assertEqual(
            response.data["title"],
            "Customer ticket",
        )

    def test_customer_cannot_retrieve_another_customers_ticket(self):
        self.authenticate(self.customer)

        response = self.client.get(
            f"/api/tickets/{self.other_ticket.id}/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )

    def test_assigned_agent_can_retrieve_ticket(self):
        self.authenticate(self.agent)

        response = self.client.get(
            f"/api/tickets/{self.customer_ticket.id}/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

    def test_only_active_categories_are_listed(self):
        self.authenticate(self.customer)

        response = self.client.get(
            "/api/tickets/categories/"  
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )
        self.assertEqual(len(response.data), 1)
        self.assertEqual(
            response.data[0]["name"],
            "Technical Support",
        )