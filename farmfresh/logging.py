import logging
import uuid

from django.utils.deprecation import MiddlewareMixin

from .request_context import current_request_id


class RequestIdFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        # Inject the current request id into logs
        record.request_id = current_request_id.get()
        return True


class RequestIdMiddleware(MiddlewareMixin):
    def process_request(self, request):
        request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
        request.request_id = request_id
        current_request_id.set(request_id)

    def process_response(self, request, response):
        request_id = getattr(request, "request_id", None) or current_request_id.get()
        if request_id and isinstance(response, object):
            response["X-Request-ID"] = request_id
        # reset context var for safety
        current_request_id.set("-")
        return response



