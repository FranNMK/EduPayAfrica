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

			# Update Firebase user (creates if doesn't exist)
			print(f"Updating Firebase user: old_email={old_email}, new_email={email}, has_password={bool(new_password)}")
			firebase_ok = update_firebase_user(
				current_email=old_email,
				new_email=email,
				new_password=new_password or None,
				display_name=full_name,
			)
			if not firebase_ok:
				messages.error(request, "Failed to update Firebase user. Check server logs for details.")
				return redirect("platform_admin:users")

			first_name, last_name = (full_name.split(' ', 1) + [''])[:2]
			user.email = email
			user.username = email
			user.first_name = first_name
			user.last_name = last_name

			if new_password:
				user.set_password(new_password)
				print(f"Django password updated for user: {user.username}")
				if user == request.user:
					update_session_auth_hash(request, user)

			user.save()
			print(f"Django user saved: {user.username}")

			AuditLog.record(
				action="User details updated",
				actor=request.user,
				entity_type="user",
				entity_id=str(user.id),
				description=f"Email updated to {email}{' and password reset' if new_password else ''}",
			)

			messages.success(request, f"User details updated successfully.{' Password has been changed.' if new_password else ''}")
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
	"""Manage platform-wide settings: academic years, terms, and theme customization."""

	settings_qs = PlatformSetting.objects.all().order_by("category", "key")

	if request.method == "POST":
		setting_type = request.POST.get("setting_type", "")
		
		if setting_type == "academic_year":
			# Handle academic year
			year_key = request.POST.get("key", "").strip()
			start_date = request.POST.get("start_date", "").strip()
			end_date = request.POST.get("end_date", "").strip()
			is_active = request.POST.get("is_active") == "on"
			
			if not year_key or not start_date or not end_date:
				messages.error(request, "All fields are required for academic year")
				return redirect("platform_admin:settings")
			
			# If setting as active, deactivate others
			if is_active:
				PlatformSetting.objects.filter(category="academic_year").update(is_active=False)
			
			value = f"Start: {start_date}, End: {end_date}"
			description = f"Academic year from {start_date} to {end_date}"
			
			setting, created = PlatformSetting.objects.update_or_create(
				key=year_key,
				defaults={
					"value": value,
					"category": "academic_year",
					"description": description,
					"is_active": is_active,
					"updated_by": request.user,
				},
			)
			
			AuditLog.record(
				action=f"Academic year {'added' if created else 'updated'}: {year_key}",
				actor=request.user,
				entity_type="setting",
				entity_id=setting.key,
				description=description,
			)
			messages.success(request, f"✓ Academic year '{year_key}' has been {'added' if created else 'updated'} successfully.")
			
		elif setting_type == "term":
			# Handle term
			term_name = request.POST.get("key", "").strip()
			term_number = request.POST.get("term_number", "").strip()
			start_date = request.POST.get("start_date", "").strip()
			end_date = request.POST.get("end_date", "").strip()
			
			if not term_name or not term_number or not start_date or not end_date:
				messages.error(request, "All fields are required for term")
				return redirect("platform_admin:settings")
			
			key = f"term_{term_number}_{term_name.lower().replace(' ', '_')}"
			value = f"Start: {start_date}, End: {end_date}"
			description = f"{term_name} (Term {term_number}) from {start_date} to {end_date}"
			
			setting, created = PlatformSetting.objects.update_or_create(
				key=key,
				defaults={
					"value": value,
					"category": "constant",
					"description": description,
					"is_active": True,
					"updated_by": request.user,
				},
			)
			
			AuditLog.record(
				action=f"Term {'added' if created else 'updated'}: {term_name}",
				actor=request.user,
				entity_type="setting",
				entity_id=setting.key,
				description=description,
			)
			messages.success(request, f"✓ Term '{term_name}' has been {'added' if created else 'updated'} successfully.")
			
		elif setting_type == "theme":
			# Handle theme settings
			primary_color = request.POST.get("primary_color", "#0d6efd").strip()
			secondary_color = request.POST.get("secondary_color", "#6c757d").strip()
			accent_color = request.POST.get("accent_color", "#198754").strip()
			logo_url = request.POST.get("logo_url", "").strip()
			favicon_url = request.POST.get("favicon_url", "").strip()
			custom_css = request.POST.get("custom_css", "").strip()
			
			# Save each theme setting
			theme_settings = [
				("theme_primary_color", primary_color, "Primary brand color"),
				("theme_secondary_color", secondary_color, "Secondary brand color"),
				("theme_accent_color", accent_color, "Accent/highlight color"),
			]
			
			if logo_url:
				theme_settings.append(("theme_logo_url", logo_url, "Platform logo URL"))
			if favicon_url:
				theme_settings.append(("theme_favicon_url", favicon_url, "Platform favicon URL"))
			if custom_css:
				theme_settings.append(("theme_custom_css", custom_css, "Custom CSS overrides"))
			
			for key, value, desc in theme_settings:
				PlatformSetting.objects.update_or_create(
					key=key,
					defaults={
						"value": value,
						"category": "constant",
						"description": desc,
						"is_active": True,
						"updated_by": request.user,
					},
				)
			
			AuditLog.record(
				action="Theme settings updated",
				actor=request.user,
				entity_type="setting",
				entity_id="theme",
				description="Updated platform theme and appearance settings",
			)
			messages.success(request, "✓ Theme settings have been updated successfully.")
		
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
	"""View all institution admins with CRUD operations."""
	
	if request.method == "POST":
		action = request.POST.get("action")
		
		if action == "create_admin":
			# Create new institution admin
			username = request.POST.get("username", "").strip()
			email = request.POST.get("email", "").strip()
			first_name = request.POST.get("first_name", "").strip()
			last_name = request.POST.get("last_name", "").strip()
			institution_id = request.POST.get("institution_id")
			notes = request.POST.get("notes", "").strip()
			
			if not username or not email:
				messages.error(request, "Username and email are required.")
				return redirect("platform_admin:institution_admins")
			
			from django.contrib.auth import get_user_model
			User = get_user_model()
			
			# Check if user already exists
			if User.objects.filter(username=username).exists():
				messages.error(request, f"User with username '{username}' already exists.")
				return redirect("platform_admin:institution_admins")
			
			if User.objects.filter(email=email).exists():
				messages.error(request, f"User with email '{email}' already exists.")
				return redirect("platform_admin:institution_admins")
			
			# Create user
			user = User.objects.create_user(
				username=username,
				email=email,
				first_name=first_name,
				last_name=last_name,
				is_staff=True,
				is_active=True
			)
			
			# Create profile
			institution = None
			if institution_id:
				institution = get_object_or_404(Institution, pk=institution_id)
			
			profile = PlatformUserProfile.objects.create(
				user=user,
				role="institution_admin",
				institution=institution,
				notes=notes,
				is_active=True
			)
			
			AuditLog.record(
				action="Institution admin created",
				actor=request.user,
				entity_type="institution_admin",
				entity_id=str(user.id),
				description=f"Created admin {username} for {institution.name if institution else 'no institution'}"
			)
			
			messages.success(request, f"Institution admin {username} created successfully.")
			return redirect("platform_admin:institution_admins")
		
		elif action == "update_admin":
			# Update existing admin
			profile_id = request.POST.get("profile_id")
			profile = get_object_or_404(PlatformUserProfile, pk=profile_id)
			
			first_name = request.POST.get("first_name", "").strip()
			last_name = request.POST.get("last_name", "").strip()
			email = request.POST.get("email", "").strip()
			institution_id = request.POST.get("institution_id")
			notes = request.POST.get("notes", "").strip()
			is_active = request.POST.get("is_active") == "on"
			
			# Update user
			if first_name:
				profile.user.first_name = first_name
			if last_name:
				profile.user.last_name = last_name
			if email and email != profile.user.email:
				from django.contrib.auth import get_user_model
				User = get_user_model()
				if User.objects.filter(email=email).exclude(pk=profile.user.pk).exists():
					messages.error(request, f"Email '{email}' is already in use.")
					return redirect("platform_admin:institution_admins")
				profile.user.email = email
			
			profile.user.is_active = is_active
			profile.user.save()
			
			# Update profile
			if institution_id:
				profile.institution = get_object_or_404(Institution, pk=institution_id)
			else:
				profile.institution = None
			
			profile.notes = notes
			profile.is_active = is_active
			profile.save()
			
			AuditLog.record(
				action="Institution admin updated",
				actor=request.user,
				entity_type="institution_admin",
				entity_id=str(profile.user.id),
				description=f"Updated admin {profile.user.username}"
			)
			
			messages.success(request, f"Institution admin {profile.user.username} updated successfully.")
			return redirect("platform_admin:institution_admins")
		
		elif action == "delete_admin":
			# Delete admin
			profile_id = request.POST.get("profile_id")
			profile = get_object_or_404(PlatformUserProfile, pk=profile_id)
			username = profile.user.username
			user_id = profile.user.id
			
			# Delete user (cascade will delete profile)
			profile.user.delete()
			
			AuditLog.record(
				action="Institution admin deleted",
				actor=request.user,
				entity_type="institution_admin",
				entity_id=str(user_id),
				description=f"Deleted admin {username}"
			)
			
			messages.success(request, f"Institution admin {username} deleted successfully.")
			return redirect("platform_admin:institution_admins")
	
	# Get all profiles with institution_admin role
	institution_admins = PlatformUserProfile.objects.filter(
		role='institution_admin'
	).select_related('user', 'institution').order_by('-created_at')
	
	# Get all institutions for the dropdown
	institutions = Institution.objects.filter(status__in=["approved", "active"]).order_by("name")
	
	context = {
		'institution_admins': institution_admins,
		'institutions': institutions,
	}
	return render(request, 'platform_admin/institution_admins.html', context)
