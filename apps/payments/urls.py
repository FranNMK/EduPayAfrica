from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import PaymentViewSet, PaymentMethodViewSet, ReceiptViewSet

router = DefaultRouter()
router.register(r'methods', PaymentMethodViewSet, basename='payment-method')
router.register(r'payments', PaymentViewSet, basename='payment')
router.register(r'receipts', ReceiptViewSet, basename='receipt')

urlpatterns = router.urls
