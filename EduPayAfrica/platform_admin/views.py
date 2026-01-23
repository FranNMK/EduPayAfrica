from datetime import datetime

from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
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
		action = request.POST.get("action")

		if action == "create_institution":
			name = request.POST.get("name", "").strip()
			institution_type = request.POST.get("institution_type")
			contact_name = request.POST.get("contact_name", "").strip()
			contact_email = request.POST.get("contact_email", "").strip()
			contact_phone = request.POST.get("contact_phone", "").strip()
			note = request.POST.get("note", "").strip()

			if not name or not institution_type or not contact_name or not contact_email:
				messages.error(request, "Name, type, contact name, and contact email are required.")
				return redirect("platform_admin:institutions")

			institution = Institution.objects.create(
				name=name,
				institution_type=institution_type,
				contact_name=contact_name,
				contact_email=contact_email,
				contact_phone=contact_phone,
				onboarding_notes=note,
				status="pending",
			)

			AuditLog.record(
				action="Institution created",
				actor=request.user,
				entity_type="institution",
				entity_id=str(institution.id),
				description=note,
			)
			messages.success(request, f"Institution {institution.name} created and set to pending.")
			return redirect("platform_admin:institutions")

		if action == "assign_admin":
			institution_id = request.POST.get("institution_id")
			user_id = request.POST.get("user_id")
			if not user_id:
				messages.error(request, "Please select a user to assign as admin.")
				return redirect("platform_admin:institutions")
			institution = get_object_or_404(Institution, pk=institution_id)
			from django.contrib.auth import get_user_model
			User = get_user_model()
			try:
				admin_user = User.objects.get(pk=user_id)
			except User.DoesNotExist:
				messages.error(request, "Selected user not found.")
				return redirect("platform_admin:institutions")

			profile, _ = PlatformUserProfile.objects.get_or_create(user=admin_user)
			profile.institution = institution
			profile.role = "institution_admin"
			profile.is_active = True
			profile.save()

			AuditLog.record(
				action="Institution admin assigned",
				actor=request.user,
				entity_type="institution",
				entity_id=str(institution.id),
				description=f"{admin_user.get_full_name() or admin_user.username} assigned as admin",
			)
			messages.success(request, "School admin assigned to institution.")
			return redirect("platform_admin:institutions")

		if action == "update_institution":
			institution_id = request.POST.get("institution_id")
			institution = get_object_or_404(Institution, pk=institution_id)
			name = request.POST.get("name", "").strip()
			institution_type = request.POST.get("institution_type")
			contact_name = request.POST.get("contact_name", "").strip()
			contact_email = request.POST.get("contact_email", "").strip()
			contact_phone = request.POST.get("contact_phone", "").strip()
			note = request.POST.get("note", "").strip()

			if not name or not institution_type or not contact_name or not contact_email:
				messages.error(request, "Name, type, contact name, and contact email are required.")
				return redirect("platform_admin:institutions")

			institution.name = name
			institution.institution_type = institution_type
			institution.contact_name = contact_name
			institution.contact_email = contact_email
			institution.contact_phone = contact_phone
			institution.onboarding_notes = note
			institution.save()

			AuditLog.record(
				action="Institution updated",
				actor=request.user,
				entity_type="institution",
				entity_id=str(institution.id),
				description=note,
			)
			messages.success(request, f"Institution {institution.name} updated.")
			return redirect("platform_admin:institutions")

		if action == "delete_institution":
			institution_id = request.POST.get("institution_id")
			institution = get_object_or_404(Institution, pk=institution_id)
			name = institution.name
			institution.delete()
			AuditLog.record(
				action="Institution deleted",
				actor=request.user,
				entity_type="institution",
				entity_id=str(institution_id),
				description=f"Deleted {name}",
			)
			messages.success(request, f"Institution {name} deleted.")
			return redirect("platform_admin:institutions")

		institution_id = request.POST.get("institution_id")
		institution = get_object_or_404(Institution, pk=institution_id)
		note = request.POST.get("note", "").strip()
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

	from django.contrib.auth import get_user_model
	User = get_user_model()
	admin_users = User.objects.filter(is_staff=True, is_active=True).order_by("first_name", "last_name")

	context = {
		"institutions": institutions_qs,
		"admin_users": admin_users,
	}
	return render(request, "platform_admin/institutions.html", context)


