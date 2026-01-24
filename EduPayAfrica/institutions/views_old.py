from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Sum, F
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_http_methods
from datetime import datetime
import csv

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
)


def get_institution_or_404(request):
    """Get institution profile for current user."""
    try:
        return request.user.institution_profile
    except InstitutionProfile.DoesNotExist:
        return None


@login_required
def institution_dashboard(request):
    """Institution Admin/Bursar Dashboard."""
    institution = get_institution_or_404(request)
    if not institution:
        messages.error(request, "You don't have an institution profile.")
        return redirect("home")
    
    # Get dashboard statistics
    students_count = Student.objects.filter(institution=institution, is_active=True).count()
    active_academic_year = AcademicYear.objects.filter(
        institution=institution, is_active=True
    ).first()
    
    total_fees_billed = StudentFeeAssignment.objects.filter(
        student__institution=institution
    ).aggregate(total=Sum("total_fees"))["total"] or 0
    
    total_outstanding = StudentFeeAssignment.objects.filter(
        student__institution=institution
    ).aggregate(
        outstanding=Sum(
            F("total_fees") - F("discount_amount") + F("penalty_amount") - F("amount_paid")
        )
    )["outstanding"] or 0
    
    overdue_count = StudentFeeAssignment.objects.filter(
        student__institution=institution, is_overdue=True
    ).count()
    
    context = {
        "institution": institution,
        "students_count": students_count,
        "active_academic_year": active_academic_year,
        "total_fees_billed": total_fees_billed,
        "total_outstanding": total_outstanding,
        "overdue_count": overdue_count,
    }
    
    return render(request, "institutions/dashboard.html", context)


@login_required
def profile_management(request):
    """Institution Profile Management."""
    institution = get_institution_or_404(request)
    if not institution:
        messages.error(request, "You don't have an institution profile.")
        return redirect("home")
    
    if request.method == "POST":
        institution.contact_email = request.POST.get("contact_email", institution.contact_email)
        institution.phone_number = request.POST.get("phone_number", institution.phone_number)
        institution.address = request.POST.get("address", institution.address)
        
        if request.FILES.get("logo_url"):
            institution.logo_url = request.FILES["logo_url"]
        
        institution.save()
        
        InstitutionAuditLog.objects.create(
            institution=institution,
            actor=request.user,
            action="institution_updated",
            description=f"Updated institution profile",
        )
        
        messages.success(request, "Institution profile updated successfully.")
        return redirect("institutions:profile")
    
    context = {"institution": institution}
    return render(request, "institutions/profile.html", context)


@login_required
def academic_structure(request):
    """Academic Structure Management (Years, Terms, Faculties, Programs)."""
    institution = get_institution_or_404(request)
    if not institution:
        messages.error(request, "You don't have an institution profile.")
        return redirect("home")
    
    academic_years = AcademicYear.objects.filter(institution=institution)
    faculties = Faculty.objects.filter(institution=institution)
    programs = Program.objects.filter(faculty__institution=institution)
    
    context = {
        "institution": institution,
        "academic_years": academic_years,
        "faculties": faculties,
        "programs": programs,
    }
    
    return render(request, "institutions/academic_structure.html", context)


@login_required
@require_http_methods(["POST"])
def add_academic_year(request):
    """Add new academic year."""
    institution = get_institution_or_404(request)
    if not institution:
        return JsonResponse({"success": False, "message": "No institution profile"})
    
    year_code = request.POST.get("year_code", "").strip()
    start_date = request.POST.get("start_date", "").strip()
    end_date = request.POST.get("end_date", "").strip()
    is_active = request.POST.get("is_active") == "on"
    
    if not all([year_code, start_date, end_date]):
        return JsonResponse({"success": False, "message": "All fields are required"})
    
    try:
        from django.core.exceptions import ValidationError
        
        academic_year = AcademicYear(
            institution=institution,
            year_code=year_code,
            start_date=start_date,
            end_date=end_date,
            is_active=is_active,
        )
        academic_year.full_clean()
        academic_year.save()
        
        if is_active:
            AcademicYear.objects.filter(institution=institution).exclude(
                pk=academic_year.pk
            ).update(is_active=False)
        
        InstitutionAuditLog.objects.create(
            institution=institution,
            actor=request.user,
            action="academic_year_created",
            entity_type="AcademicYear",
            entity_id=str(academic_year.pk),
            description=f"Created academic year {year_code}",
        )
        
        messages.success(request, f"Academic year {year_code} added successfully.")
        return JsonResponse({"success": True})
    except Exception as e:
        return JsonResponse({"success": False, "message": str(e)})


@login_required
@require_http_methods(["POST"])
def add_term(request):
    """Add term to academic year."""
    institution = get_institution_or_404(request)
    if not institution:
        return JsonResponse({"success": False, "message": "No institution profile"})
    
    academic_year_id = request.POST.get("academic_year_id")
    term_number = request.POST.get("term_number")
    term_name = request.POST.get("term_name", "").strip()
    start_date = request.POST.get("start_date")
    end_date = request.POST.get("end_date")
    
    try:
        academic_year = AcademicYear.objects.get(pk=academic_year_id, institution=institution)
        
        term = Term.objects.create(
            academic_year=academic_year,
            term_number=term_number,
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
            description=f"Created term {term_number} for {academic_year.year_code}",
        )
        
        messages.success(request, f"Term {term_number} added successfully.")
        return JsonResponse({"success": True})
    except AcademicYear.DoesNotExist:
        return JsonResponse({"success": False, "message": "Academic year not found"})
    except Exception as e:
        return JsonResponse({"success": False, "message": str(e)})


