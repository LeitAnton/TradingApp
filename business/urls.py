from rest_framework import routers

from business.views import CurrencyViewSet, OrderViewSet, PortfolioViewSet, HistoryViewSet

router = routers.SimpleRouter()
router.register(r'currency', CurrencyViewSet, basename='Currency')
router.register(r'order', OrderViewSet)
router.register(r'portfolio', PortfolioViewSet)
router.register(r'history', HistoryViewSet)

urlpatterns = router.urls
