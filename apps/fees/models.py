from django.db import models
from apps.schools.models import School, SchoolClass, Term
from apps.students.models import Student

class FeeCategory(models.Model):
    """Fee categories (Tuition, Activity, etc)"""
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='fee_categories')
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    
    class Meta:
        db_table = 'fee_categories'
        unique_together = ['school', 'name']
    
    def __str__(self):
        return f"{self.school.name} - {self.name}"

class FeeStructure(models.Model):
    """Fee structure for a class"""
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='fee_structures')
    school_class = models.ForeignKey(SchoolClass, on_delete=models.CASCADE)
    term = models.ForeignKey(Term, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'fee_structures'
        unique_together = ['school_class', 'term']
    
    def __str__(self):
        return f"{self.school_class} - {self.term}"

class FeeItem(models.Model):
    """Individual fee items in a structure"""
    fee_structure = models.ForeignKey(FeeStructure, on_delete=models.CASCADE, related_name='items')
    category = models.ForeignKey(FeeCategory, on_delete=models.PROTECT)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    is_mandatory = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'fee_items'
        unique_together = ['fee_structure', 'category']
    
    def __str__(self):
        return f"{self.category.name} - {self.amount}"

class StudentFee(models.Model):
    """Fee charged to a student"""
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='fees')
    fee_structure = models.ForeignKey(FeeStructure, on_delete=models.CASCADE)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2)
    amount_paid = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    balance = models.DecimalField(max_digits=12, decimal_places=2)
    due_date = models.DateField()
    is_paid = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'student_fees'
    
    def __str__(self):
        return f"{self.student.admission_number} - {self.total_amount}"
