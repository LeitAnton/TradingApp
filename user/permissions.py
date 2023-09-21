from rest_framework import permissions


class IsAnalyst(permissions.BasePermission):
    def has_permission(self, request, view):
        try:
            if request.user.role in 'AN':
                return True

        except AttributeError:
            return False

        return False
