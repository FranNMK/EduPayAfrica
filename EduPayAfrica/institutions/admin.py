from django import forms
from django.contrib import admin
from django.forms import Select
from .models import (
    InstitutionProfile,
    AcademicYear,
    Term,
    Faculty,
    Program,
    Student,
    FeeStructure,
    FeeItem,
    StudentFeeAssignment,
    InstitutionAuditLog,
    InstitutionStaff,
    ParentGuardian,
    PrincipalMessage,
    FeeAnalysisSnapshot,
)


class ReadableSelectWidget(Select):
    """Custom select widget with proper styling to override Jazzmin theme."""
    
    def get_context(self, name, value, attrs):
        attrs = attrs or {}
        # Add classes and inline styles to make it visible
        attrs['class'] = attrs.get('class', '') + ' admin-select-readable'
        attrs['style'] = 'background-color: #ffffff !important; color: #000000 !important; border: 1px solid #ccc;'
        return super().get_context(name, value, attrs)


class StudentAdminForm(forms.ModelForm):
    """Filter program and academic year by selected institution on the fly."""

    class Meta:
        model = Student
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        institution = None

        # Apply custom widget with proper styling to dropdowns
        for name in ("institution", "program", "academic_year"):
            if name in self.fields:
                self.fields[name].widget = ReadableSelectWidget()

        if self.instance and self.instance.pk:
            institution = self.instance.institution

        if not institution:
            inst_id = self.data.get("institution") or self.initial.get("institution")
            if inst_id:
                try:
                    institution = InstitutionProfile.objects.get(pk=inst_id)
                except InstitutionProfile.DoesNotExist:
                    institution = None

        if institution:
            self.fields["program"].queryset = Program.objects.filter(institution=institution)
            self.fields["academic_year"].queryset = AcademicYear.objects.filter(institution=institution)


class InstitutionStaffAdminForm(forms.ModelForm):
    """Allow setting/updating the linked user's password while adding staff."""

    password1 = forms.CharField(
        label="Set/Update Password",
        widget=forms.PasswordInput,
        required=False,
        help_text="Leave blank to keep the current password."
    )
    password2 = forms.CharField(
        label="Confirm Password",
        widget=forms.PasswordInput,
        required=False,
    )

    class Meta:
        model = InstitutionStaff
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Apply custom widget to institution dropdown
        if "institution" in self.fields:
            self.fields["institution"].widget = ReadableSelectWidget()

    def clean(self):
        cleaned = super().clean()
        p1 = cleaned.get("password1")
        p2 = cleaned.get("password2")

        if p1 or p2:
            if p1 != p2:
                raise forms.ValidationError("Passwords do not match.")
            if p1 and len(p1) < 6:
                raise forms.ValidationError("Password must be at least 6 characters.")
        return cleaned

    def save(self, commit=True):
        staff = super().save(commit=False)
        p1 = self.cleaned_data.get("password1")
        if p1:
            staff.user.set_password(p1)
            staff.user.save()
        if commit:
            staff.save()
            self.save_m2m()
        return staff


@admin.register(InstitutionProfile)
class InstitutionProfileAdmin(admin.ModelAdmin):
    list_display = ("institution_name", "user", "contact_email", "is_active", "created_at")
    list_filter = ("is_active", "created_at")
    search_fields = ("institution_name", "user__email", "contact_email")
    readonly_fields = ("created_at", "updated_at")
    
    fieldsets = (
        ("Institution Details", {
            "fields": ("user", "institution_name", "institution_type")
        }),
        ("Contact Information", {
            "fields": ("contact_email", "phone_number", "address")
        }),
        ("Branding", {
            "fields": ("logo_url",)
        }),
        ("Status", {
            "fields": ("is_active",)
        }),
        ("Audit", {
            "fields": ("created_at", "updated_at"), "classes": ("collapse",)
        }),
    )


@admin.register(AcademicYear)
class AcademicYearAdmin(admin.ModelAdmin):
    list_display = ("year_code", "institution", "start_date", "end_date", "is_active")
    list_filter = ("is_active", "institution")
    search_fields = ("year_code", "institution__institution_name")
    readonly_fields = ("created_at", "updated_at")


@admin.register(Term)
class TermAdmin(admin.ModelAdmin):
    list_display = ("__str__", "academic_year", "term_number", "start_date", "end_date")
    list_filter = ("academic_year", "term_number")
    search_fields = ("term_name", "academic_year__year_code")
    readonly_fields = ("created_at", "updated_at")


@admin.register(Faculty)
class FacultyAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "institution", "is_active")
    list_filter = ("is_active", "institution")
    search_fields = ("name", "code", "institution__institution_name")
    readonly_fields = ("created_at", "updated_at")


