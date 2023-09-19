from django.urls import path
from rest_framework import routers

from .views import RegistrationAPIView

# router = routers.SimpleRouter()
# router.register(r'registration', RegistrationAPIView.as_view())

# urlpatterns = router.urls

urlpatterns = [
    path('registration', RegistrationAPIView.as_view())
]
