import jwt
from rest_framework import status
from rest_framework.exceptions import PermissionDenied
from rest_framework.generics import get_object_or_404

from TradingApp import settings

# from django.core.exceptions import PermissionDenied
from .models import User


class AuthenticationMiddleware:
    def raise_error(self, msg):
        error = {
            "error_code": status.HTTP_403_FORBIDDEN,
            "error_message": msg,
        }

        raise PermissionDenied(error)

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        exclusion_list = (
            '/',
            '/api/users/login/',
            '/api/users/registration/',
        )
        if request.path not in exclusion_list and not request.path.startswith('/admin/'):
            try:
                auth_header = request.headers.get('Authorization').split()
                token = auth_header[1]
                payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256', ])
                payload_id = payload.get('id')
                request.user = get_object_or_404(User, id=payload_id)

            except Exception:
                msg = 'The token is invalid or expired. '
                raise self.raise_error(msg)

            if not request.user.is_active:
                msg = 'This user has been deactivated.'
                raise self.raise_error(msg)

        return self.get_response(request)
