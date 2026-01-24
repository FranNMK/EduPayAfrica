from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Sum, F, Count, Case, When
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from datetime import datetime, timedelta
import csv
import openpyxl
from io import BytesIO

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


def get_institution_or_404(request):
    """Get institution profile for current user."""
    try:
        return request.user.institution_profile
    except InstitutionProfile.DoesNotExist:
        return None


def get_staff_role(request, institution):
    """Get staff role for current user at this institution."""
    try:
        staff = InstitutionStaff.objects.get(
            institution=institution, user=request.user, is_active=True
        )
        return staff.role
    except InstitutionStaff.DoesNotExist:
        return None


def require_role(*allowed_roles):
    """Decorator to check user role at institution."""
    def decorator(view_func):
        def wrapper(request, *args, **kwargs):
            institution = get_institution_or_404(request)
            if not institution:
                messages.error(request, "You don't have an institution profile.")
                return redirect("home")
            
            staff_role = get_staff_role(request, institution)
            if not staff_role or staff_role not in allowed_roles:
                messages.error(request, f"You don't have permission. Required role: {', '.join(allowed_roles)}")
                return redirect("institutions:dashboard")
            
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


@login_required
def institution_dashboard(request):
    """Main institution dashboard - role-based content."""
    institution = get_institution_or_404(request)
    
    # Auto-create InstitutionProfile from PlatformUserProfile if needed
    if not institution and hasattr(request.user, 'platform_profile'):
        platform_profile = request.user.platform_profile
        if platform_profile.role == 'institution_admin' and platform_profile.institution:
            # Create InstitutionProfile from platform admin data
            institution = InstitutionProfile.objects.create(
                user=request.user,
                institution_name=platform_profile.institution.name,
                institution_type=platform_profile.institution.institution_type,
                contact_email=platform_profile.institution.contact_email,
                phone_number=platform_profile.institution.contact_phone,
                is_active=True
            )
            messages.success(request, f"Welcome! Your institution profile has been created for {institution.institution_name}.")
    
    if not institution:
        messages.error(request, "You don't have an institution profile. Please contact support.")
        return redirect("home")
    
    # Auto-create InstitutionStaff record for institution admins if needed
    staff_role = get_staff_role(request, institution)
    if not staff_role and hasattr(request.user, 'platform_profile'):
        if request.user.platform_profile.role == 'institution_admin':
            # Create staff record with admin role
            InstitutionStaff.objects.create(
                institution=institution,
                user=request.user,
                role='admin',
                is_active=True
            )
            staff_role = 'admin'
            messages.info(request, "Your admin access has been activated.")
    
    # Common data for all roles
    context = {
        "institution": institution,
        "staff_role": staff_role,
    }
    
    # Get active academic year
    active_academic_year = AcademicYear.objects.filter(
        institution=institution, is_active=True
    ).first()
    context["active_academic_year"] = active_academic_year
    
    if staff_role == "admin":
        # Admin sees full dashboard
        students_count = Student.objects.filter(institution=institution, is_active=True).count()
        total_fees_billed = StudentFeeAssignment.objects.filter(
            student__institution=institution
        ).aggregate(total=Sum("total_fees"))["total"] or 0
        
        total_outstanding = StudentFeeAssignment.objects.filter(
            student__institution=institution
        ).aggregate(
            total=Sum(F("total_fees") - F("discount_amount") + F("penalty_amount") - F("amount_paid"))
        )["total"] or 0
        
        overdue_count = StudentFeeAssignment.objects.filter(
            student__institution=institution, is_overdue=True
        ).count()
        
        context.update({
            "students_count": students_count,
            "total_fees_billed": total_fees_billed,
            "total_outstanding": total_outstanding,
            "overdue_count": overdue_count,
            "staff_list": InstitutionStaff.objects.filter(institution=institution, is_active=True),
        })
        return render(request, "institutions/dashboards/admin_dashboard.html", context)
    
    elif staff_role == "principal":
        # Principal sees messaging and analytics
        context["messages_sent"] = PrincipalMessage.objects.filter(
            institution=institution
        ).count()
        context["recent_messages"] = PrincipalMessage.objects.filter(
            institution=institution
        ).order_by("-sent_date")[:5]
        context["staff_list"] = InstitutionStaff.objects.filter(institution=institution, is_active=True)
        return render(request, "institutions/dashboards/principal_dashboard.html", context)
    
    elif staff_role in ["bursar", "accountant"]:
        # Bursar/Finance sees fee structures and analysis
        total_billed = StudentFeeAssignment.objects.filter(
            student__institution=institution
        ).aggregate(total=Sum("total_fees"))["total"] or 0
        
        total_paid = StudentFeeAssignment.objects.filter(
            student__institution=institution
        ).aggregate(total=Sum("amount_paid"))["total"] or 0
        
        collection_rate = (total_paid / total_billed * 100) if total_billed > 0 else 0
        
        context.update({
            "total_billed": total_billed,
            "total_paid": total_paid,
            "total_outstanding": total_billed - total_paid,
            "collection_rate": round(collection_rate, 2),
            "programs": Program.objects.filter(institution=institution, is_active=True),
            "fee_structures": FeeStructure.objects.filter(institution=institution),
        })
        return render(request, "institutions/dashboards/bursar_dashboard.html", context)
    
    elif staff_role == "teacher":
        # Teacher sees their students
        context["students_count"] = Student.objects.filter(institution=institution, is_active=True).count()
        return render(request, "institutions/dashboards/teacher_dashboard.html", context)
    
    else:
        # Generic dashboard for other roles
        return render(request, "institutions/dashboards/generic_dashboard.html", context)


