from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError
from typing import Any, Dict, Optional
import logging
import traceback
import sys
from datetime import datetime

from ...config import Settings, get_settings
from ...utils.security import sanitize_token

# Initialize logger
logger = logging.getLogger(__name__)

class APIError(Exception):
    """Base API Error class"""
    def __init__(
        self,
        message: str,
        code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.code = code
        self.details = details or {}
        super().__init__(message)

class ErrorHandler:
    """Handles API error responses"""
    
    def __init__(self, settings: Settings):
        self.settings = settings
        self.include_details = settings.ENVIRONMENT != "production"

    async def handle_error(
        self,
        request: Request,
        exc: Exception
    ) -> JSONResponse:
        """Handle different types of errors and return appropriate responses"""
        
        # Initialize error context
        error_context = {
            "timestamp": datetime.utcnow().isoformat(),
            "path": request.url.path,
            "method": request.method,
        }

        # Handle different error types
        if isinstance(exc, APIError):
            return await self._handle_api_error(exc, error_context)
            
        elif isinstance(exc, RequestValidationError):
            return await self._handle_validation_error(exc, error_context)
            
        elif isinstance(exc, SQLAlchemyError):
            return await self._handle_database_error(exc, error_context)
            
        else:
            return await self._handle_unexpected_error(exc, error_context)

    async def _handle_api_error(
        self,
        exc: APIError,
        context: Dict[str, Any]
    ) -> JSONResponse:
        """Handle custom API errors"""
        response = {
            "error": {
                "message": exc.message,
                "code": exc.code,
                **context
            }
        }

        if self.include_details and exc.details:
            response["error"]["details"] = exc.details

        return JSONResponse(
            status_code=exc.code,
            content=response
        )

    async def _handle_validation_error(
        self,
        exc: RequestValidationError,
        context: Dict[str, Any]
    ) -> JSONResponse:
        """Handle request validation errors"""
        # Clean validation errors
        clean_errors = []
        for error in exc.errors():
            clean_error = {
                "loc": " -> ".join(str(x) for x in error["loc"]),
                "msg": error["msg"],
                "type": error["type"]
            }
            clean_errors.append(clean_error)

        response = {
            "error": {
                "message": "Validation error",
                "code": status.HTTP_422_UNPROCESSABLE_ENTITY,
                "validation_errors": clean_errors,
                **context
            }
        }

        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=response
        )

    async def _handle_database_error(
        self,
        exc: SQLAlchemyError,
        context: Dict[str, Any]
    ) -> JSONResponse:
        """Handle database errors"""
        error_msg = "Database error occurred"
        
        # Log the full error
        logger.error(
            f"Database error: {str(exc)}\n"
            f"Context: {context}\n"
            f"Traceback: {''.join(traceback.format_tb(exc.__traceback__))}"
        )

        response = {
            "error": {
                "message": error_msg,
                "code": status.HTTP_500_INTERNAL_SERVER_ERROR,
                **context
            }
        }

        if self.include_details:
            response["error"]["details"] = {
                "error_type": exc.__class__.__name__,
                "error_message": str(exc)
            }

        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=response
        )

    async def _handle_unexpected_error(
        self,
        exc: Exception,
        context: Dict[str, Any]
    ) -> JSONResponse:
        """Handle unexpected errors"""
        error_msg = "An unexpected error occurred"
        
        # Log the full error
        logger.error(
            f"Unexpected error: {str(exc)}\n"
            f"Context: {context}\n"
            f"Traceback: {''.join(traceback.format_tb(exc.__traceback__))}"
        )

        response = {
            "error": {
                "message": error_msg,
                "code": status.HTTP_500_INTERNAL_SERVER_ERROR,
                **context
            }
        }

        if self.include_details:
            response["error"]["details"] = {
                "error_type": exc.__class__.__name__,
                "error_message": str(exc)
            }

        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=response
        )

    async def log_error(
        self,
        request: Request,
        exc: Exception,
        error_id: str
    ) -> None:
        """Log error details"""
        # Gather request information
        headers = dict(request.headers)
        if "authorization" in headers:
            headers["authorization"] = sanitize_token(headers["authorization"])

        # Create error log
        error_log = {
            "error_id": error_id,
            "timestamp": datetime.utcnow().isoformat(),
            "request": {
                "method": request.method,
                "url": str(request.url),
                "headers": headers,
                "client_host": request.client.host if request.client else None,
            },
            "error": {
                "type": exc.__class__.__name__,
                "message": str(exc),
                "traceback": traceback.format_exception(
                    type(exc),
                    exc,
                    exc.__traceback__
                )
            }
        }

        # Log error details
        logger.error(f"Error {error_id}: {error_log}")

        # If in development, print to console
        if self.settings.ENVIRONMENT == "development":
            print("\n=== Error Details ===")
            print(f"Error ID: {error_id}")
            print(f"Type: {exc.__class__.__name__}")
            print(f"Message: {str(exc)}")
            print("\nTraceback:")
            traceback.print_exception(
                type(exc),
                exc,
                exc.__traceback__,
                file=sys.stderr
            )
            print("==================\n")

# Create custom exceptions for common cases
class ValidationError(APIError):
    def __init__(
        self,
        message: str,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message,
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            details
        )

class AuthenticationError(APIError):
    def __init__(
        self,
        message: str = "Authentication required",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message,
            status.HTTP_401_UNAUTHORIZED,
            details
        )

class AuthorizationError(APIError):
    def __init__(
        self,
        message: str = "Permission denied",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message,
            status.HTTP_403_FORBIDDEN,
            details
        )

class NotFoundError(APIError):
    def __init__(
        self,
        message: str,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message,
            status.HTTP_404_NOT_FOUND,
            details
        )

class RateLimitError(APIError):
    def __init__(
        self,
        message: str = "Rate limit exceeded",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message,
            status.HTTP_429_TOO_MANY_REQUESTS,
            details
        )

# Initialize global error handler
error_handler = ErrorHandler(get_settings())

# Example usage in routes:
"""
@router.get("/items/{item_id}")
async def get_item(item_id: str):
    item = await db.get_item(item_id)
    if not item:
        raise NotFoundError(f"Item {item_id} not found")
    return item
"""