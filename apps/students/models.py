from django.db import models
from django.contrib.auth import get_user_model
from apps.schools.models import School, SchoolClass, Stream

User = get_user_model()

class Parent(models.Model):
    """Parent/Guardian model"""
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=20)
    occupation = models.CharField(max_length=100, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    
    class Meta:
        db_table = 'parents'
    
    def __str__(self):
        return f"{self.user.get_full_name()}"

class Student(models.Model):
    """Student model"""
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='students')
    admission_number = models.CharField(max_length=50)
    first_name = models.CharField(max_length=100)
    middle_name = models.CharField(max_length=100, blank=True, null=True)
    last_name = models.CharField(max_length=100)
    date_of_birth = models.DateField()
    gender = models.CharField(max_length=1, choices=[('M', 'Male'), ('F', 'Female'), ('O', 'Other')])
    national_id = models.CharField(max_length=50, blank=True, null=True)
    photo = models.ImageField(upload_to='student_photos/', blank=True, null=True)
    
    # Enrollment
    enrollment_date = models.DateField()
    school_class = models.ForeignKey(SchoolClass, on_delete=models.PROTECT, related_name='students')
    stream = models.ForeignKey(Stream, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Parent/Guardian Info
    primary_parent = models.ForeignKey(Parent, on_delete=models.SET_NULL, null=True, related_name='children_as_primary')
    secondary_parent = models.ForeignKey(Parent, on_delete=models.SET_NULL, null=True, blank=True, related_name='children_as_secondary')
    
    # Medical Info
    allergies = models.TextField(blank=True, null=True)
    chronic_conditions = models.TextField(blank=True, null=True)
    special_needs = models.TextField(blank=True, null=True)
    doctor_contact = models.CharField(max_length=20, blank=True, null=True)
    
    # Status
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'students'
        unique_together = ['school', 'admission_number']
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.admission_number})"