@login_required
@require_role("admin")
def staff_management(request):
    """Manage institution staff and roles."""
    institution = get_institution_or_404(request)
    
    staff_list = InstitutionStaff.objects.filter(institution=institution)
    
    context = {
        "institution": institution,
        "staff_list": staff_list,
        "roles": InstitutionStaff.ROLE_CHOICES,
    }
    
    return render(request, "institutions/staff_management.html", context)


@login_required
@require_role("admin")
@require_http_methods(["POST"])
def add_staff(request):
    """Add staff member to institution."""
    institution = get_institution_or_404(request)
    
    try:
        full_name = request.POST.get("full_name")
        email = request.POST.get("email")
        phone = request.POST.get("phone_number")
        role = request.POST.get("role")
        
        # Create user if doesn't exist
        from django.contrib.auth.models import User
        user, created = User.objects.get_or_create(
            email=email,
            defaults={"username": email.split("@")[0], "first_name": full_name}
        )
        
        # Create staff record
        staff = InstitutionStaff.objects.create(
            institution=institution,
            user=user,
            full_name=full_name,
            email=email,
            phone_number=phone,
            role=role,
        )
        
        # Log action
        InstitutionAuditLog.objects.create(
            institution=institution,
            actor=request.user,
            action="staff_added",
            entity_type="InstitutionStaff",
            entity_id=str(staff.pk),
            description=f"Added {full_name} as {role}",
        )
        
        messages.success(request, f"Staff member {full_name} added successfully!")
        return redirect("institutions:staff_management")
    
    except Exception as e:
        messages.error(request, f"Error adding staff: {str(e)}")
        return redirect("institutions:staff_management")


@login_required
@require_role("admin")
def student_management(request):
    """Manage students - manual add, bulk upload, view all."""
    institution = get_institution_or_404(request)
    
    students = Student.objects.filter(institution=institution, is_active=True)
    programs = Program.objects.filter(institution=institution, is_active=True)
    academic_years = AcademicYear.objects.filter(institution=institution)
    
    context = {
        "institution": institution,
        "students": students,
        "programs": programs,
        "academic_years": academic_years,
    }
    
    return render(request, "institutions/students.html", context)


