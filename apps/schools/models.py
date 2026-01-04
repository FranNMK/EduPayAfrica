from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import FileExtensionValidator

User = get_user_model()

class Country(models.Model):
    """Country master data"""
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=2, unique=True)
    currency = models.CharField(max_length=3)
    
    class Meta:
        db_table = 'countries'
    
    def __str__(self):
        return self.name

class Region(models.Model):
    """Region/State in a country"""
    country = models.ForeignKey(Country, on_delete=models.CASCADE, related_name='regions')
    name = models.CharField(max_length=100)
    
    class Meta:
        db_table = 'regions'
        unique_together = ['country', 'name']
    
    def __str__(self):
        return f"{self.name}, {self.country.name}"

class County(models.Model):
    """County/District in a region"""
    region = models.ForeignKey(Region, on_delete=models.CASCADE, related_name='counties')
    name = models.CharField(max_length=100)
    
    class Meta:
        db_table = 'counties'
        unique_together = ['region', 'name']
    
    def __str__(self):
        return f"{self.name}, {self.region.name}"

class School(models.Model):
    """School Registration Model"""
    INSTITUTION_TYPES = [
        ('primary', 'Primary School'),
        ('secondary', 'Secondary School'),
        ('university', 'University'),
        ('college', 'College'),
        ('tvet', 'TVET'),
    ]
    
    OWNERSHIP_TYPES = [
        ('public', 'Public'),
        ('private', 'Private'),
        ('international', 'International'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending Verification'),
        ('approved', 'Approved'),
        ('active', 'Active'),
        ('suspended', 'Suspended'),
        ('inactive', 'Inactive'),
    ]
    
    # Basic Information
    name = models.CharField(max_length=255)
    registration_number = models.CharField(max_length=100, unique=True)
    institution_type = models.CharField(max_length=20, choices=INSTITUTION_TYPES)
    ownership_type = models.CharField(max_length=20, choices=OWNERSHIP_TYPES)
    
    # Location Information
    country = models.ForeignKey(Country, on_delete=models.PROTECT)
    region = models.ForeignKey(Region, on_delete=models.PROTECT)
    county = models.ForeignKey(County, on_delete=models.PROTECT)
    physical_address = models.TextField()
    town_city = models.CharField(max_length=100)
    
    # Contact Information
    email = models.EmailField()
    phone_numbers = models.CharField(max_length=500, help_text="Comma-separated phone numbers")
    website = models.URLField(blank=True, null=True)
    social_media = models.JSONField(default=dict, blank=True)
    
    # Branding
    logo = models.ImageField(upload_to='school_logos/', validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png'])])
    primary_color = models.CharField(max_length=7, default='#000000')
    secondary_color = models.CharField(max_length=7, default='#FFFFFF')
    banner_image = models.ImageField(upload_to='school_banners/', blank=True, null=True)
    
    # Payment Configuration
    mpesa_paybill = models.CharField(max_length=20, blank=True, null=True)
    bank_account_name = models.CharField(max_length=100, blank=True, null=True)
    bank_account_number = models.CharField(max_length=50, blank=True, null=True)
    bank_name = models.CharField(max_length=100, blank=True, null=True)
    bank_swift = models.CharField(max_length=20, blank=True, null=True)
    
    # Documents
    registration_certificate = models.FileField(upload_to='school_documents/')
    tax_certificate = models.FileField(upload_to='school_documents/', blank=True, null=True)
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    admin = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='schools_as_admin')
    is_verified = models.BooleanField(default=False)
    verified_at = models.DateTimeField(blank=True, null=True)
    verified_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='verified_schools')
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'schools'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.name

class AcademicYear(models.Model):
    """Academic Year for a school"""
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='academic_years')
    year = models.CharField(max_length=9)  # e.g., "2023/2024"
    start_date = models.DateField()
    end_date = models.DateField()
    is_active = models.BooleanField(default=False)
    
    class Meta:
        db_table = 'academic_years'
        unique_together = ['school', 'year']
    
    def __str__(self):
        return f"{self.school.name} - {self.year}"

class Term(models.Model):
    """Term/Semester in an academic year"""
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE, related_name='terms')
    name = models.CharField(max_length=50)  # e.g., "Term 1"
    start_date = models.DateField()
    end_date = models.DateField()
    
    class Meta:
        db_table = 'terms'
        unique_together = ['academic_year', 'name']
    
    def __str__(self):
        return f"{self.academic_year.year} - {self.name}"

class SchoolClass(models.Model):
    """Class/Form/Year in a school"""
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='classes')
    name = models.CharField(max_length=100)
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE)
    capacity = models.IntegerField(default=50)
    class_teacher = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    
    class Meta:
        db_table = 'school_classes'
        unique_together = ['school', 'name', 'academic_year']
    
    def __str__(self):
        return f"{self.school.name} - {self.name}"

class Stream(models.Model):
    """Stream/Section within a class"""
    school_class = models.ForeignKey(SchoolClass, on_delete=models.CASCADE, related_name='streams')
    name = models.CharField(max_length=50)  # e.g., "A", "B", "C"
    capacity = models.IntegerField(default=50)
    
    class Meta:
        db_table = 'streams'
        unique_together = ['school_class', 'name']
    
    def __str__(self):
        return f"{self.school_class} - {self.name}"
