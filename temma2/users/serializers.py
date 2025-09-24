from rest_framework import serializers
from .models import CustomUser
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth import authenticate

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=2)
    re_password = serializers.CharField(write_only=True, min_length=2)

    class Meta:
        model = CustomUser
        fields = [
            "id",
            "full_name",
            "phone_number",
            "email",
            "region",
            "birth_date",
            "education_level",
            "role",
            "password",
            "re_password",
        ]
        extra_kwargs = {
            "email": {"required": False, "allow_null": True},
            "birth_date": {"required": False, "allow_null": True},
            "education_level": {"required": False, "allow_null": True},
        }

    def validate(self, data):
        if data["password"] != data["re_password"]:
            raise serializers.ValidationError({"password": "Passwords do not match"})
        return data

    def create(self, validated_data):
        validated_data.pop("re_password")
        password = validated_data.pop("password")

        user = CustomUser(**validated_data)
        user.set_password(password)  # hash password
        user.save()
        return user




class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    username_field = "phone_number"

    def validate(self, attrs):
        phone_number = attrs.get("phone_number")
        password = attrs.get("password")

        user = authenticate(username=phone_number, password=password)
        if not user:
            raise serializers.ValidationError("Invalid phone number or password")

        data = super().validate(attrs)
        data["user"] = {
            "id": user.id,
            "full_name": user.full_name,
            "phone_number": user.phone_number,
            "email": user.email,
            "role": user.role,
        }
        return data