@login_required
@require_role("admin")
@require_http_methods(["POST"])
def add_student(request):
    """Add single student."""
    institution = get_institution_or_404(request)
    
    try:
        full_name = request.POST.get("full_name")
        admission_number = request.POST.get("admission_number")
        email = request.POST.get("email", "")
        program_id = request.POST.get("program_id")
        academic_year_id = request.POST.get("academic_year_id")
        
        program = Program.objects.get(pk=program_id, institution=institution)
        academic_year = AcademicYear.objects.get(pk=academic_year_id, institution=institution)
        
        student = Student.objects.create(
            institution=institution,
            program=program,
            academic_year=academic_year,
            full_name=full_name,
            admission_number=admission_number,
            email=email,
        )
        
        InstitutionAuditLog.objects.create(
            institution=institution,
            actor=request.user,
            action="student_added",
            entity_type="Student",
            entity_id=str(student.pk),
            description=f"Added student {full_name}",
        )
        
        messages.success(request, f"Student {full_name} added successfully!")
        return redirect("institutions:students")
    
    except Exception as e:
        messages.error(request, f"Error adding student: {str(e)}")
        return redirect("institutions:students")


@login_required
@require_role("admin")
@require_http_methods(["POST"])
def bulk_upload_students(request):
    """Bulk upload students from Excel/CSV."""
    institution = get_institution_or_404(request)
    
    try:
        file = request.FILES.get("file")
        
        if not file:
            messages.error(request, "No file selected.")
            return redirect("institutions:students")
        
        # Handle both Excel and CSV
        students_added = 0
        errors = []
        
        if file.name.endswith(".xlsx"):
            # Excel file
            wb = openpyxl.load_workbook(file)
            ws = wb.active
            
            for row_idx, row in enumerate(ws.iter_rows(min_row=2, values_only=True), 2):
                try:
                    full_name, admission_no, email, program_code, year_code = row[:5]
                    
                    program = Program.objects.get(
                        institution=institution, program_code=program_code
                    )
                    academic_year = AcademicYear.objects.get(
                        institution=institution, year_code=year_code
                    )
                    
                    Student.objects.create(
                        institution=institution,
                        program=program,
                        academic_year=academic_year,
                        full_name=full_name,
                        admission_number=admission_no,
                        email=email or "",
                    )
                    students_added += 1
                
                except Exception as e:
                    errors.append(f"Row {row_idx}: {str(e)}")
        
        else:
            # CSV file
            decoded_file = file.read().decode("utf-8").split("\n")
            reader = csv.reader(decoded_file)
            next(reader)  # Skip header
            
            for row_idx, row in enumerate(reader, 2):
                if not row:
                    continue
                try:
                    full_name, admission_no, email, program_code, year_code = row[:5]
                    
                    program = Program.objects.get(
                        institution=institution, program_code=program_code
                    )
                    academic_year = AcademicYear.objects.get(
                        institution=institution, year_code=year_code
                    )
                    
                    Student.objects.create(
                        institution=institution,
                        program=program,
                        academic_year=academic_year,
                        full_name=full_name,
                        admission_number=admission_no,
                        email=email or "",
                    )
                    students_added += 1
                
                except Exception as e:
                    errors.append(f"Row {row_idx}: {str(e)}")
        
        InstitutionAuditLog.objects.create(
            institution=institution,
            actor=request.user,
            action="bulk_upload",
            entity_type="Student",
            description=f"Bulk uploaded {students_added} students",
        )
        
        messages.success(request, f"Successfully added {students_added} students!")
        
        if errors:
            messages.warning(request, f"Errors: {'; '.join(errors[:5])}")
        
        return redirect("institutions:students")
    
    except Exception as e:
        messages.error(request, f"Error uploading file: {str(e)}")
        return redirect("institutions:students")


@login_required
@require_role("admin", "bursar", "accountant")
def program_management(request):
    """Manage academic programs."""
    institution = get_institution_or_404(request)
    
    programs = Program.objects.filter(institution=institution)
    faculties = Faculty.objects.filter(institution=institution)
    
    context = {
        "institution": institution,
        "programs": programs,
        "faculties": faculties,
        "program_types": Program.PROGRAM_TYPE_CHOICES,
    }
    
    return render(request, "institutions/program_management.html", context)


