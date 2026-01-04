from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Payment, PaymentMethod, Receipt
from .serializers import PaymentSerializer, PaymentMethodSerializer, ReceiptSerializer

class PaymentMethodViewSet(viewsets.ModelViewSet):
    """Payment method management"""
    queryset = PaymentMethod.objects.all()
    serializer_class = PaymentMethodSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['school', 'is_active']

class PaymentViewSet(viewsets.ModelViewSet):
    """Payment management"""
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['student', 'school', 'status', 'payment_method']
    search_fields = ['reference_number', 'mpesa_receipt', 'student__admission_number']
    
    def create(self, request, *args, **kwargs):
        """Initiate payment"""
        # TODO: Implement M-Pesa STK Push or payment gateway integration
        return super().create(request, *args, **kwargs)
    
    @action(detail=True, methods=['post'])
    def confirm(self, request, pk=None):
        """Confirm a payment"""
        payment = self.get_object()
        payment.status = 'confirmed'
        payment.confirmed_at = timezone.now()
        payment.save()
        return Response(PaymentSerializer(payment).data)

class ReceiptViewSet(viewsets.ModelViewSet):
    """Receipt management"""
    queryset = Receipt.objects.all()
    serializer_class = ReceiptSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['payment', 'is_void']
    search_fields = ['receipt_number']
    
    @action(detail=True, methods=['post'])
    def void(self, request, pk=None):
        """Void a receipt"""
        receipt = self.get_object()
        receipt.is_void = True
        receipt.void_reason = request.data.get('reason', '')
        receipt.save()
        return Response(ReceiptSerializer(receipt).data)

from django.utils import timezone
