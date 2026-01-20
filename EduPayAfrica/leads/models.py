from django.db import models
from django.utils import timezone

class DemoRequest(models.Model):
    """Model for storing demo booking requests from institutions"""
    
    INSTITUTION_TYPES = [
        ('university', 'University'),
        ('college', 'College'),
        ('secondary_school', 'Secondary School'),
        ('primary_school', 'Primary School'),
        ('vocational', 'Vocational/Technical Institution'),
        ('other', 'Other'),
    ]
    
    STUDENT_COUNT_CHOICES = [
        ('below_100', 'Below 100'),
        ('100_500', '100 - 500'),
        ('500_1000', '500 - 1,000'),
        ('1000_5000', '1,000 - 5,000'),
        ('5000_above', '5,000+'),
    ]
    
    CHALLENGE_CHOICES = [
        ('manual_collection', 'Manual fee collection processes'),
        ('tracking', 'Tracking payments and balances'),
        ('reconciliation', 'Payment reconciliation'),
        ('communication', 'Communication with students/parents'),
        ('multiple_systems', 'Multiple disconnected systems'),
        ('security', 'Data security and protection'),
        ('reporting', 'Financial reporting'),
        ('other_challenge', 'Other challenge'),
    ]
    
    TIME_PREFERENCE_CHOICES = [
        ('morning', 'Morning (8:00 AM - 12:00 PM)'),
        ('afternoon', 'Afternoon (12:00 PM - 4:00 PM)'),
        ('evening', 'Evening (4:00 PM - 6:00 PM)'),
        ('flexible', 'I\'m flexible'),
    ]
    
    # Personal Information
    full_name = models.CharField(max_length=255)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    job_title = models.CharField(max_length=255)
    
    # Institution Information
    institution_name = models.CharField(max_length=255)
    institution_type = models.CharField(max_length=50, choices=INSTITUTION_TYPES)
    student_count = models.CharField(max_length=50, choices=STUDENT_COUNT_CHOICES)
    country = models.CharField(max_length=100)
    
    # Additional Information
    challenge = models.CharField(max_length=100, choices=CHALLENGE_CHOICES)
    message = models.TextField(blank=True, null=True)
    preferred_time = models.CharField(max_length=50, choices=TIME_PREFERENCE_CHOICES)
    include_team = models.BooleanField(default=False)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(
        max_length=50,
        default='pending',
        choices=[
            ('pending', 'Pending'),
            ('scheduled', 'Scheduled'),
            ('completed', 'Completed'),
            ('cancelled', 'Cancelled'),
        ]
    )
    notes = models.TextField(blank=True, null=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Demo Request'
        verbose_name_plural = 'Demo Requests'
    
    def __str__(self):
        return f"{self.full_name} - {self.institution_name} ({self.created_at.strftime('%Y-%m-%d')})"
