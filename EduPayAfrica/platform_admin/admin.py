from django.contrib import admin

from .models import (
	AuditLog,
	Institution,
	InstitutionStatusLog,
	PlatformSetting,
	PlatformUserProfile,
	SystemStatus,
)


@admin.register(Institution)
class InstitutionAdmin(admin.ModelAdmin):
	list_display = ("name", "institution_type", "status", "contact_name", "created_at")
	list_filter = ("status", "institution_type")
	search_fields = ("name", "contact_name", "contact_email")


@admin.register(InstitutionStatusLog)
class InstitutionStatusLogAdmin(admin.ModelAdmin):
	list_display = ("institution", "action", "previous_status", "new_status", "created_at")
	list_filter = ("action",)
	search_fields = ("institution__name",)


@admin.register(PlatformUserProfile)
class PlatformUserProfileAdmin(admin.ModelAdmin):
	list_display = ("user", "role", "role_conflict", "created_at")
	list_filter = ("role", "role_conflict")
	search_fields = ("user__username", "user__email")


@admin.register(PlatformSetting)
class PlatformSettingAdmin(admin.ModelAdmin):
	list_display = ("key", "category", "is_active", "updated_at")
	list_filter = ("category", "is_active")
	search_fields = ("key",)


@admin.register(SystemStatus)
class SystemStatusAdmin(admin.ModelAdmin):
	list_display = ("is_operational", "message", "checked_at")


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
	list_display = ("action", "actor", "entity_type", "created_at")
	list_filter = ("entity_type",)
	search_fields = ("action", "entity_type", "entity_id")
