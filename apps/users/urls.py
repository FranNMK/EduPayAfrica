from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import AuthViewSet, UserViewSet

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r'', AuthViewSet, basename='auth')

urlpatterns = router.urls
