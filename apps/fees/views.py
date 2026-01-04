from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import FeeCategory, FeeStructure, FeeItem, StudentFee
from .serializers import FeeCategorySerializer, FeeStructureSerializer, FeeItemSerializer, StudentFeeSerializer

class FeeCategoryViewSet(viewsets.ModelViewSet):
    """Fee category management"""
    queryset = FeeCategory.objects.all()
    serializer_class = FeeCategorySerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['school']

class FeeStructureViewSet(viewsets.ModelViewSet):
    """Fee structure management"""
    queryset = FeeStructure.objects.all()
    serializer_class = FeeStructureSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['school', 'school_class', 'term']

class FeeItemViewSet(viewsets.ModelViewSet):
    """Fee item management"""
    queryset = FeeItem.objects.all()
    serializer_class = FeeItemSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['fee_structure', 'category']

class StudentFeeViewSet(viewsets.ModelViewSet):
    """Student fee management"""
    queryset = StudentFee.objects.all()
    serializer_class = StudentFeeSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['student', 'fee_structure', 'is_paid']
    search_fields = ['student__admission_number']
