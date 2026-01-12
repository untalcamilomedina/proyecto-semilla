from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status

def custom_exception_handler(exc, context):
    """
    Custom exception handler for DRF to provide a unified error format.
    Format:
    {
        "status": "error",
        "code": "exception_type",
        "message": "Human readable message",
        "details": { ... }
    }
    """
    response = exception_handler(exc, context)

    if response is not None:
        custom_data = {
            "status": "error",
            "code": getattr(exc, "default_code", "error"),
            "message": str(exc.detail) if hasattr(exc, "detail") else "An error occurred",
            "details": response.data if isinstance(response.data, dict) else {"non_field_errors": response.data}
        }
        
        # Handle simple string details
        if isinstance(response.data, str):
            custom_data["message"] = response.data
            custom_data["details"] = {}

        response.data = custom_data

    return response
