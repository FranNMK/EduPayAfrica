from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import (
    CountryViewSet, RegionViewSet, CountyViewSet, SchoolViewSet,
    AcademicYearViewSet, TermViewSet, SchoolClassViewSet, StreamViewSet
)

router = DefaultRouter()
router.register(r'countries', CountryViewSet, basename='country')
router.register(r'regions', RegionViewSet, basename='region')
router.register(r'counties', CountyViewSet, basename='county')
router.register(r'schools', SchoolViewSet, basename='school')
router.register(r'academic-years', AcademicYearViewSet, basename='academic-year')
router.register(r'terms', TermViewSet, basename='term')
router.register(r'classes', SchoolClassViewSet, basename='class')
router.register(r'streams', StreamViewSet, basename='stream')

urlpatterns = router.urls
