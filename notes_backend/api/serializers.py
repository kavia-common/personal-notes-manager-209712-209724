from typing import Any
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from .models import Note

User = get_user_model()


class SignupSerializer(serializers.ModelSerializer):
    """
    Serializer used to register a new user.
    """
    password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ("id", "username", "email", "password")
        read_only_fields = ("id",)

    def validate_password(self, value: str) -> str:
        validate_password(value)
        return value

    def create(self, validated_data: dict[str, Any]) -> User:
        password = validated_data.pop("password")
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


class NoteSerializer(serializers.ModelSerializer):
    """
    Serializer for Note CRUD.
    """
    id = serializers.IntegerField(read_only=True)

    class Meta:
        model = Note
        fields = ("id", "title", "content", "is_archived", "created_at", "updated_at")
        read_only_fields = ("id", "created_at", "updated_at")

    def create(self, validated_data):
        # Ensure the note is created for the authenticated user
        request = self.context.get("request")
        assert request is not None and request.user.is_authenticated, "Authentication required"
        return Note.objects.create(user=request.user, **validated_data)
