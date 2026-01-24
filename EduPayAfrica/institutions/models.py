from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.utils import timezone

User = get_user_model()


class InstitutionProfile(models.Model):
    """Institution-level profile and operational details."""

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="institution_profile")
    institution_name = models.CharField(max_length=255)  # Immutable after approval
    institution_type = models.CharField(max_length=50)  # Immutable after approval
    
    # Operational details (mutable)
    contact_email = models.EmailField()
    phone_number = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    logo_url = models.URLField(blank=True, null=True)
    
    # Status
    is_active = models.BooleanField(default=True)
    
    # Audit
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Institution Profile"
        verbose_name_plural = "Institution Profiles"

    def __str__(self):
        return f"{self.institution_name} ({self.user.email})"


class AcademicYear(models.Model):
    """Academic years managed by Institution Admin."""

    institution = models.ForeignKey(
        InstitutionProfile, on_delete=models.CASCADE, related_name="academic_years"
    )
    year_code = models.CharField(max_length=20)  # e.g., "2025/2026"
    start_date = models.DateField()
    end_date = models.DateField()
    is_active = models.BooleanField(default=False)
    
    # Audit
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("institution", "year_code")
        ordering = ["-start_date"]
        verbose_name = "Academic Year"
        verbose_name_plural = "Academic Years"

    def __str__(self):
        return f"{self.institution.institution_name} - {self.year_code}"

    def clean(self):
        """Ensure academic years don't overlap."""
        from django.core.exceptions import ValidationError
        
        overlapping = AcademicYear.objects.filter(
            institution=self.institution,
            start_date__lt=self.end_date,
            end_date__gt=self.start_date,
        ).exclude(pk=self.pk)
        
        if overlapping.exists():
            raise ValidationError("Academic year overlaps with an existing year.")


class Term(models.Model):
    """Terms/semesters within an academic year."""

    TERM_CHOICES = [
        (1, "Term 1"),
        (2, "Term 2"),
        (3, "Term 3"),
    ]

    academic_year = models.ForeignKey(
        AcademicYear, on_delete=models.CASCADE, related_name="terms"
    )
    term_number = models.IntegerField(choices=TERM_CHOICES)
    term_name = models.CharField(max_length=100, blank=True)  # e.g., "First Semester"
    start_date = models.DateField()
    end_date = models.DateField()
    
    # Audit
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("academic_year", "term_number")
        ordering = ["term_number"]
        verbose_name = "Term"
        verbose_name_plural = "Terms"

    def __str__(self):
        return f"{self.academic_year.year_code} - Term {self.term_number}"


class Faculty(models.Model):
    """Faculties/Schools within an institution."""

    institution = models.ForeignKey(
        InstitutionProfile, on_delete=models.CASCADE, related_name="faculties"
    )
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=50)
    description = models.TextField(blank=True)
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("institution", "code")
        verbose_name = "Faculty"
        verbose_name_plural = "Faculties"

    def __str__(self):
        return f"{self.institution.institution_name} - {self.name}"


class Program(models.Model):
    """Academic Programs (Courses) with modular/non-modular options."""

    PROGRAM_TYPE_CHOICES = [
        ("modular", "Modular"),
        ("non_modular", "Non-Modular"),
        ("semester", "Semester-Based"),
        ("year_round", "Year Round"),
    ]

    institution = models.ForeignKey(
        InstitutionProfile, on_delete=models.CASCADE, related_name="programs"
    )
    faculty = models.ForeignKey(Faculty, on_delete=models.CASCADE, related_name="programs_rel")
    program_name = models.CharField(max_length=255)
    program_code = models.CharField(max_length=50)
    program_type = models.CharField(max_length=50, choices=PROGRAM_TYPE_CHOICES, default="non_modular")
    duration_months = models.IntegerField(default=12, validators=[MinValueValidator(1)])
    description = models.TextField(blank=True)
    
    # Status
    is_active = models.BooleanField(default=True)
    
    # Audit
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("institution", "program_code")
        ordering = ["program_name"]
        verbose_name = "Program"
        verbose_name_plural = "Programs"

    def __str__(self):
        return f"{self.program_name} ({self.get_program_type_display()})"


