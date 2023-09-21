from rest_framework import routers

from business.views import CurrencyViewSet, OrderViewSet

router = routers.SimpleRouter()
router.register(r'currency', CurrencyViewSet, basename='Currency')
router.register(r'order', OrderViewSet)

urlpatterns = router.urls
