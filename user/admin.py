from django.contrib import admin

from user.models import User


class UserAdmin(admin.ModelAdmin):
    """Custom admin configuration for the User model.

    This admin configuration defines how User model instances are displayed and filtered in the admin interface.

    Attributes:
        list_display (tuple): A tuple of fields to display in the list view of User model instances.
        search_fields (tuple): A tuple of fields to enable searching in the admin interface.
        list_filter (tuple): A tuple of fields to enable filtering in the admin interface.
        list_editable (tuple): A tuple of fields that can be edited directly in the list view.

    """

    list_display = ('pk', 'username', 'role', 'balance')
    readonly_fields = ('username', 'password', 'token', 'email')
    search_fields = ('username',)
    list_filter = ('role',)
    list_editable = ('role',)


admin.site.register(User, UserAdmin)
