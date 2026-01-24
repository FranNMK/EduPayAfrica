from django.contrib import admin
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
    readonly_fields = ("created_at", "updated_at")


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ("full_name", "admission_number", "program", "academic_year", "is_active")
    list_filter = ("is_active", "institution", "program")
    search_fields = ("full_name", "admission_number", "email")
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
    list_display = ("full_name", "institution", "role", "email", "is_active")
    list_filter = ("role", "institution", "is_active", "date_hired")
    search_fields = ("full_name", "email", "institution__institution_name")
    readonly_fields = ("created_at", "updated_at", "date_hired")
    
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