@login_required
@require_role("admin", "bursar", "accountant")
@require_http_methods(["POST"])
def add_program(request):
    """Add new academic program."""
    institution = get_institution_or_404(request)
    
    try:
        program_name = request.POST.get("program_name")
        program_code = request.POST.get("program_code")
        program_type = request.POST.get("program_type")
        faculty_id = request.POST.get("faculty_id")
        duration_months = request.POST.get("duration_months")
        description = request.POST.get("description", "")
        
        faculty = Faculty.objects.get(pk=faculty_id, institution=institution)
        
        program = Program.objects.create(
            institution=institution,
            faculty=faculty,
            program_name=program_name,
            program_code=program_code,
            program_type=program_type,
            duration_months=int(duration_months),
            description=description,
        )
        
        InstitutionAuditLog.objects.create(
            institution=institution,
            actor=request.user,
            action="program_created",
            entity_type="Program",
            entity_id=str(program.pk),
            description=f"Created program {program_name}",
        )
        
        messages.success(request, f"Program {program_name} created successfully!")
        return redirect("institutions:program_management")
    
    except Exception as e:
        messages.error(request, f"Error creating program: {str(e)}")
        return redirect("institutions:program_management")


@login_required
@require_role("bursar", "accountant")
def fee_structure_management(request):
    """Manage fee structures for different programs."""
    institution = get_institution_or_404(request)
    
    fee_structures = FeeStructure.objects.filter(institution=institution)
    programs = Program.objects.filter(institution=institution, is_active=True)
    
    context = {
        "institution": institution,
        "fee_structures": fee_structures,
        "programs": programs,
    }
    
    return render(request, "institutions/fee_structure_management.html", context)


@login_required
@require_role("bursar", "accountant")
@require_http_methods(["POST"])
def create_fee_structure(request):
    """Create fee structure for specific program/academic year."""
    institution = get_institution_or_404(request)
    
    try:
        version = request.POST.get("version", 1)
        
        fee_structure = FeeStructure.objects.create(
            institution=institution,
            version=int(version),
        )
        
        # Get fee items from POST
        fee_names = request.POST.getlist("fee_name")
        fee_types = request.POST.getlist("fee_type")
        fee_amounts = request.POST.getlist("fee_amount")
        fee_mandatory = request.POST.getlist("fee_mandatory")
        
        for i, name in enumerate(fee_names):
            if name and fee_amounts[i]:
                FeeItem.objects.create(
                    fee_structure=fee_structure,
                    name=name,
                    fee_type=fee_types[i] if i < len(fee_types) else "other",
                    amount=float(fee_amounts[i]),
                    is_mandatory=i in [int(x) for x in fee_mandatory],
                )
        
        InstitutionAuditLog.objects.create(
            institution=institution,
            actor=request.user,
            action="fee_structure_created",
            entity_type="FeeStructure",
            entity_id=str(fee_structure.pk),
            description="Created new fee structure",
        )
        
        messages.success(request, "Fee structure created successfully!")
        return redirect("institutions:fee_structure_management")
    
    except Exception as e:
        messages.error(request, f"Error creating fee structure: {str(e)}")
        return redirect("institutions:fee_structure_management")


@login_required
@require_role("principal")
def messaging_panel(request):
    """Principal messaging panel."""
    institution = get_institution_or_404(request)
    
    messages_list = PrincipalMessage.objects.filter(institution=institution)
    
    context = {
        "institution": institution,
        "messages": messages_list,
        "message_types": PrincipalMessage.MESSAGE_TYPE_CHOICES,
    }
    
    return render(request, "institutions/messaging_panel.html", context)


@login_required
@require_role("principal")
@require_http_methods(["POST"])
def send_message(request):
    """Send message to parents about fees."""
    institution = get_institution_or_404(request)
    
    try:
        staff = InstitutionStaff.objects.get(institution=institution, user=request.user)
        
        subject = request.POST.get("subject")
        content = request.POST.get("content")
        message_type = request.POST.get("message_type")
        target_type = request.POST.get("target_type")  # all, overdue, specific
        
        message = PrincipalMessage.objects.create(
            institution=institution,
            sent_by=staff,
            subject=subject,
            content=content,
            message_type=message_type,
        )
        
        # Add target students
        if target_type == "all":
            students = Student.objects.filter(institution=institution, is_active=True)
        elif target_type == "overdue":
            students = Student.objects.filter(
                institution=institution,
                fee_assignments__is_overdue=True,
                is_active=True
            ).distinct()
        else:
            student_ids = request.POST.getlist("student_ids")
            students = Student.objects.filter(pk__in=student_ids)
        
        message.target_students.set(students)
        
        InstitutionAuditLog.objects.create(
            institution=institution,
            actor=request.user,
            action="message_sent",
            entity_type="PrincipalMessage",
            entity_id=str(message.pk),
            description=f"Sent message to {message.target_students.count()} students",
        )
        
        messages.success(request, f"Message sent to {message.target_students.count()} students!")
        return redirect("institutions:messaging_panel")
    
    except Exception as e:
        messages.error(request, f"Error sending message: {str(e)}")
        return redirect("institutions:messaging_panel")


