from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from .models import School, Country, Region, County, AcademicYear, Term, SchoolClass, Stream
from .serializers import (
    SchoolSerializer, CountrySerializer, RegionSerializer, CountySerializer,
    SchoolRegistrationSerializer, AcademicYearSerializer, TermSerializer,
    SchoolClassSerializer, StreamSerializer
)

class CountryViewSet(viewsets.ReadOnlyModelViewSet):
    """Get list of countries"""
    queryset = Country.objects.all()
    serializer_class = CountrySerializer
    permission_classes = [AllowAny]

class RegionViewSet(viewsets.ReadOnlyModelViewSet):
    """Get regions for a country"""
    serializer_class = RegionSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['country']
    
    def get_queryset(self):
        country_id = self.request.query_params.get('country')
        if country_id:
            return Region.objects.filter(country_id=country_id)
        return Region.objects.all()

class CountyViewSet(viewsets.ReadOnlyModelViewSet):
    """Get counties for a region"""
    serializer_class = CountySerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['region']
    
    def get_queryset(self):
        region_id = self.request.query_params.get('region')
        if region_id:
            return County.objects.filter(region_id=region_id)
        return County.objects.all()

class SchoolViewSet(viewsets.ModelViewSet):
    """School management endpoints"""
    queryset = School.objects.all()
    serializer_class = SchoolSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'institution_type', 'country']
    search_fields = ['name', 'registration_number']
    ordering_fields = ['created_at', 'name']
    
    def get_queryset(self):
        user = self.request.user
        if user.role == 'super_admin':
            return School.objects.all()
        return School.objects.filter(admin=user)
    
    def create(self, request, *args, **kwargs):
        """School registration"""
        serializer = SchoolRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            school = serializer.save(admin=request.user, status='pending')
            return Response(
                SchoolSerializer(school).data,
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def verify(self, request, pk=None):
        """Verify a school (Super Admin only)"""
        if request.user.role != 'super_admin':
            return Response(
                {'error': 'Only super admin can verify schools'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        school = self.get_object()
        school.status = 'approved'
        school.is_verified = True
        school.verified_by = request.user
        from django.utils import timezone
        school.verified_at = timezone.now()
        school.save()
        
        return Response(SchoolSerializer(school).data)

class AcademicYearViewSet(viewsets.ModelViewSet):
    """Academic Year management"""
    queryset = AcademicYear.objects.all()
    serializer_class = AcademicYearSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['school', 'is_active']

class TermViewSet(viewsets.ModelViewSet):
    """Term management"""
    queryset = Term.objects.all()
    serializer_class = TermSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['academic_year']

class SchoolClassViewSet(viewsets.ModelViewSet):
    """School Class management"""
    queryset = SchoolClass.objects.all()
    serializer_class = SchoolClassSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['school', 'academic_year']

class StreamViewSet(viewsets.ModelViewSet):
    """Stream management"""
    queryset = Stream.objects.all()
    serializer_class = StreamSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['school_class']
