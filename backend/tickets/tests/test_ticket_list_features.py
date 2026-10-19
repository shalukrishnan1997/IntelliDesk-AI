from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from tickets.models import Category, Ticket


User = get_user_model()


class TicketListFeatureTests(APITestCase):
    def setUp(self):
        self.manager = User.objects.create_user(
            username="filter_manager",
            email="filter_manager@example.com",
            password="StrongPassword@123",
            role="manager",
        )
        self.customer = User.objects.create_user(
            username="filter_customer",
            email="filter_customer@example.com",
            password="StrongPassword@123",
            role="customer",
        )
        self.agent = User.objects.create_user(
            username="filter_agent",
            email="filter_agent@example.com",
            password="StrongPassword@123",
            role="agent",
        )
        self.category = Category.objects.create(
            name="Account Support",
            description="Account-related tickets",
        )

        for index in range(12):
            title = f"Ticket {index:02d}"

            if index == 0:
                title = "Password reset issue"

            Ticket.objects.create(
                title=title,
                description=f"Test ticket number {index}",
                created_by=self.customer,
                assigned_to=self.agent,
                category=self.category,
                status=(
                    Ticket.Status.RESOLVED
                    if index < 3
                    else Ticket.Status.OPEN
                ),
                priority=(
                    Ticket.Priority.URGENT
                    if index < 2
                    else Ticket.Priority.MEDIUM
                ),
            )

        self.client.force_authenticate(user=self.manager)

    def test_filters_tickets_by_status(self):
        response = self.client.get(
            "/api/tickets/",
            {"status": Ticket.Status.RESOLVED},
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )
        self.assertEqual(response.data["count"], 3)

        for ticket in response.data["results"]:
            self.assertEqual(
                ticket["status"],
                Ticket.Status.RESOLVED,
            )

    def test_filters_tickets_by_priority(self):
        response = self.client.get(
            "/api/tickets/",
            {"priority": Ticket.Priority.URGENT},
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )
        self.assertEqual(response.data["count"], 2)

        for ticket in response.data["results"]:
            self.assertEqual(
                ticket["priority"],
                Ticket.Priority.URGENT,
            )

    def test_searches_tickets_by_title(self):
        response = self.client.get(
            "/api/tickets/",
            {"search": "Password"},
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(
            response.data["results"][0]["title"],
            "Password reset issue",
        )

    def test_orders_tickets_by_title(self):
        response = self.client.get(
            "/api/tickets/",
            {
                "ordering": "title",
                "page_size": 100,
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        titles = [
            ticket["title"]
            for ticket in response.data["results"]
        ]

        self.assertEqual(titles, sorted(titles))

    def test_uses_default_page_size(self):
        response = self.client.get("/api/tickets/")

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )
        self.assertEqual(response.data["count"], 12)
        self.assertEqual(len(response.data["results"]), 10)
        self.assertIsNotNone(response.data["next"])
        self.assertIsNone(response.data["previous"])

    def test_returns_second_page(self):
        response = self.client.get(
            "/api/tickets/",
            {"page": 2},
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )
        self.assertEqual(response.data["count"], 12)
        self.assertEqual(len(response.data["results"]), 2)
        self.assertIsNone(response.data["next"])
        self.assertIsNotNone(response.data["previous"])