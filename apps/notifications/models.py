from django.db import models
from django.contrib.auth import get_user_model
from apps.schools.models import School

User = get_user_model()

class Notification(models.Model):
    """Notification model"""
    TYPES = [
        ('payment', 'Payment Notification'),
        ('announcement', 'School Announcement'),
        ('reminder', 'Fee Reminder'),
        ('system', 'System Notification'),
        ('alert', 'Alert'),
    ]
    
    CHANNELS = [
        ('sms', 'SMS'),
        ('email', 'Email'),
        ('whatsapp', 'WhatsApp'),
        ('in_app', 'In-App'),
        ('push', 'Push Notification'),
    ]
    
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='notifications')
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    notification_type = models.CharField(max_length=20, choices=TYPES)
    channel = models.CharField(max_length=20, choices=CHANNELS)
    subject = models.CharField(max_length=255)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    is_sent = models.BooleanField(default=False)
    sent_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'notifications'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.subject} - {self.recipient}"

class NotificationTemplate(models.Model):
    """Reusable notification templates"""
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='notification_templates')
    name = models.CharField(max_length=100)
    subject_template = models.CharField(max_length=255)
    body_template = models.TextField()
    variables = models.JSONField(default=list, blank=True)  # e.g., ['student_name', 'amount']
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'notification_templates'
    
    def __str__(self):
        return f"{self.school.name} - {self.name}"
