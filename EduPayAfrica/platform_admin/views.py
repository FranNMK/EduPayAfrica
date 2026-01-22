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
	"""View and approve demo requests from institutions."""

	qs = DemoRequest.objects.all().order_by("-timestamp")
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
			qs = qs.filter(timestamp__date__gte=parsed.date())
		except ValueError:
			messages.error(request, "Invalid start date")
	if date_to:
		try:
			parsed = datetime.strptime(date_to, "%Y-%m-%d")
			qs = qs.filter(timestamp__date__lte=parsed.date())
		except ValueError:
			messages.error(request, "Invalid end date")

	if request.method == "POST":
		action = request.POST.get("action")
		demo_id = request.POST.get("demo_id")
		demo = get_object_or_404(DemoRequest, pk=demo_id)
		
		if action == "approve":
			# Create new institution from demo request
			admin_user_id = request.POST.get("admin_user")
			onboarding_notes = request.POST.get("onboarding_notes", "")
			
			if not admin_user_id:
				messages.error(request, "Please select an admin user to assign.")
				return redirect("platform_admin:demo_requests")
			
			try:
				from django.contrib.auth.models import User
				admin_user = User.objects.get(pk=admin_user_id)
			except User.DoesNotExist:
				messages.error(request, "Selected admin user not found.")
				return redirect("platform_admin:demo_requests")
			
			# Create institution record
			institution = Institution.objects.create(
				name=demo.institution_name,
				institution_type=demo.institution_type,
				contact_name=demo.full_name,
				contact_email=demo.email,
				contact_phone=demo.phone,
				status="pending",
				onboarding_notes=onboarding_notes,
			)
			
			# Create relationship to admin user
			PlatformUserProfile.objects.get_or_create(
				user=admin_user,
				defaults={
					'role': 'admin',
					'institution': institution,
					'is_active': True,
				}
			)
			
			# Record status log
			InstitutionStatusLog.objects.create(
				institution=institution,
				from_status="draft",
				to_status="pending",
				changed_by=request.user,
				reason="Created from demo request approval"
			)
			
			# Record audit log
			AuditLog.record(
				action="Demo request approved and institution created",
				actor=request.user,
				entity_type="demo_request",
				entity_id=str(demo.id),
				description=f"Institution '{institution.name}' created and assigned to {admin_user.get_full_name() or admin_user.username}"
			)
			
			# Update demo request status
			demo.status = "approved"
			demo.save()
			
			messages.success(request, f"Demo request approved. Institution '{institution.name}' created.")
			return redirect("platform_admin:demo_requests")
		
		elif action == "reject":
			reason = request.POST.get("reason", "No reason provided")
			demo.status = "rejected"
			demo.save()
			
			AuditLog.record(
				action="Demo request rejected",
				actor=request.user,
				entity_type="demo_request",
				entity_id=str(demo.id),
				description=reason
			)
			
			messages.success(request, "Demo request rejected.")
			return redirect("platform_admin:demo_requests")
		
		else:
			messages.error(request, "Invalid action")
			return redirect("platform_admin:demo_requests")

	# Get active admin users for assignment dropdown
	from django.contrib.auth.models import User
	admin_users = User.objects.filter(is_staff=True, is_active=True).exclude(
		username=request.user.username
	).order_by("first_name", "last_name")

	context = {
		"demo_requests": qs,
		"admin_users": admin_users,
	}
	return render(request, "platform_admin/demo_requests.html", context)


@login_required
@super_admin_required
def user_oversight(request):
	"""View users by role and toggle account status. Create new admin users."""
	from accounts.firebase_auth import create_firebase_user

	profiles = PlatformUserProfile.objects.select_related("user").all()

	if request.method == "POST":
		action = request.POST.get("action")
		
		if action == "create":
			# Create new user
			email = request.POST.get("email", "").strip()
			password = request.POST.get("password", "").strip()
			full_name = request.POST.get("full_name", "").strip()
			role = request.POST.get("role", "admin")
			
			# Validate inputs
			if not email or not password or not full_name:
				messages.error(request, "Email, password, and full name are required.")
				return redirect("platform_admin:users")
			
			if len(password) < 6:
				messages.error(request, "Password must be at least 6 characters long.")
				return redirect("platform_admin:users")
			
			# Check if email already exists
			from django.contrib.auth.models import User
			if User.objects.filter(email=email).exists():
				messages.error(request, "A user with this email already exists.")
				return redirect("platform_admin:users")
			
			# Create Firebase user
			firebase_user = create_firebase_user(email, password, full_name)
			if not firebase_user:
				messages.error(request, "Failed to create user in Firebase. Please check the password requirements.")
				return redirect("platform_admin:users")
			
			# Create Django user
			try:
				first_name, last_name = (full_name.split(' ', 1) + [''])[:2]
				django_user = User.objects.create_user(
					username=email,
					email=email,
					password=password,  # Create with same password for consistency
					first_name=first_name,
					last_name=last_name,
					is_staff=True,
					is_active=True,
				)
				
				# Create platform user profile
				PlatformUserProfile.objects.create(
					user=django_user,
					role=role,
					is_active=True,
					notes=f"Created by {request.user.username}"
				)
				
				# Record audit log
				AuditLog.record(
					action="New admin user created",
					actor=request.user,
					entity_type="user",
					entity_id=str(django_user.id),
					description=f"Email: {email}, Role: {role}"
				)
				
				messages.success(request, f"User {email} created successfully. Password set in Firebase.")
				return redirect("platform_admin:users")
			except Exception as e:
				messages.error(request, f"Error creating Django user: {str(e)}")
				return redirect("platform_admin:users")
		
		elif action == "disable" or action == "enable":
			profile_id = request.POST.get("profile_id")
			profile = get_object_or_404(PlatformUserProfile, pk=profile_id)
			user = profile.user
			
			if action == "disable":
				user.is_active = False
			elif action == "enable":
				user.is_active = True
			user.save()
			
			AuditLog.record(
				action=f"User {action}",
				actor=request.user,
				entity_type="user",
				entity_id=str(user.id),
				description=profile.notes or "",
			)
			messages.success(request, f"Account {user.get_username()} updated.")
			return redirect("platform_admin:users")
		
		else:
			messages.error(request, "Invalid action")
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
