from rest_framework import permissions


class IsAnalystOrAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        try:
            if request.user.role in ['AN', 'AD']:
                return True

        except AttributeError:
            return False

        return False
