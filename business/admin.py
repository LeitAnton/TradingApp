from django.contrib import admin

from business.models import Currency, Order, History, Portfolio


class CurrencyAdmin(admin.ModelAdmin):
    """Admin configuration for the Currency model.

    This configuration defines how Currency objects are displayed in the Django admin interface.

    Attributes:
        list_display (tuple): The fields to display in the list view.
        search_fields (tuple): The fields to search for when using the search bar.

    """

    list_display = ('pk', 'title', 'symbol', 'quantity', 'price_per_quantity')
    search_fields = ('pk', 'title', 'symbol')


class OrderAdmin(admin.ModelAdmin):
    """Admin configuration for the Order model.

    This configuration defines how Order objects are displayed in the Django admin interface.

    Attributes:
        model (Order): The model associated with this admin configuration.
        fields (tuple): The fields to display and edit when viewing an Order object.
        search_fields (tuple): The fields to search for when using the search bar.
        list_filter (tuple): The fields to use for filtering in the list view.

    """

    model = Order
    fields = ('user', 'currency', 'action', 'quantity', 'price', 'match_price_per_currency_quantity')
    readonly_fields = ('user', 'currency', 'action', 'quantity', 'price', 'match_price_per_currency_quantity')
    search_fields = ('currency',)
    list_filter = ('action', 'currency')


class HistoryAdmin(admin.ModelAdmin):
    """Admin configuration for the Order model.

    This configuration defines how Order objects are displayed in the Django admin interface.

    Attributes:
        model (Order): The model associated with this admin configuration.
        fields (tuple): The fields to display and edit when viewing an Order object.
        search_fields (tuple): The fields to search for when using the search bar.
        list_filter (tuple): The fields to use for filtering in the list view.

    """

    model = History
    fields = ('user', 'currency', 'action', 'quantity', 'price', 'date_time',)
    search_fields = ('currency', 'user')
    readonly_fields = ('user', 'currency', 'action', 'quantity', 'price', 'date_time',)
    list_filter = ('action', 'currency')


admin.site.register(Currency, CurrencyAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(History, HistoryAdmin)
admin.site.register(Portfolio)