@login_required
@require_role("principal", "bursar", "accountant")
def fee_analysis_dashboard(request):
    """Fee analysis and collection analytics."""
    institution = get_institution_or_404(request)
    
    # Get active academic year
    active_year = AcademicYear.objects.filter(
        institution=institution, is_active=True
    ).first()
    
    if active_year:
        # Get current snapshot or create if missing
        today = timezone.now().date()
        snapshot, created = FeeAnalysisSnapshot.objects.get_or_create(
            institution=institution,
            academic_year=active_year,
            snapshot_date=today,
            defaults={
                "total_students": Student.objects.filter(
                    institution=institution, academic_year=active_year, is_active=True
                ).count(),
            }
        )
        
        # Calculate metrics
        assignments = StudentFeeAssignment.objects.filter(
            student__institution=institution,
            academic_year=active_year
        )
        
        total_billed = assignments.aggregate(Sum("total_fees"))["total_fees__sum"] or 0
        total_paid = assignments.aggregate(Sum("amount_paid"))["amount_paid__sum"] or 0
        
        stats = {
            "total_students": snapshot.total_students,
            "total_billed": total_billed,
            "total_paid": total_paid,
            "total_outstanding": total_billed - total_paid,
            "fully_paid": assignments.filter(amount_paid__gte=F("total_fees") - F("discount_amount") + F("penalty_amount")).count(),
            "partially_paid": assignments.filter(amount_paid__gt=0, amount_paid__lt=F("total_fees") - F("discount_amount") + F("penalty_amount")).count(),
            "not_paid": assignments.filter(amount_paid=0).count(),
            "overdue": assignments.filter(is_overdue=True).count(),
            "collection_rate": (total_paid / total_billed * 100) if total_billed > 0 else 0,
        }
    else:
        stats = {
            "total_students": 0,
            "total_billed": 0,
            "total_paid": 0,
            "total_outstanding": 0,
            "fully_paid": 0,
            "partially_paid": 0,
            "not_paid": 0,
            "overdue": 0,
            "collection_rate": 0,
        }
    
    # Get detailed fees for table
    detailed_fees = StudentFeeAssignment.objects.filter(
        student__institution=institution,
        academic_year=active_year
    ).select_related("student").order_by("-created_at")[:100]
    
    context = {
        "institution": institution,
        "active_year": active_year,
        "stats": stats,
        "detailed_fees": detailed_fees,
    }
    
    return render(request, "institutions/fee_analysis.html", context)


@login_required
def profile_management(request):
    """Institution profile view/update."""
    institution = get_institution_or_404(request)
    
    if request.method == "POST":
        # Update institution
        institution.contact_email = request.POST.get("contact_email")
        institution.phone_number = request.POST.get("phone_number")
        institution.address = request.POST.get("address")
        institution.save()
        
        InstitutionAuditLog.objects.create(
            institution=institution,
            actor=request.user,
            action="profile_updated",
            entity_type="InstitutionProfile",
            entity_id=str(institution.pk),
            description="Updated institution profile",
        )
        
        messages.success(request, "Institution profile updated successfully!")
        return redirect("institutions:profile")
    
    context = {"institution": institution}
    return render(request, "institutions/profile.html", context)


