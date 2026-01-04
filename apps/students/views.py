from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Student, Parent
from .serializers import StudentSerializer, ParentSerializer

class ParentViewSet(viewsets.ModelViewSet):
    """Parent management"""
    queryset = Parent.objects.all()
    serializer_class = ParentSerializer
    permission_classes = [IsAuthenticated]

class StudentViewSet(viewsets.ModelViewSet):
    """Student management"""
    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['school', 'school_class', 'is_active']
    search_fields = ['admission_number', 'first_name', 'last_name']
    
    @action(detail=False, methods=['post'])
    def bulk_upload(self, request):
        """Bulk upload students via CSV"""
        # TODO: Implement CSV upload functionality
        return Response({'message': 'Bulk upload endpoint - to be implemented'})
