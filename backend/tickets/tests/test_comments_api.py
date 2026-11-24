from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from tickets.models import Ticket, TicketComment


User = get_user_model()


class TicketCommentAPITests(APITestCase):
    def setUp(self):
        self.manager = User.objects.create_user(
            username="comment_manager",
            email="comment_manager@example.com",
            password="StrongPassword@123",
            role="manager",
        )
        self.agent = User.objects.create_user(
            username="comment_agent",
            email="comment_agent@example.com",
            password="StrongPassword@123",
            role="agent",
        )
        self.other_agent = User.objects.create_user(
            username="other_comment_agent",
            email="other_comment_agent@example.com",
            password="StrongPassword@123",
            role="agent",
        )
        self.customer = User.objects.create_user(
            username="comment_customer",
            email="comment_customer@example.com",
            password="StrongPassword@123",
            role="customer",
        )
        self.other_customer = User.objects.create_user(
            username="other_comment_customer",
            email="other_comment_customer@example.com",
            password="StrongPassword@123",
            role="customer",
        )

        self.ticket = Ticket.objects.create(
            title="Comment API ticket",
            description="Testing the ticket comment API.",
            created_by=self.customer,
            assigned_to=self.agent,
        )
        self.comment = TicketComment.objects.create(
            ticket=self.ticket,
            author=self.agent,
            message="We are checking this issue.",
        )

        self.comments_url = (
            f"/api/tickets/{self.ticket.id}/comments/"
        )

    def authenticate(self, user):
        self.client.force_authenticate(user=user)

    def test_anonymous_user_cannot_list_comments(self):
        response = self.client.get(self.comments_url)

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    def test_ticket_owner_can_list_comments(self):
        self.authenticate(self.customer)

        response = self.client.get(self.comments_url)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )
        self.assertEqual(len(response.data), 1)
        self.assertEqual(
            response.data[0]["message"],
            "We are checking this issue.",
        )
        self.assertEqual(
            response.data[0]["author_username"],
            "comment_agent",
        )

    def test_ticket_owner_can_create_comment(self):
        self.authenticate(self.customer)

        response = self.client.post(
            self.comments_url,
            {
                "message": "Thank you for the update.",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        comment = TicketComment.objects.get(
            id=response.data["id"],
        )

        self.assertEqual(comment.ticket, self.ticket)
        self.assertEqual(comment.author, self.customer)
        self.assertEqual(
            comment.message,
            "Thank you for the update.",
        )

    def test_assigned_agent_can_list_comments(self):
        self.authenticate(self.agent)

        response = self.client.get(self.comments_url)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )
        self.assertEqual(len(response.data), 1)

    def test_other_customer_cannot_access_comments(self):
        self.authenticate(self.other_customer)

        response = self.client.get(self.comments_url)

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )

    def test_unassigned_agent_cannot_access_comments(self):
        self.authenticate(self.other_agent)

        response = self.client.get(self.comments_url)

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )

    def test_manager_can_access_comments(self):
        self.authenticate(self.manager)

        response = self.client.get(self.comments_url)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )
        self.assertEqual(len(response.data), 1)