@login_required
@super_admin_required
def demo_requests(request):
	"""View and approve demo requests from institutions."""

	qs = DemoRequest.objects.select_related("institution", "approved_by").all().order_by("-created_at")
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
		action = request.POST.get("action")
		demo_id = request.POST.get("demo_id")
		demo = get_object_or_404(DemoRequest, pk=demo_id)

		if action == "approve":
			onboarding_notes = request.POST.get("onboarding_notes", "")

			# Create institution if not already linked
			if demo.institution:
				institution = demo.institution
			else:
				institution = Institution.objects.create(
					name=demo.institution_name,
					institution_type=demo.institution_type,
					contact_name=demo.full_name,
					contact_email=demo.email,
					contact_phone=demo.phone,
					status="pending",
					onboarding_notes=onboarding_notes,
				)

			InstitutionStatusLog.objects.create(
				institution=institution,
				action="approved",
				actor=request.user,
				note="Created from demo request approval",
				previous_status="draft",
				new_status="pending",
			)

			demo.status = "approved"
			demo.approved_at = timezone.now()
			demo.approved_by = request.user
			demo.institution = institution
			demo.save()

			AuditLog.record(
				action="Demo request approved",
				actor=request.user,
				entity_type="demo_request",
				entity_id=str(demo.id),
				description=f"Institution '{institution.name}' created from demo request",
			)

			messages.success(request, f"Demo request approved. Institution '{institution.name}' created and awaiting admin assignment.")
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
				description=reason,
			)

			messages.success(request, "Demo request rejected.")
			return redirect("platform_admin:demo_requests")

		elif action == "pending":
			demo.status = "pending"
			demo.save()
			messages.success(request, "Demo request moved to pending.")
			return redirect("platform_admin:demo_requests")

		else:
			messages.error(request, "Invalid action")
			return redirect("platform_admin:demo_requests")

	context = {
		"demo_requests": qs,
	}
	return render(request, "platform_admin/demo_requests.html", context)


