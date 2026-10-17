from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.test import TestCase
from rest_framework.test import APIRequestFactory

from tickets.models import Ticket
from tickets.permissions import IsTicketParticipantOrStaff


User = get_user_model()


class IsTicketParticipantOrStaffTests(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.permission = IsTicketParticipantOrStaff()

        self.admin = User.objects.create_user(
            username="ticket_admin",
            email="ticket_admin@example.com",
            password="StrongPassword@123",
            role="admin",
        )
        self.manager = User.objects.create_user(
            username="ticket_manager",
            email="ticket_manager@example.com",
            password="StrongPassword@123",
            role="manager",
        )
        self.agent = User.objects.create_user(
            username="assigned_agent",
            email="assigned_agent@example.com",
            password="StrongPassword@123",
            role="agent",
        )
        self.other_agent = User.objects.create_user(
            username="other_agent",
            email="other_agent@example.com",
            password="StrongPassword@123",
            role="agent",
        )
        self.customer = User.objects.create_user(
            username="ticket_owner",
            email="ticket_owner@example.com",
            password="StrongPassword@123",
            role="customer",
        )
        self.other_customer = User.objects.create_user(
            username="other_customer",
            email="other_customer@example.com",
            password="StrongPassword@123",
            role="customer",
        )

        self.ticket = Ticket.objects.create(
            title="Permission test ticket",
            description="Testing ticket object permissions.",
            created_by=self.customer,
            assigned_to=self.agent,
        )

    def create_request(self, user, method="get"):
        request_method = getattr(self.factory, method)
        request = request_method(
            f"/api/tickets/{self.ticket.id}/"
        )
        request.user = user
        return request

    def test_authenticated_user_has_general_permission(self):
        request = self.create_request(self.customer)

        has_permission = self.permission.has_permission(
            request,
            view=None,
        )

        self.assertTrue(has_permission)

    def test_anonymous_user_has_no_general_permission(self):
        request = self.create_request(AnonymousUser())

        has_permission = self.permission.has_permission(
            request,
            view=None,
        )

        self.assertFalse(has_permission)

    def test_admin_and_manager_can_access_any_ticket(self):
        for user in (self.admin, self.manager):
            with self.subTest(role=user.role):
                request = self.create_request(user)

                has_permission = (
                    self.permission.has_object_permission(
                        request,
                        view=None,
                        obj=self.ticket,
                    )
                )

                self.assertTrue(has_permission)

    def test_assigned_agent_can_access_ticket(self):
        request = self.create_request(self.agent)

        has_permission = self.permission.has_object_permission(
            request,
            view=None,
            obj=self.ticket,
        )

        self.assertTrue(has_permission)

    def test_unassigned_agent_cannot_access_ticket(self):
        request = self.create_request(self.other_agent)

        has_permission = self.permission.has_object_permission(
            request,
            view=None,
            obj=self.ticket,
        )

        self.assertFalse(has_permission)

    def test_ticket_owner_can_access_ticket(self):
        request = self.create_request(self.customer)

        has_permission = self.permission.has_object_permission(
            request,
            view=None,
            obj=self.ticket,
        )

        self.assertTrue(has_permission)

    def test_other_customer_cannot_access_ticket(self):
        request = self.create_request(self.other_customer)

        has_permission = self.permission.has_object_permission(
            request,
            view=None,
            obj=self.ticket,
        )

        self.assertFalse(has_permission)

    def test_admin_and_manager_can_delete_ticket(self):
        for user in (self.admin, self.manager):
            with self.subTest(role=user.role):
                request = self.create_request(
                    user,
                    method="delete",
                )

                has_permission = (
                    self.permission.has_object_permission(
                        request,
                        view=None,
                        obj=self.ticket,
                    )
                )

                self.assertTrue(has_permission)

    def test_agent_and_customer_cannot_delete_ticket(self):
        for user in (self.agent, self.customer):
            with self.subTest(role=user.role):
                request = self.create_request(
                    user,
                    method="delete",
                )

                has_permission = (
                    self.permission.has_object_permission(
                        request,
                        view=None,
                        obj=self.ticket,
                    )
                )

                self.assertFalse(has_permission)