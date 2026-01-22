from django.db import models
from django.conf import settings
from django.utils import timezone
from django.contrib.auth import get_user_model

User = get_user_model()


class Institution(models.Model):
	"""Institution record managed by Super Admin."""

	TYPE_CHOICES = [
		("university", "University"),
		("college", "College"),
		("secondary_school", "Secondary School"),
		("primary_school", "Primary School"),
		("vocational", "Vocational/Technical Institution"),
		("other", "Other"),
	]

	STATUS_CHOICES = [
		("pending", "Pending"),
		("approved", "Approved"),
		("rejected", "Rejected"),
		("active", "Active"),
		("suspended", "Suspended"),
		("deactivated", "Deactivated"),
	]

	name = models.CharField(max_length=255)
	institution_type = models.CharField(max_length=50, choices=TYPE_CHOICES)
	contact_name = models.CharField(max_length=255)
	contact_email = models.EmailField()
	contact_phone = models.CharField(max_length=50, blank=True)
	status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
	registration_status = models.CharField(max_length=50, default="pending")
	approval_timestamp = models.DateTimeField(null=True, blank=True)
	activation_timestamp = models.DateTimeField(null=True, blank=True)
	suspension_timestamp = models.DateTimeField(null=True, blank=True)
	deactivation_timestamp = models.DateTimeField(null=True, blank=True)
	rejection_timestamp = models.DateTimeField(null=True, blank=True)
	onboarding_notes = models.TextField(blank=True)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		ordering = ["-created_at"]
		verbose_name = "Institution"
		verbose_name_plural = "Institutions"

	def __str__(self):
		return f"{self.name} ({self.get_status_display()})"


class InstitutionStatusLog(models.Model):
	"""History of institution lifecycle actions."""

	ACTION_CHOICES = [
		("approved", "Approved"),
		("rejected", "Rejected"),
		("activated", "Activated"),
		("suspended", "Suspended"),
		("reinstated", "Reinstated"),
		("deactivated", "Deactivated"),
		("updated", "Updated"),
	]

	institution = models.ForeignKey(Institution, on_delete=models.CASCADE, related_name="status_logs")
	action = models.CharField(max_length=20, choices=ACTION_CHOICES)
	actor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
	note = models.TextField(blank=True)
	previous_status = models.CharField(max_length=20, blank=True)
	new_status = models.CharField(max_length=20, blank=True)
	created_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		ordering = ["-created_at"]
		verbose_name = "Institution Status Log"
		verbose_name_plural = "Institution Status Logs"

	def __str__(self):
		return f"{self.institution.name} - {self.action} @ {self.created_at.strftime('%Y-%m-%d %H:%M')}"


class PlatformUserProfile(models.Model):
	"""Role metadata for Django users to support Super Admin oversight."""

	ROLE_CHOICES = [
		("super_admin", "Super Admin"),
		("institution_admin", "Institution Admin"),
		("bursar", "Bursar"),
		("parent", "Parent"),
		("other", "Other"),
	]

	user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="platform_profile")
	role = models.CharField(max_length=50, choices=ROLE_CHOICES, default="other")
	role_conflict = models.BooleanField(default=False)
	notes = models.TextField(blank=True)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		verbose_name = "Platform User Profile"
		verbose_name_plural = "Platform User Profiles"

	def __str__(self):
		return f"{self.user.get_username()} ({self.get_role_display()})"

	@property
	def account_status(self):
		return "Active" if self.user.is_active else "Disabled"


class PlatformSetting(models.Model):
	"""Global configuration managed by Super Admin."""

	CATEGORY_CHOICES = [
		("institution_type", "Institution Types"),
		("academic_year", "Academic Year"),
		("feature_flag", "Feature Flag"),
		("email_template", "Email Template"),
		("constant", "System Constant"),
	]

	key = models.CharField(max_length=100, unique=True)
	value = models.TextField()
	category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
	is_active = models.BooleanField(default=True)
	description = models.TextField(blank=True)
	updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		verbose_name = "Platform Setting"
		verbose_name_plural = "Platform Settings"

	def __str__(self):
		return f"{self.key} ({self.get_category_display()})"


class SystemStatus(models.Model):
	"""Operational status indicator for the platform."""

	is_operational = models.BooleanField(default=True)
	message = models.CharField(max_length=255, default="Operational")
	checked_at = models.DateTimeField(auto_now=True)
	updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

	class Meta:
		verbose_name = "System Status"
		verbose_name_plural = "System Status"

	def __str__(self):
		state = "Operational" if self.is_operational else "Degraded"
		return f"{state} - {self.checked_at.strftime('%Y-%m-%d %H:%M')}"


class AuditLog(models.Model):
	"""Immutable audit log capturing Super Admin actions."""

	action = models.CharField(max_length=255)
	actor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
	entity_type = models.CharField(max_length=100, blank=True)
	entity_id = models.CharField(max_length=100, blank=True)
	description = models.TextField(blank=True)
	created_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		ordering = ["-created_at"]
		verbose_name = "Audit Log"
		verbose_name_plural = "Audit Logs"

	def __str__(self):
		return f"{self.action} @ {self.created_at.strftime('%Y-%m-%d %H:%M')}"

	@classmethod
	def record(cls, action: str, actor: User | None, entity_type: str = "", entity_id: str = "", description: str = ""):
		"""Helper to create a log entry while keeping logs immutable."""
		cls.objects.create(
			action=action,
			actor=actor,
			entity_type=entity_type,
			entity_id=entity_id,
			description=description,
		)
