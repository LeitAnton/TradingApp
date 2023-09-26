from rest_framework.authentication import SessionAuthentication


class CsrfExemptSessionAuthentication(SessionAuthentication):
    """Custom authentication class that exempts CSRF enforcement for session-based authentication.

    This authentication class inherits from `SessionAuthentication` and overrides the `enforce_csrf` method
    to disable CSRF (Cross-Site Request Forgery) protection for session-based authentication.

    """

    def enforce_csrf(self, request):
        """Exempt CSRF enforcement for session-based authentication.

        This method is overridden to prevent CSRF checks for requests using session-based authentication.

        Args:
            request (HttpRequest): The incoming HTTP request.

        """
        return