class Student(models.Model):
    """Student records (no authentication yet)."""

    institution = models.ForeignKey(
        InstitutionProfile, on_delete=models.CASCADE, related_name="students"
    )
    program = models.ForeignKey(Program, on_delete=models.SET_NULL, null=True)
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.SET_NULL, null=True)
    
    full_name = models.CharField(max_length=255)
    admission_number = models.CharField(max_length=50)
    email = models.EmailField(blank=True)
    phone_number = models.CharField(max_length=20, blank=True)
    
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(
        max_length=10,
        choices=[("M", "Male"), ("F", "Female"), ("Other", "Other")],
        blank=True,
    )
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("institution", "admission_number")
        verbose_name = "Student"
        verbose_name_plural = "Students"

    def __str__(self):
        return f"{self.full_name} ({self.admission_number})"


class FeeStructure(models.Model):
    """Fee structure definition (versioned)."""

    institution = models.ForeignKey(
        InstitutionProfile, on_delete=models.CASCADE, related_name="fee_structures"
    )
    version = models.IntegerField(default=1)
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("institution", "version")
        ordering = ["-version"]
        verbose_name = "Fee Structure"
        verbose_name_plural = "Fee Structures"

    def __str__(self):
        return f"{self.institution.institution_name} - Version {self.version}"


class FeeItem(models.Model):
    """Individual fee items (tuition, accommodation, etc.)."""

    FEE_ITEM_TYPES = [
        ("tuition", "Tuition"),
        ("accommodation", "Accommodation"),
        ("lab_fees", "Lab Fees"),
        ("library", "Library"),
        ("activity", "Activity Fee"),
        ("technology", "Technology Fee"),
        ("other", "Other"),
    ]

    fee_structure = models.ForeignKey(
        FeeStructure, on_delete=models.CASCADE, related_name="fee_items"
    )
    name = models.CharField(max_length=255)
    fee_type = models.CharField(max_length=50, choices=FEE_ITEM_TYPES)
    amount = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0)])
    
    is_mandatory = models.BooleanField(default=True)
    description = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Fee Item"
        verbose_name_plural = "Fee Items"

    def __str__(self):
        return f"{self.name} ({self.fee_structure})"


class StudentFeeAssignment(models.Model):
    """Assigns fees to individual students (accounting entry)."""

    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="fee_assignments")
    fee_structure = models.ForeignKey(FeeStructure, on_delete=models.PROTECT)
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.PROTECT)
    term = models.ForeignKey(Term, on_delete=models.SET_NULL, null=True, blank=True)
    
    total_fees = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    discount_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    penalty_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    amount_paid = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    due_date = models.DateField(null=True, blank=True)
    is_overdue = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("student", "fee_structure", "academic_year", "term")
        verbose_name = "Student Fee Assignment"
        verbose_name_plural = "Student Fee Assignments"

    def __str__(self):
        return f"{self.student.full_name} - {self.academic_year.year_code}"

    @property
    def outstanding_balance(self):
        """Calculate outstanding balance."""
        return self.total_fees - self.discount_amount + self.penalty_amount - self.amount_paid

    @property
    def is_paid_in_full(self):
        """Check if fees are paid in full."""
        return self.outstanding_balance <= 0

    def update_overdue_status(self):
        """Update overdue status based on due date."""
        if self.due_date and self.due_date < timezone.now().date():
            if not self.is_paid_in_full:
                self.is_overdue = True
                self.save()


class InstitutionAuditLog(models.Model):
    """Audit log for institution-level activities."""

    ACTION_CHOICES = [
        ("user_created", "User Created"),
        ("user_deactivated", "User Deactivated"),
        ("fee_structure_changed", "Fee Structure Changed"),
        ("student_added", "Student Added"),
        ("fee_assigned", "Fee Assigned"),
        ("institution_updated", "Institution Updated"),
        ("academic_year_created", "Academic Year Created"),
        ("term_created", "Term Created"),
    ]

    institution = models.ForeignKey(
        InstitutionProfile, on_delete=models.CASCADE, related_name="audit_logs"
    )
    actor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    action = models.CharField(max_length=100, choices=ACTION_CHOICES)
    
    entity_type = models.CharField(max_length=100, blank=True)
    entity_id = models.CharField(max_length=100, blank=True)
    
    description = models.TextField(blank=True)
    changes = models.JSONField(null=True, blank=True)  # Stores before/after data
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Institution Audit Log"
        verbose_name_plural = "Institution Audit Logs"

    def __str__(self):
        return f"{self.institution.institution_name} - {self.action} @ {self.created_at}"


