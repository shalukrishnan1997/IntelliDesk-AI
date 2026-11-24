from django.urls import path

from .views import (
    CategoryListView,
    TicketCommentListCreateView,
    TicketDetailView,
    TicketListCreateView,
)


urlpatterns = [
    path(
        "categories/",
        CategoryListView.as_view(),
        name="category-list",
    ),
    path(
        "",
        TicketListCreateView.as_view(),
        name="ticket-list-create",
    ),
    path(
        "<uuid:ticket_pk>/comments/",
        TicketCommentListCreateView.as_view(),
        name="ticket-comment-list-create",
    ),


    path(
        "<uuid:pk>/",
        TicketDetailView.as_view(),
        name="ticket-detail",
    ),
]