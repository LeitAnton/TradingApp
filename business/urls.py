from rest_framework import routers

from business.views import CurrencyViewSet, OrderViewSet, SubscriptionViewSet, HistoryViewSet, PortfolioViewSet

router = routers.SimpleRouter()
router.register(r'currency', CurrencyViewSet, basename='Currency')
router.register(r'order', OrderViewSet)
router.register(r'subscription', SubscriptionViewSet)
router.register(r'history', HistoryViewSet)
router.register(r'portfolio', PortfolioViewSet)

urlpatterns = router.urls
