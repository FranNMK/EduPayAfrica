from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import StudentViewSet, ParentViewSet

router = DefaultRouter()
router.register(r'students', StudentViewSet, basename='student')
router.register(r'parents', ParentViewSet, basename='parent')

urlpatterns = router.urls
