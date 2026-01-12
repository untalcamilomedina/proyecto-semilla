from __future__ import annotations

from django.contrib.auth import authenticate, login, logout
from django.middleware.csrf import get_token
from django.views.decorators.csrf import ensure_csrf_cookie
from rest_framework import status
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from drf_spectacular.utils import extend_schema
from core.models import User


@extend_schema(
    summary="Get CSRF Token",
    description="Returns a CSRF token to be used in subsequent mutating requests.",
    responses={200: {"type": "object", "properties": {"csrfToken": {"type": "string"}}}}
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
    request={"type": "object", "properties": {
        "email": {"type": "string"},
        "password": {"type": "string"}
    }, "required": ["email", "password"]},
    responses={200: {"type": "object"}, 401: {"type": "object"}}
)
@api_view(["POST"])
@authentication_classes([])
@permission_classes([AllowAny])
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
            {"detail": "Email and password are required"},
            status=status.HTTP_400_BAD_REQUEST
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
        return Response({
            "detail": "Login successful",
            "user": {
                "id": user.id,
                "email": user.email,
                "username": user.username,
                "first_name": user.first_name,
                "last_name": user.last_name,
            }
        })
    
    return Response(
        {"detail": "Invalid credentials"},
        status=status.HTTP_401_UNAUTHORIZED
    )


@api_view(["POST"])
@permission_classes([AllowAny])
def logout_view(request):
    """Logout current user"""
    logout(request)
    return Response({"detail": "Logged out successfully"})


@api_view(["POST"])
@authentication_classes([])
@permission_classes([AllowAny])
def signup_view(request):
    """Register a new user"""
    email = request.data.get("email")
    password1 = request.data.get("password1")
    password2 = request.data.get("password2")

    errors = {}

    if not email:
        errors["email"] = ["Email is required"]
    elif User.objects.filter(email=email).exists():
        errors["email"] = ["This email is already registered"]

    if not password1:
        errors["password1"] = ["Password is required"]
    elif len(password1) < 8:
        errors["password1"] = ["Password must be at least 8 characters"]

    if password1 != password2:
        errors["password2"] = ["Passwords do not match"]

    if errors:
        return Response(errors, status=status.HTTP_400_BAD_REQUEST)

    user = User.objects.create_user(
        username=email.split("@")[0],
        email=email,
        password=password1,
    )
    
    return Response({
        "detail": "Account created successfully",
        "user": {
            "id": user.id,
            "email": user.email,
            "username": user.username,
        }
    }, status=status.HTTP_201_CREATED)


