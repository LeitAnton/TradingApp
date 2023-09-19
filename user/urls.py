from django.urls import path
from rest_framework import routers

from .views import LoginAPIView, RegistrationAPIView, UserRetrieveUpdateAPIView

# router = routers.SimpleRouter()
# router.register(r'registration', RegistrationAPIView.as_view())

# urlpatterns = router.urls

urlpatterns = [
    path('user', UserRetrieveUpdateAPIView.as_view()),
    path('users/', RegistrationAPIView.as_view()),
    path('users/login/', LoginAPIView.as_view()),
]
