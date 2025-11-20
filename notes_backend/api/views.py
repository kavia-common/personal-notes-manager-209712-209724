from typing import Optional
from django.contrib.auth import authenticate, get_user_model
from django.db.models import Q
from rest_framework import permissions, status, viewsets
from rest_framework.authentication import TokenAuthentication, SessionAuthentication
from rest_framework.decorators import api_view, permission_classes
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.authtoken.models import Token

from .models import Note
from .serializers import NoteSerializer, SignupSerializer

User = get_user_model()


# PUBLIC_INTERFACE
@api_view(["GET"])
@permission_classes([permissions.AllowAny])
def health(request):
    """Health check endpoint that returns status ok."""
    return Response({"status": "ok"})


class IsOwner(permissions.BasePermission):
    """Permission to ensure users access only their own notes."""
    def has_object_permission(self, request, view, obj):
        return getattr(obj, "user_id", None) == getattr(request.user, "id", None)


class DefaultPagination(PageNumberPagination):
    """Default pagination for list endpoints."""
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 100


# PUBLIC_INTERFACE
@api_view(["POST"])
@permission_classes([permissions.AllowAny])
def signup(request):
    """
    Register a new user.

    Body:
      - username: string
      - email: string (optional)
      - password: string

    Returns: created user id and username
    """
    serializer = SignupSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        # Optionally create a token immediately
        token, _ = Token.objects.get_or_create(user=user)
        return Response(
            {"id": user.id, "username": user.username, "token": token.key},
            status=status.HTTP_201_CREATED,
        )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# PUBLIC_INTERFACE
@api_view(["POST"])
@permission_classes([permissions.AllowAny])
def login(request):
    """
    Obtain an auth token using username and password.

    Body:
      - username: string
      - password: string

    Returns: token
    """
    username = request.data.get("username")
    password = request.data.get("password")
    if not username or not password:
        return Response({"detail": "username and password required"}, status=400)
    user = authenticate(request, username=username, password=password)
    if not user:
        return Response({"detail": "Invalid credentials"}, status=400)
    token, _ = Token.objects.get_or_create(user=user)
    return Response({"token": token.key})


class NoteViewSet(viewsets.ModelViewSet):
    """
    CRUD operations for notes belonging to the authenticated user.

    Supports:
      - q: search by title or content (case-insensitive)
      - is_archived: boolean filter
      - Pagination via PageNumberPagination
      - Default ordering: updated_at desc
    """
    serializer_class = NoteSerializer
    authentication_classes = [TokenAuthentication, SessionAuthentication]
    permission_classes = [permissions.IsAuthenticated, IsOwner]
    pagination_class = DefaultPagination

    def get_queryset(self):
        user = self.request.user
        qs = Note.objects.filter(user=user)

        # search by q
        q: Optional[str] = self.request.query_params.get("q")
        if q:
            qs = qs.filter(Q(title__icontains=q) | Q(content__icontains=q))

        # filter by is_archived
        is_archived = self.request.query_params.get("is_archived")
        if is_archived is not None:
            if is_archived.lower() in ("true", "1", "yes"):
                qs = qs.filter(is_archived=True)
            elif is_archived.lower() in ("false", "0", "no"):
                qs = qs.filter(is_archived=False)

        # default ordering from model meta applies (-updated_at)
        return qs

    def perform_create(self, serializer):
        serializer.save()  # create() will attach user from request context

    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        ctx["request"] = self.request
        return ctx

    def get_permissions(self):
        # For list/create we just need IsAuthenticated; object-level permission checked on retrieve/update/delete
        if self.action in ["list", "create"]:
            return [permissions.IsAuthenticated()]
        return [permissions.IsAuthenticated(), IsOwner()]
