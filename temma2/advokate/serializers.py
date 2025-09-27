from rest_framework import serializers
from .models import AdvokateRequest

class AdvokateRequestSerializer(serializers.ModelSerializer):
    user_full_name = serializers.CharField(source="user.full_name", read_only=True)

    class Meta:
        model = AdvokateRequest
        fields = [
            "id",
            "user",
            "user_full_name",
            "problem",
            "email",
            "phone_number",
            "created_at",
        ]
        read_only_fields = ["id", "user", "created_at"]
