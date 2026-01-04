from django.db import models
from apps.schools.models import School
from apps.students.models import Student
from django.contrib.auth import get_user_model

User = get_user_model()

class PaymentMethod(models.Model):
    """Supported payment methods"""
    METHODS = [
        ('mpesa', 'M-Pesa'),
        ('airtel_money', 'Airtel Money'),
        ('card', 'Card Payment'),
        ('bank_transfer', 'Bank Transfer'),
        ('cash', 'Cash'),
        ('cheque', 'Cheque'),
    ]
    
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='payment_methods')
    name = models.CharField(max_length=20, choices=METHODS)
    is_active = models.BooleanField(default=True)
    min_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    max_amount = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    
    class Meta:
        db_table = 'payment_methods'
        unique_together = ['school', 'name']
    
    def __str__(self):
        return f"{self.school.name} - {self.get_name_display()}"

class Payment(models.Model):
    """Payment transactions"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    ]
    
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='payments')
    school = models.ForeignKey(School, on_delete=models.PROTECT)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    payment_method = models.ForeignKey(PaymentMethod, on_delete=models.PROTECT)
    reference_number = models.CharField(max_length=100, unique=True)
    mpesa_receipt = models.CharField(max_length=100, blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    paid_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='payments_made')
    transaction_id = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    confirmed_at = models.DateTimeField(blank=True, null=True)
    
    class Meta:
        db_table = 'payments'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.student.admission_number} - {self.amount} - {self.status}"

class Receipt(models.Model):
    """Digital Receipt"""
    payment = models.OneToOneField(Payment, on_delete=models.CASCADE, related_name='receipt')
    receipt_number = models.CharField(max_length=50, unique=True)
    issued_at = models.DateTimeField(auto_now_add=True)
    issued_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    is_void = models.BooleanField(default=False)
    void_reason = models.TextField(blank=True, null=True)
    
    class Meta:
        db_table = 'receipts'
    
    def __str__(self):
        return self.receipt_number