@login_required
@super_admin_required
def user_oversight(request):
	"""View users by role and toggle account status. Create and assign users."""
	from accounts.firebase_auth import create_firebase_user, update_firebase_user
	from django.contrib.auth import get_user_model

	profiles = PlatformUserProfile.objects.select_related("user", "institution").all()
	institutions = Institution.objects.all().order_by("name")
	User = get_user_model()

	if request.method == "POST":
		action = request.POST.get("action")
		
		if action == "update_details":
			profile_id = request.POST.get("profile_id")
			email = request.POST.get("email", "").strip()
			full_name = request.POST.get("full_name", "").strip()
			new_password = request.POST.get("password", "").strip()
			profile = get_object_or_404(PlatformUserProfile, pk=profile_id)
			user = profile.user
			old_email = user.email

			if not email or not full_name:
				messages.error(request, "Email and full name are required.")
				return redirect("platform_admin:users")

			if User.objects.filter(email=email).exclude(pk=user.pk).exists():
				messages.error(request, "Another user already uses this email.")
				return redirect("platform_admin:users")

			# First update Firebase so login stays in sync
			if new_password and len(new_password) < 6:
				messages.error(request, "Password must be at least 6 characters long.")
				return redirect("platform_admin:users")

			firebase_ok = update_firebase_user(
				current_email=old_email,
				new_email=email,
				new_password=new_password or None,
				display_name=full_name,
			)
			if not firebase_ok:
				messages.error(request, "Failed to update Firebase user. No changes were applied.")
				return redirect("platform_admin:users")

			first_name, last_name = (full_name.split(' ', 1) + [''])[:2]
			user.email = email
			user.username = email
			user.first_name = first_name
			user.last_name = last_name

			if new_password:
				user.set_password(new_password)
				if user == request.user:
					update_session_auth_hash(request, user)

			user.save()

			AuditLog.record(
				action="User details updated",
				actor=request.user,
				entity_type="user",
				entity_id=str(user.id),
				description=f"Email updated to {email}{' and password reset' if new_password else ''}",
			)

			messages.success(request, "User details updated.")
			return redirect("platform_admin:users")

		if action == "create":
			# Create new user
			email = request.POST.get("email", "").strip()
			password = request.POST.get("password", "").strip()
			full_name = request.POST.get("full_name", "").strip()
			role = request.POST.get("role", "institution_admin")
			institution_id = request.POST.get("institution_id") or None
			
			# Validate inputs
			if not email or not password or not full_name:
				messages.error(request, "Email, password, and full name are required.")
				return redirect("platform_admin:users")
			
			if len(password) < 6:
				messages.error(request, "Password must be at least 6 characters long.")
				return redirect("platform_admin:users")
			
			if User.objects.filter(email=email).exists():
				messages.error(request, "A user with this email already exists.")
				return redirect("platform_admin:users")
			
			firebase_user = create_firebase_user(email, password, full_name)
			if not firebase_user:
				messages.error(request, "Failed to create user in Firebase. Please check the password requirements.")
				return redirect("platform_admin:users")

			institution = None
			if institution_id:
				try:
					institution = Institution.objects.get(pk=institution_id)
				except Institution.DoesNotExist:
					messages.error(request, "Institution not found.")
					return redirect("platform_admin:users")

			try:
				first_name, last_name = (full_name.split(' ', 1) + [''])[:2]
				django_user = User.objects.create_user(
					username=email,
					email=email,
					password=password,
					first_name=first_name,
					last_name=last_name,
					is_staff=True,
					is_superuser=(role == "super_admin"),
					is_active=True,
				)

				PlatformUserProfile.objects.create(
					user=django_user,
					role=role,
					institution=institution,
					is_active=True,
					notes=f"Created by {request.user.username}",
				)

				AuditLog.record(
					action="New user created",
					actor=request.user,
					entity_type="user",
					entity_id=str(django_user.id),
					description=f"Email: {email}, Role: {role}",
				)

				messages.success(request, f"User {email} created successfully.")
				return redirect("platform_admin:users")
			except Exception as e:
				messages.error(request, f"Error creating Django user: {str(e)}")
				return redirect("platform_admin:users")

		elif action in ["disable", "enable"]:
			profile_id = request.POST.get("profile_id")
			profile = get_object_or_404(PlatformUserProfile, pk=profile_id)
			user = profile.user
			user.is_active = action == "enable"
			profile.is_active = user.is_active
			user.save()
			profile.save()

			AuditLog.record(
				action=f"User {action}",
				actor=request.user,
				entity_type="user",
				entity_id=str(user.id),
				description=profile.notes or "",
			)
			messages.success(request, f"Account {user.get_username()} updated.")
			return redirect("platform_admin:users")

		elif action == "update":
			profile_id = request.POST.get("profile_id")
			role = request.POST.get("role")
			institution_id = request.POST.get("institution_id") or None
			profile = get_object_or_404(PlatformUserProfile, pk=profile_id)

			institution = None
			if institution_id:
				institution = get_object_or_404(Institution, pk=institution_id)

			profile.role = role
			profile.institution = institution
			profile.save()

			# Update staff/superuser flags for clarity
			profile.user.is_staff = True
			profile.user.is_superuser = role == "super_admin"
			profile.user.save()

			AuditLog.record(
				action="User updated",
				actor=request.user,
				entity_type="user",
				entity_id=str(profile.user.id),
				description=f"Role: {role}",
			)
			messages.success(request, "User updated.")
			return redirect("platform_admin:users")

		elif action == "delete":
			profile_id = request.POST.get("profile_id")
			profile = get_object_or_404(PlatformUserProfile, pk=profile_id)
			user = profile.user
			profile.delete()
			user.delete()
			messages.success(request, "User deleted.")
			return redirect("platform_admin:users")

		else:
			messages.error(request, "Invalid action")
			return redirect("platform_admin:users")

	context = {
		"profiles": profiles,
		"institutions": institutions,
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


@login_required
@super_admin_required
def institution_admins(request):
	"""View all institution admins with their contact details."""
	
	# Get all profiles with institution_admin role
	institution_admins = PlatformUserProfile.objects.filter(
		role='institution_admin'
	).select_related('user', 'institution').order_by('-created_at')
	
	context = {
		'institution_admins': institution_admins,
	}
	return render(request, 'platform_admin/institution_admins.html', context)
