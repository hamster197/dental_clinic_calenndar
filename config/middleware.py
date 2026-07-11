import threading

from django.http import HttpRequest, HttpResponse
from django.utils.deprecation import MiddlewareMixin

_thread_locals = threading.local()

def get_current_user():
    return getattr(_thread_locals, 'user', None)

class CurrentUserMiddleware(MiddlewareMixin):

    def process_request(self, request: HttpRequest) -> None:
        _thread_locals.user = getattr(request, 'user', None)

    def process_response(self, request: HttpRequest, response: HttpResponse):
        if hasattr(_thread_locals, 'user'):
            del _thread_locals.user

        return response

    def process_exception(self, request: HttpRequest, exception: Exception):
        if hasattr(_thread_locals, 'user'):
            del _thread_locals.user

        return None