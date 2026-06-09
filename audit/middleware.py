from .context import clear_current_request, set_current_request
from .utils import build_request_metadata


class AuditMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.audit_metadata = build_request_metadata(request)
        set_current_request(request)
        try:
            return self.get_response(request)
        finally:
            clear_current_request()

