from datetime import datetime

from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from leads.models import DemoRequest
from .models import (
	AuditLog,
	Institution,
	InstitutionStatusLog,
	PlatformSetting,
	PlatformUserProfile,
	SystemStatus,
)


def _super_admin_check(user):
	return user.is_authenticated and user.is_active and user.is_staff and user.is_superuser


super_admin_required = user_passes_test(_super_admin_check)


@login_required
@super_admin_required
def dashboard(request):
	"""High-level overview for Super Admin."""

	institution_counts = Institution.objects.aggregate(
		total=Count("id"),
		pending=Count("id", filter=Q(status="pending")),
		approved=Count("id", filter=Q(status="approved")),
		active=Count("id", filter=Q(status="active")),
		suspended=Count("id", filter=Q(status="suspended")),
	)

	users_by_role = PlatformUserProfile.objects.values("role").annotate(total=Count("id"))
	demo_total = DemoRequest.objects.count()
	system_status, _ = SystemStatus.objects.get_or_create(id=1)

	context = {
		"institution_counts": institution_counts,
		"users_by_role": users_by_role,
		"demo_total": demo_total,
		"system_status": system_status,
	}
	return render(request, "platform_admin/dashboard.html", context)


@login_required
@super_admin_required
def institutions(request):
	"""View and govern institutions."""

	institutions_qs = Institution.objects.all().order_by("-created_at")

	if request.method == "POST":
		institution_id = request.POST.get("institution_id")
		action = request.POST.get("action")
		note = request.POST.get("note", "").strip()
		institution = get_object_or_404(Institution, pk=institution_id)
		previous_status = institution.status
		timestamp = timezone.now()

		if action == "approve":
			institution.status = "approved"
			institution.approval_timestamp = timestamp
			institution.registration_status = "approved"
		elif action == "activate":
			institution.status = "active"
			institution.activation_timestamp = timestamp
		elif action == "suspend":
			institution.status = "suspended"
			institution.suspension_timestamp = timestamp
		elif action == "deactivate":
			institution.status = "deactivated"
			institution.deactivation_timestamp = timestamp
		elif action == "reject":
			institution.status = "rejected"
			institution.rejection_timestamp = timestamp
		else:
			messages.error(request, "Unsupported action")
			return redirect("platform_admin:institutions")

		institution.save()
		InstitutionStatusLog.objects.create(
			institution=institution,
			action=action if action != "activate" else "activated",
			actor=request.user,
			note=note,
			previous_status=previous_status,
			new_status=institution.status,
		)
		AuditLog.record(
			action=f"Institution {action}",
			actor=request.user,
			entity_type="institution",
			entity_id=str(institution.id),
			description=note,
		)
		messages.success(request, f"Institution {institution.name} updated to {institution.get_status_display()}.")
		return redirect("platform_admin:institutions")

	context = {
		"institutions": institutions_qs,
	}
	return render(request, "platform_admin/institutions.html", context)


@login_required
@super_admin_required
def demo_requests(request):
	"""Read-only and status control for demo requests."""

	qs = DemoRequest.objects.all().order_by("-created_at")
	institution_type = request.GET.get("institution_type")
	status = request.GET.get("status")
	date_from = request.GET.get("from")
	date_to = request.GET.get("to")

	if institution_type:
		qs = qs.filter(institution_type=institution_type)
	if status:
		qs = qs.filter(status=status)
	if date_from:
		try:
			parsed = datetime.strptime(date_from, "%Y-%m-%d")
			qs = qs.filter(created_at__date__gte=parsed.date())
		except ValueError:
			messages.error(request, "Invalid start date")
	if date_to:
		try:
			parsed = datetime.strptime(date_to, "%Y-%m-%d")
			qs = qs.filter(created_at__date__lte=parsed.date())
		except ValueError:
			messages.error(request, "Invalid end date")

	if request.method == "POST":
		demo_id = request.POST.get("demo_id")
		new_status = request.POST.get("status")
		note = request.POST.get("note", "")
		demo = get_object_or_404(DemoRequest, pk=demo_id)
		previous_status = demo.status
		demo.status = new_status
		demo.notes = note or demo.notes
		demo.save()

		AuditLog.record(
			action="Demo request status updated",
			actor=request.user,
			entity_type="demo_request",
			entity_id=str(demo.id),
			description=f"{previous_status} -> {new_status}. {note}",
		)
		messages.success(request, "Demo request updated.")
		return redirect("platform_admin:demo_requests")

	context = {
		"demo_requests": qs,
	}
	return render(request, "platform_admin/demo_requests.html", context)


@login_required
@super_admin_required
def user_oversight(request):
	"""View users by role and toggle account status."""

	profiles = PlatformUserProfile.objects.select_related("user").all()

	if request.method == "POST":
		profile_id = request.POST.get("profile_id")
		action = request.POST.get("action")
		profile = get_object_or_404(PlatformUserProfile, pk=profile_id)
		user = profile.user
		if action == "disable":
			user.is_active = False
		elif action == "enable":
			user.is_active = True
		else:
			messages.error(request, "Unsupported action")
			return redirect("platform_admin:users")
		user.save()
		AuditLog.record(
			action=f"User {action}",
			actor=request.user,
			entity_type="user",
			entity_id=str(user.id),
			description=profile.notes,
		)
		messages.success(request, f"Account {user.get_username()} updated.")
		return redirect("platform_admin:users")

	context = {
		"profiles": profiles,
	}
	return render(request, "platform_admin/users.html", context)


@login_required
@super_admin_required
def settings_view(request):
	"""Manage platform-wide settings with audit logging."""

	settings_qs = PlatformSetting.objects.all().order_by("key")

	if request.method == "POST":
		key = request.POST.get("key", "").strip()
		value = request.POST.get("value", "")
		category = request.POST.get("category", "constant")
		description = request.POST.get("description", "")
		is_active = request.POST.get("is_active") == "on"

		if not key:
			messages.error(request, "Key is required")
			return redirect("platform_admin:settings")

		setting, _created = PlatformSetting.objects.update_or_create(
			key=key,
			defaults={
				"value": value,
				"category": category,
				"description": description,
				"is_active": is_active,
				"updated_by": request.user,
			},
		)
		AuditLog.record(
			action="Platform setting updated",
			actor=request.user,
			entity_type="setting",
			entity_id=setting.key,
			description=description,
		)
		messages.success(request, f"Setting {setting.key} saved.")
		return redirect("platform_admin:settings")

	context = {
		"settings": settings_qs,
	}
	return render(request, "platform_admin/settings.html", context)


@login_required
@super_admin_required
def audit_logs(request):
	"""Read-only audit log feed."""

	logs = AuditLog.objects.select_related("actor").all()
	return render(request, "platform_admin/audit_logs.html", {"logs": logs})