@login_required
def academic_structure(request):
    """Academic structure management (years, terms, faculties)."""
    institution = get_institution_or_404(request)
    
    academic_years = AcademicYear.objects.filter(institution=institution)
    terms = Term.objects.filter(academic_year__institution=institution)
    faculties = Faculty.objects.filter(institution=institution)
    
    context = {
        "institution": institution,
        "academic_years": academic_years,
        "terms": terms,
        "faculties": faculties,
        "term_choices": Term.TERM_CHOICES,
    }
    
    return render(request, "institutions/academic_structure.html", context)


@login_required
@require_role("admin")
@require_http_methods(["POST"])
def add_academic_year(request):
    """Add academic year."""
    institution = get_institution_or_404(request)
    
    try:
        year_code = request.POST.get("year_code")
        start_date = request.POST.get("start_date")
        end_date = request.POST.get("end_date")
        is_active = request.POST.get("is_active") == "on"
        
        # Deactivate other active years if this one is active
        if is_active:
            AcademicYear.objects.filter(
                institution=institution, is_active=True
            ).update(is_active=False)
        
        academic_year = AcademicYear.objects.create(
            institution=institution,
            year_code=year_code,
            start_date=start_date,
            end_date=end_date,
            is_active=is_active,
        )
        
        InstitutionAuditLog.objects.create(
            institution=institution,
            actor=request.user,
            action="academic_year_created",
            entity_type="AcademicYear",
            entity_id=str(academic_year.pk),
            description=f"Created academic year {year_code}",
        )
        
        messages.success(request, f"Academic year {year_code} created successfully!")
        return redirect("institutions:academic_structure")
    
    except Exception as e:
        messages.error(request, f"Error creating academic year: {str(e)}")
        return redirect("institutions:academic_structure")


@login_required
@require_role("admin")
@require_http_methods(["POST"])
def add_term(request):
    """Add term."""
    institution = get_institution_or_404(request)
    
    try:
        academic_year_id = request.POST.get("academic_year_id")
        term_number = request.POST.get("term_number")
        term_name = request.POST.get("term_name", "")
        start_date = request.POST.get("start_date")
        end_date = request.POST.get("end_date")
        
        academic_year = AcademicYear.objects.get(pk=academic_year_id, institution=institution)
        
        term = Term.objects.create(
            academic_year=academic_year,
            term_number=int(term_number),
            term_name=term_name,
            start_date=start_date,
            end_date=end_date,
        )
        
        InstitutionAuditLog.objects.create(
            institution=institution,
            actor=request.user,
            action="term_created",
            entity_type="Term",
            entity_id=str(term.pk),
            description=f"Created {term_name}",
        )
        
        messages.success(request, f"Term {term_name} created successfully!")
        return redirect("institutions:academic_structure")
    
    except Exception as e:
        messages.error(request, f"Error creating term: {str(e)}")
        return redirect("institutions:academic_structure")


@login_required
def student_fee_statement(request, student_id):
    """Generate printable student fee statement."""
    institution = get_institution_or_404(request)
    
    student = get_object_or_404(Student, pk=student_id, institution=institution)
    fee_assignments = StudentFeeAssignment.objects.filter(student=student)
    
    context = {
        "institution": institution,
        "student": student,
        "fee_assignments": fee_assignments,
    }
    
    return render(request, "institutions/student_statement.html", context)


@login_required
def fee_reports(request):
    """Fee reports and analytics."""
    institution = get_institution_or_404(request)
    
    # Get active academic year
    active_year = AcademicYear.objects.filter(
        institution=institution, is_active=True
    ).first()
    
    # Get assignments
    assignments = StudentFeeAssignment.objects.filter(
        student__institution=institution,
        academic_year=active_year
    ) if active_year else StudentFeeAssignment.objects.none()
    
    # Calculate statistics
    total_billed = assignments.aggregate(Sum("total_fees"))["total_fees__sum"] or 0
    total_paid = assignments.aggregate(Sum("amount_paid"))["amount_paid__sum"] or 0
    
    context = {
        "institution": institution,
        "active_year": active_year,
        "total_billed": total_billed,
        "total_paid": total_paid,
        "total_outstanding": total_billed - total_paid,
        "collection_rate": (total_paid / total_billed * 100) if total_billed > 0 else 0,
        "assignments": assignments.order_by("-created_at"),
    }
    
    return render(request, "institutions/reports.html", context)
