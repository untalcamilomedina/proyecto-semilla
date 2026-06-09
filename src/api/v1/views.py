from __future__ import annotations

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from django.middleware.csrf import get_token
from django.views.decorators.csrf import ensure_csrf_cookie
from django_ratelimit.decorators import ratelimit
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from core.models import User


@extend_schema(
    summary="Get CSRF Token",
    description="Returns a CSRF token to be used in subsequent mutating requests.",
    responses={200: {"type": "object", "properties": {"csrfToken": {"type": "string"}}}},
)
@api_view(["GET"])
@authentication_classes([])
@permission_classes([AllowAny])
@ensure_csrf_cookie
def csrf(request):
    return Response({"csrfToken": get_token(request)})


@extend_schema(
    summary="Login",
    description="Authenticates a user with email and password and creates a session.",
    request={
        "type": "object",
        "properties": {"email": {"type": "string"}, "password": {"type": "string"}},
        "required": ["email", "password"],
    },
    responses={200: {"type": "object"}, 401: {"type": "object"}},
)
@api_view(["POST"])
@authentication_classes([])
@permission_classes([AllowAny])
@ratelimit(key="ip", rate="20/m", method="POST", block=True)
def login_view(request):
    """Login user with email and password.

    Args:
        request: The Django request object containing email and password.

    Returns:
        Response: Login success or failure message with user data.
    """
    email = request.data.get("email")
    password = request.data.get("password")

    if not email or not password:
        return Response(
            {"detail": "Email and password are required"}, status=status.HTTP_400_BAD_REQUEST
        )

    # Authenticate with email as username
    user = authenticate(request, username=email, password=password)
    if user is None:
        # Try to find user by email and authenticate
        try:
            user_obj = User.objects.get(email=email)
            user = authenticate(request, username=user_obj.username, password=password)
        except User.DoesNotExist:
            pass

    if user is not None and user.is_active:
        login(request, user)
        return Response(
            {
                "detail": "Login successful",
                "user": {
                    "id": user.id,
                    "email": user.email,
                    "username": user.username,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                },
            }
        )

    return Response({"detail": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)


@extend_schema(
    summary="Logout",
    description=(
        "Logs out the current user. Invalidates the Django session and, "
        "if a `refresh` token is provided, blacklists it (JWT)."
    ),
    request={"type": "object", "properties": {"refresh": {"type": "string"}}},
    responses={200: {"type": "object"}},
)
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def logout_view(request):
    """Logout current user: kill session and blacklist the JWT refresh token."""
    refresh = request.data.get("refresh")
    if refresh:
        try:
            from rest_framework_simplejwt.tokens import RefreshToken

            RefreshToken(refresh).blacklist()
        except Exception:  # noqa: S110
            # Token inválido/expirado: el logout de sesión sigue siendo válido.
            pass
    logout(request)
    return Response({"detail": "Logged out successfully"})


@extend_schema(
    summary="Signup",
    description=(
        "Registers a new user account. Password is checked against AUTH_PASSWORD_VALIDATORS."
    ),
    request={
        "type": "object",
        "properties": {
            "email": {"type": "string"},
            "password1": {"type": "string"},
            "password2": {"type": "string"},
        },
        "required": ["email", "password1", "password2"],
    },
    responses={201: {"type": "object"}, 400: {"type": "object"}},
)
@api_view(["POST"])
@authentication_classes([])
@permission_classes([AllowAny])
@ratelimit(key="ip", rate="10/h", method="POST", block=True)
def signup_view(request):
    """Register a new user"""
    email = (request.data.get("email") or "").strip().lower()
    password1 = request.data.get("password1")
    password2 = request.data.get("password2")

    errors = {}

    if not email:
        errors["email"] = ["Email is required"]
    elif User.objects.filter(email=email).exists():
        errors["email"] = ["This email is already registered"]

    if not password1:
        errors["password1"] = ["Password is required"]
    else:
        try:
            validate_password(password1)
        except DjangoValidationError as exc:
            errors["password1"] = list(exc.messages)

    if password1 != password2:
        errors["password2"] = ["Passwords do not match"]

    if errors:
        return Response(errors, status=status.HTTP_400_BAD_REQUEST)

    # El email es único: usarlo como username evita colisiones de prefijo.
    user = User.objects.create_user(
        username=email,
        email=email,
        password=password1,
    )

    try:
        from allauth.account.utils import send_email_confirmation

        send_email_confirmation(request, user, signup=True)
    except Exception:  # noqa: S110
        # El registro no debe fallar si el backend de email no está disponible.
        pass

    return Response(
        {
            "detail": "Account created successfully",
            "user": {
                "id": user.id,
                "email": user.email,
                "username": user.username,
            },
        },
        status=status.HTTP_201_CREATED,
    )
