import jwt
from rest_framework import status
from rest_framework.exceptions import PermissionDenied

from TradingApp import settings
from user.models import User


class AuthenticationMiddleware:
    """Custom authentication middleware for JWT-based authentication.

    This middleware checks the JWT token provided in the 'Authorization' header
    and associates the user with the request if the token is valid.

    Attributes:
        get_response (callable): The next middleware or view function to be called.

    """

    def raise_error(self, msg):
        """Raise a PermissionDenied exception with a custom error message.

        Args:
            msg (str): The error message to be included in the exception.

        Raises:
            PermissionDenied: An exception indicating a permission error.

        """
        error = {
            'error_code': status.HTTP_403_FORBIDDEN,
            'error_message': msg,
        }
        raise PermissionDenied(error)

    def __init__(self, get_response):
        """Initialize the middleware with a callable for the next step in the request/response process.

        Args:
            get_response (callable): The next middleware or view function to be called.

        """
        self.get_response = get_response

    def __call__(self, request):
        """Handle the incoming request and perform JWT authentication.

        This method checks if the request path requires authentication, validates the JWT token,
        and associates the user with the request.

        Args:
            request (HttpRequest): The incoming HTTP request.

        Returns:
            HttpResponse: The HTTP response from the next middleware or view function.

        """
        exclusion_list = (
            '/',
            '/swagger/',
            '/api/users/user/login/',
            '/api/users/user/registration/',
        )

        if request.path not in exclusion_list and not request.path.startswith('/admin/'):
            try:
                auth_header = request.headers.get('Authorization').split()
                token = auth_header[1]
                payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256', ])
                user = User.objects.get(pk=payload['id'])
                request.user = user

            except Exception:
                msg = 'The token is invalid or expired. '
                raise self.raise_error(msg)

            if not request.user.is_active:
                msg = 'This user has been deactivated.'
                raise self.raise_error(msg)

        return self.get_response(request)