@login_required
def student_management(request):
    """Student Management (Registration, Bulk Upload, View)."""
    institution = get_institution_or_404(request)
    if not institution:
        messages.error(request, "You don't have an institution profile.")
        return redirect("home")
    
    students = Student.objects.filter(institution=institution)
    academic_years = AcademicYear.objects.filter(institution=institution)
    programs = Program.objects.filter(faculty__institution=institution)
    
    context = {
        "institution": institution,
        "students": students,
        "academic_years": academic_years,
        "programs": programs,
    }
    
    return render(request, "institutions/students.html", context)


@login_required
@require_http_methods(["POST"])
def add_student(request):
    """Manually add a student."""
    institution = get_institution_or_404(request)
    if not institution:
        return JsonResponse({"success": False, "message": "No institution profile"})
    
    full_name = request.POST.get("full_name", "").strip()
    admission_number = request.POST.get("admission_number", "").strip()
    email = request.POST.get("email", "").strip()
    program_id = request.POST.get("program_id")
    academic_year_id = request.POST.get("academic_year_id")
    
    if not all([full_name, admission_number, program_id, academic_year_id]):
        return JsonResponse({"success": False, "message": "Required fields missing"})
    
    try:
        program = Program.objects.get(pk=program_id, faculty__institution=institution)
        academic_year = AcademicYear.objects.get(pk=academic_year_id, institution=institution)
        
        student = Student.objects.create(
            institution=institution,
            full_name=full_name,
            admission_number=admission_number,
            email=email,
            program=program,
            academic_year=academic_year,
        )
        
        InstitutionAuditLog.objects.create(
            institution=institution,
            actor=request.user,
            action="student_added",
            entity_type="Student",
            entity_id=str(student.pk),
            description=f"Added student {full_name} ({admission_number})",
        )
        
        messages.success(request, f"Student {full_name} added successfully.")
        return JsonResponse({"success": True, "student_id": student.pk})
    except Exception as e:
        return JsonResponse({"success": False, "message": str(e)})


@login_required
def bulk_upload_students(request):
    """Bulk upload students from CSV."""
    if request.method == "POST":
        institution = get_institution_or_404(request)
        if not institution:
            messages.error(request, "No institution profile")
            return redirect("institutions:students")
        
        csv_file = request.FILES.get("csv_file")
        if not csv_file:
            messages.error(request, "No file selected")
            return redirect("institutions:students")
        
        try:
            decoded_file = csv_file.read().decode("utf-8").splitlines()
            reader = csv.DictReader(decoded_file)
            
            created_count = 0
            error_count = 0
            
            for row in reader:
                try:
                    program = Program.objects.get(pk=row["program_id"], faculty__institution=institution)
                    academic_year = AcademicYear.objects.get(pk=row["academic_year_id"], institution=institution)
                    
                    Student.objects.get_or_create(
                        institution=institution,
                        admission_number=row["admission_number"],
                        defaults={
                            "full_name": row["full_name"],
                            "email": row.get("email", ""),
                            "program": program,
                            "academic_year": academic_year,
                        },
                    )
                    created_count += 1
                except Exception as e:
                    error_count += 1
            
            InstitutionAuditLog.objects.create(
                institution=institution,
                actor=request.user,
                action="student_added",
                description=f"Bulk uploaded {created_count} students, {error_count} errors",
            )
            
            messages.success(request, f"Uploaded {created_count} students successfully.")
            return redirect("institutions:students")
        except Exception as e:
            messages.error(request, f"Error uploading file: {str(e)}")
            return redirect("institutions:students")
    
    return redirect("institutions:students")


@login_required
def fee_management(request):
    """Fee Structure and Assignment Management."""
    institution = get_institution_or_404(request)
    if not institution:
        messages.error(request, "You don't have an institution profile.")
        return redirect("home")
    
    fee_structures = FeeStructure.objects.filter(institution=institution)
    students = Student.objects.filter(institution=institution)
    
    context = {
        "institution": institution,
        "fee_structures": fee_structures,
        "students": students,
    }
    
    return render(request, "institutions/fees.html", context)


@login_required
def fee_reports(request):
    """Financial Reports (Fee Summaries, Balances, Student Statements)."""
    institution = get_institution_or_404(request)
    if not institution:
        messages.error(request, "You don't have an institution profile.")
        return redirect("home")
    
    # Get fee data
    fee_assignments = StudentFeeAssignment.objects.filter(student__institution=institution)
    total_billed = fee_assignments.aggregate(Sum("total_fees"))["total_fees__sum"] or 0
    total_paid = fee_assignments.aggregate(Sum("amount_paid"))["amount_paid__sum"] or 0
    total_outstanding = total_billed - total_paid
    
    context = {
        "institution": institution,
        "fee_assignments": fee_assignments,
        "total_billed": total_billed,
        "total_paid": total_paid,
        "total_outstanding": total_outstanding,
    }
    
    return render(request, "institutions/reports.html", context)


@login_required
def student_fee_statement(request, student_id):
    """Generate student fee statement (PDF/Export)."""
    institution = get_institution_or_404(request)
    if not institution:
        messages.error(request, "You don't have an institution profile.")
        return redirect("home")
    
    student = get_object_or_404(Student, pk=student_id, institution=institution)
    fee_assignments = StudentFeeAssignment.objects.filter(student=student)
    
    context = {
        "institution": institution,
        "student": student,
        "fee_assignments": fee_assignments,
    }
    
    # For now, render as HTML. Later can add PDF generation
    return render(request, "institutions/student_statement.html", context)
