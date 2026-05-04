"""
Rate limiting configuration for TutoratUp API.

Uses slowapi to prevent abuse on critical endpoints:
- Authentication: strict (5 attempts/minute)
- Search/List: moderate (30 requests/minute)
- General: relaxed (100 requests/minute)
"""

from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi import Request
from fastapi.responses import JSONResponse
import logging

logger = logging.getLogger(__name__)

# Initialize rate limiter using IP address as key
limiter = Limiter(key_func=get_remote_address)


async def rate_limit_error_handler(request: Request, exc: RateLimitExceeded) -> JSONResponse:
    """Custom error handler for rate limit exceeded responses."""
    return JSONResponse(
        status_code=429,
        content={
            "detail": "Rate limit exceeded. Please try again later.",
            "retry_after": exc.detail if hasattr(exc, "detail") else None,
        },
    )


# Rate limit templates for common use cases
RATE_LIMITS = {
    "auth": "5/minute",  # Login, register, password reset
    "search": "30/minute",  # Search endpoints
    "list": "60/minute",  # List/fetch endpoints
    "general": "100/minute",  # Standard endpoints
    "global": "1000/minute",  # Global fallback
}
