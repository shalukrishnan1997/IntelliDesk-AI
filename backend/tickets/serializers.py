from rest_framework import serializers

from .models import Category, Ticket


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = (
            "id",
            "name",
            "description",
            "is_active",
            "created_at",
            "updated_at",
        )
        read_only_fields = (
            "id",
            "created_at",
            "updated_at",
        )


class TicketSerializer(serializers.ModelSerializer):
    created_by_username = serializers.CharField(
        source="created_by.username",
        read_only=True,
    )
    assigned_to_username = serializers.CharField(
        source="assigned_to.username",
        read_only=True,
        allow_null=True,
    )
    category_name = serializers.CharField(
        source="category.name",
        read_only=True,
        allow_null=True,
    )

    class Meta:
        model = Ticket
        fields = (
            "id",
            "title",
            "description",
            "created_by",
            "created_by_username",
            "assigned_to",
            "assigned_to_username",
            "category",
            "category_name",
            "status",
            "priority",
            "created_at",
            "updated_at",
            "resolved_at",
        )
        read_only_fields = (
            "id",
            "created_by",
            "created_by_username",
            "assigned_to_username",
            "category_name",
            "created_at",
            "updated_at",
            "resolved_at",
        )

    def validate_assigned_to(self, value):
        if value is not None and value.role != "agent":
            raise serializers.ValidationError(
                "Tickets can only be assigned to users with the agent role."
            )

        return value

    def validate(self, attrs):
        request = self.context.get("request")

        if request is None:
            return attrs

        user = request.user
        errors = {}

        if user.role == "customer":
            if "assigned_to" in self.initial_data:
                errors["assigned_to"] = (
                    "Customers cannot assign tickets."
                )

            if "status" in self.initial_data:
                errors["status"] = (
                    "Customers cannot change ticket status."
                )

        if user.role == "agent":
            if "assigned_to" in self.initial_data:
                errors["assigned_to"] = (
                    "Agents cannot assign or reassign tickets."
                )

        if errors:
            raise serializers.ValidationError(errors)

        return attrs
        