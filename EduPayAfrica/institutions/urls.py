from django.urls import path
from . import views

app_name = "institutions"

urlpatterns = [
    # Dashboard
    path("", views.institution_dashboard, name="dashboard"),
    
    # Profile Management
    path("profile/", views.profile_management, name="profile"),
    
    # Staff Management (Admin only)
    path("staff/", views.staff_management, name="staff_management"),
    path("staff/add/", views.add_staff, name="add_staff"),
    
    # Academic Structure
    path("academic-structure/", views.academic_structure, name="academic_structure"),
    path("academic-year/add/", views.add_academic_year, name="add_academic_year"),
    path("term/add/", views.add_term, name="add_term"),
    
    # Student Management
    path("students/", views.student_management, name="students"),
    path("students/add/", views.add_student, name="add_student"),
    path("students/bulk-upload/", views.bulk_upload_students, name="bulk_upload_students"),
    
    # Program Management
    path("programs/", views.program_management, name="program_management"),
    path("programs/add/", views.add_program, name="add_program"),
    
    # Fee Structure Management (Bursar/Accountant)
    path("fee-structures/", views.fee_structure_management, name="fee_structure_management"),
    path("fee-structures/create/", views.create_fee_structure, name="create_fee_structure"),
    
    # Messaging (Principal only)
    path("messages/", views.messaging_panel, name="messaging_panel"),
    path("messages/send/", views.send_message, name="send_message"),
    
    # Fee Analysis Dashboard
    path("fee-analysis/", views.fee_analysis_dashboard, name="fee_analysis"),
    
    # Reports
    path("reports/", views.fee_reports, name="reports"),
    path("student/<int:student_id>/statement/", views.student_fee_statement, name="student_statement"),
]
