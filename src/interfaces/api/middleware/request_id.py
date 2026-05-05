"""
RequestIdMiddleware — assigns a unique request_id to every HTTP request.

The ID is taken from the incoming X-Request-ID header when present (useful for
tracing across services), or generated as a UUID4.  It is stored in a ContextVar
so that every log statement emitted during the request automatically includes it.
The ID is also echoed back in the X-Request-ID response header.
"""
import uuid

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from src.infrastructure.logging.setup import request_id_var


class RequestIdMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
        token = request_id_var.set(request_id)
        try:
            response: Response = await call_next(request)
        finally:
            request_id_var.reset(token)
        response.headers["X-Request-ID"] = request_id
        return response
