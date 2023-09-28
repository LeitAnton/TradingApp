from rest_framework import routers

from business.views import CurrencyViewSet, OrderViewSet, PortfolioViewSet

router = routers.SimpleRouter()
router.register(r'currency', CurrencyViewSet, basename='Currency')
router.register(r'order', OrderViewSet)
router.register(r'portfolio', PortfolioViewSet)

urlpatterns = router.urls