class InstitutionStaff(models.Model):
    """Staff members at institution with roles and permissions."""

    ROLE_CHOICES = [
        ("admin", "Institution Admin"),
        ("principal", "Principal"),
        ("deputy_principal", "Deputy Principal"),
        ("bursar", "Bursar/Finance Officer"),
        ("teacher", "Teacher"),
        ("accountant", "Accountant"),
        ("registrar", "Registrar"),
        ("support_staff", "Support Staff"),
    ]

    institution = models.ForeignKey(
        InstitutionProfile, on_delete=models.CASCADE, related_name="staff"
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="staff_roles")
    full_name = models.CharField(max_length=255)
    role = models.CharField(max_length=50, choices=ROLE_CHOICES)
    email = models.EmailField()
    phone_number = models.CharField(max_length=20, blank=True)
    
    # Status
    is_active = models.BooleanField(default=True)
    date_hired = models.DateField(auto_now_add=True)
    
    # Audit
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("institution", "user")
        verbose_name = "Institution Staff"
        verbose_name_plural = "Institution Staff"

    def __str__(self):
        return f"{self.full_name} ({self.get_role_display()}) - {self.institution.institution_name}"


class ParentGuardian(models.Model):
    """Parent/Guardian contacts for students."""

    RELATIONSHIP_CHOICES = [
        ("parent", "Parent"),
        ("guardian", "Guardian"),
        ("uncle_aunt", "Uncle/Aunt"),
        ("grandparent", "Grandparent"),
    ]

    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="parents")
    full_name = models.CharField(max_length=255)
    relationship = models.CharField(max_length=50, choices=RELATIONSHIP_CHOICES)
    email = models.EmailField(blank=True)
    phone_number = models.CharField(max_length=20)
    is_primary_contact = models.BooleanField(default=False)
    
    # Audit
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Parent/Guardian"
        verbose_name_plural = "Parents/Guardians"

    def __str__(self):
        return f"{self.full_name} ({self.get_relationship_display()}) - {self.student.full_name}"


class PrincipalMessage(models.Model):
    """Messages sent by principal to parents about fees."""

    MESSAGE_TYPE_CHOICES = [
        ("reminder", "Fee Reminder"),
        ("urgent", "Urgent Payment Required"),
        ("announcement", "General Announcement"),
        ("congratulation", "Congratulations"),
    ]

    institution = models.ForeignKey(
        InstitutionProfile, on_delete=models.CASCADE, related_name="messages"
    )
    sent_by = models.ForeignKey(InstitutionStaff, on_delete=models.SET_NULL, null=True)
    subject = models.CharField(max_length=255)
    message_type = models.CharField(max_length=50, choices=MESSAGE_TYPE_CHOICES)
    content = models.TextField()
    
    # Targeting
    target_students = models.ManyToManyField(Student, related_name="messages")
    
    # Status
    is_active = models.BooleanField(default=True)
    sent_date = models.DateTimeField(auto_now_add=True)
    
    # Audit
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-sent_date"]
        verbose_name = "Principal Message"
        verbose_name_plural = "Principal Messages"

    def __str__(self):
        return f"{self.subject} - {self.institution.institution_name}"


class FeeAnalysisSnapshot(models.Model):
    """Daily snapshot of fee collection for analysis."""


    institution = models.ForeignKey(
        InstitutionProfile, on_delete=models.CASCADE, related_name="fee_snapshots"
    )
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE)
    
    # Metrics
    total_students = models.IntegerField()
    total_fees_billed = models.DecimalField(max_digits=15, decimal_places=2)
    total_fees_paid = models.DecimalField(max_digits=15, decimal_places=2)
    total_outstanding = models.DecimalField(max_digits=15, decimal_places=2)
    overdue_count = models.IntegerField()
    fully_paid_count = models.IntegerField()
    partially_paid_count = models.IntegerField()
    not_paid_count = models.IntegerField()
    
    # Analysis
    collection_rate = models.DecimalField(max_digits=5, decimal_places=2)  # Percentage
    average_fee_per_student = models.DecimalField(max_digits=15, decimal_places=2)
    
    # Audit
    snapshot_date = models.DateField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-snapshot_date"]
        verbose_name = "Fee Analysis Snapshot"
        verbose_name_plural = "Fee Analysis Snapshots"

    def __str__(self):
        return f"{self.institution.institution_name} - {self.snapshot_date}"
