from rest_framework import permissions

from user.models import User


class IsAnalyst(permissions.BasePermission):
    """Permission class for checking if a user is an analyst.

    This permission class checks if the user's role is 'AN' (analyst) to grant access.

    """

    def has_permission(self, request, view):
        """Check if the user has permission.

        Args:
            request (Request): The HTTP request object.
            view: The view being accessed.

        Returns:
            bool: True if the user is an analyst, False otherwise.

        """
        try:
            if request.user.role == 'AN':
                return True

        except AttributeError:
            return False

        return False


class IsAnAuthor(permissions.BasePermission):
    """Permission class for checking if a user is an author.

    This permission class checks if the user is one of the authors of an object (e.g., a book).

    """

    def has_object_permission(self, request, view, obj):
        """Check if the user has permission to edit the object.

        Args:
            request (Request): The HTTP request object.
            view: The view being accessed.
            obj: The object being accessed (e.g., a book).

        Returns:
            bool: True if the user is one of the authors of the object, False otherwise.

        """
        if isinstance(obj, User):
            user_id = obj.id
        else:
            user_id = obj.user.id

        if request.user.id == user_id:
            return True

        return False
