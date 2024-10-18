
from django.utils.deprecation import MiddlewareMixin
from django.contrib.sessions.middleware import SessionMiddleware
from django.contrib.sessions.backends.db import SessionStore as DBSessionStore
from django.contrib.sessions.backends.cache import SessionStore as CacheSessionStore

class CustomUserSessionMiddleware(MiddlewareMixin):
    def __init__(self, get_response=None):
        super().__init__(get_response)
        self.user_session_store = DBSessionStore()
        self.admin_session_store = CacheSessionStore()

    def process_request(self, request):
        # Use a different session store and cookie name for user and admin
        if request.path.startswith('/admin/'):
            request.session = self.admin_session_store
            request.session_cookie_name = 'admin_sessionid'
        else:
            request.session = self.user_session_store
            request.session_cookie_name = 'user_sessionid'

    def process_response(self, request, response):
        # Ensure the correct session cookie is used for response
        if hasattr(request, 'session_cookie_name'):
            response.set_cookie(request.session_cookie_name, request.session.session_key)
        return response
