from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import FeeCategoryViewSet, FeeStructureViewSet, FeeItemViewSet, StudentFeeViewSet

router = DefaultRouter()
router.register(r'categories', FeeCategoryViewSet, basename='fee-category')
router.register(r'structures', FeeStructureViewSet, basename='fee-structure')
router.register(r'items', FeeItemViewSet, basename='fee-item')
router.register(r'student-fees', StudentFeeViewSet, basename='student-fee')

urlpatterns = router.urls