@admin.register(Program)
class ProgramAdmin(admin.ModelAdmin):
    list_display = ("program_name", "program_code", "faculty", "program_type", "is_active")
    list_filter = ("is_active", "program_type", "faculty__institution")
    search_fields = ("program_name", "program_code", "faculty__name")
    autocomplete_fields = ("institution", "faculty")
    readonly_fields = ("created_at", "updated_at")


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    form = StudentAdminForm
    list_display = ("full_name", "admission_number", "program", "academic_year", "is_active")
    list_filter = ("is_active", "institution", "program")
    search_fields = ("full_name", "admission_number", "email")
    autocomplete_fields = ("institution", "program", "academic_year")
    readonly_fields = ("created_at", "updated_at")
    
    fieldsets = (
        ("Institution & Program", {
            "fields": ("institution", "program", "academic_year")
        }),
        ("Personal Information", {
            "fields": ("full_name", "admission_number", "email", "phone_number", "date_of_birth", "gender")
        }),
        ("Status", {
            "fields": ("is_active",)
        }),
        ("Audit", {
            "fields": ("created_at", "updated_at"), "classes": ("collapse",)
        }),
    )


@admin.register(FeeStructure)
class FeeStructureAdmin(admin.ModelAdmin):
    list_display = ("__str__", "institution", "version", "is_active", "created_at")
    list_filter = ("is_active", "institution")
    search_fields = ("institution__institution_name",)
    readonly_fields = ("created_at", "updated_at", "version")


@admin.register(FeeItem)
class FeeItemAdmin(admin.ModelAdmin):
    list_display = ("name", "fee_type", "amount", "is_mandatory", "fee_structure")
    list_filter = ("fee_type", "is_mandatory", "fee_structure")
    search_fields = ("name", "fee_structure__institution__institution_name")
    readonly_fields = ("created_at", "updated_at")


@admin.register(StudentFeeAssignment)
class StudentFeeAssignmentAdmin(admin.ModelAdmin):
    list_display = (
        "student",
        "academic_year",
        "total_fees",
        "outstanding_balance",
        "is_paid_in_full",
        "is_overdue",
    )
    list_filter = ("academic_year", "is_overdue", "created_at")
    search_fields = ("student__full_name", "student__admission_number")
    readonly_fields = ("created_at", "updated_at", "outstanding_balance", "is_paid_in_full")


@admin.register(InstitutionAuditLog)
class InstitutionAuditLogAdmin(admin.ModelAdmin):
    list_display = ("institution", "action", "actor", "created_at")
    list_filter = ("action", "institution", "created_at")
    search_fields = ("institution__institution_name", "actor__email", "description")
    readonly_fields = ("created_at", "institution", "actor", "action", "description", "changes")


@admin.register(InstitutionStaff)
class InstitutionStaffAdmin(admin.ModelAdmin):
    form = InstitutionStaffAdminForm
    list_display = ("full_name", "institution", "role", "email", "is_active")
    list_filter = ("role", "institution", "is_active", "date_hired")
    search_fields = ("full_name", "email", "institution__institution_name")
    readonly_fields = ("created_at", "updated_at", "date_hired")
    autocomplete_fields = ("institution", "user")
    fieldsets = (
        ("Staff Information", {
            "fields": ("institution", "user", "full_name", "role")
        }),
        ("Contact", {
            "fields": ("email", "phone_number")
        }),
        ("Status", {
            "fields": ("is_active", "date_hired")
        }),
        ("Audit", {
            "fields": ("created_at", "updated_at"), "classes": ("collapse",)
        }),
    )


@admin.register(ParentGuardian)
class ParentGuardianAdmin(admin.ModelAdmin):
    list_display = ("full_name", "student", "relationship", "is_primary_contact")
    list_filter = ("relationship", "is_primary_contact")
    search_fields = ("full_name", "student__full_name", "email", "phone_number")
    readonly_fields = ("created_at", "updated_at")


@admin.register(PrincipalMessage)
class PrincipalMessageAdmin(admin.ModelAdmin):
    list_display = ("subject", "message_type", "institution", "sent_by", "sent_date")
    list_filter = ("message_type", "institution", "sent_date")
    search_fields = ("subject", "content", "institution__institution_name")
    readonly_fields = ("sent_date", "created_at", "updated_at")
    filter_horizontal = ("target_students",)


@admin.register(FeeAnalysisSnapshot)
class FeeAnalysisSnapshotAdmin(admin.ModelAdmin):
    list_display = ("institution", "snapshot_date", "total_students", "collection_rate")
    list_filter = ("institution", "snapshot_date")
    search_fields = ("institution__institution_name",)
    readonly_fields = ("created_at", "snapshot_date")
