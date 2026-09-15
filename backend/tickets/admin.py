from django.contrib import admin

from .models import Category, Ticket


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "is_active",
        "created_at",
        "updated_at",
    )
    list_filter = (
        "is_active",
    )
    search_fields = (
        "name",
        "description",
    )
    ordering = (
        "name",
    )
    readonly_fields = (
        "id",
        "created_at",
        "updated_at",
    )


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "status",
        "priority",
        "category",
        "created_by",
        "assigned_to",
        "created_at",
    )
    list_filter = (
        "status",
        "priority",
        "category",
        "created_at",
    )
    search_fields = (
        "title",
        "description",
        "created_by__username",
        "created_by__email",
        "assigned_to__username",
        "assigned_to__email",
    )
    ordering = (
        "-created_at",
    )
    readonly_fields = (
        "id",
        "created_at",
        "updated_at",
    )
    raw_id_fields = (
        "created_by",
        "assigned_to",
    )
    list_select_related = (
        "category",
        "created_by",
        "assigned_to",
    )