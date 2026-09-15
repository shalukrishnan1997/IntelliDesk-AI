from django.urls import path

from .views import (
    UserListView,
    UserProfileView,
    UserRegistrationView,
)


urlpatterns = [
    path(
        "register/",
        UserRegistrationView.as_view(),
        name="register",
    ),
    path(
        "profile/",
        UserProfileView.as_view(),
        name="profile",
    ),
    path(
        "users/",
        UserListView.as_view(),
        name="user-list",
    ),
]