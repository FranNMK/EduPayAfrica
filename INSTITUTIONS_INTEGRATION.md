# Institutions App - Integration Reference

## URL Endpoints

### Dashboard & Navigation
```
GET  /institution/                          - Institution Dashboard
GET  /institution/profile/                  - Institution Profile
POST /institution/profile/                  - Update Profile
```

### Academic Structure
```
GET  /institution/academic-structure/       - Academic Structure Overview
POST /institution/academic-year/add/        - Create Academic Year (AJAX)
POST /institution/term/add/                 - Create Term (AJAX)
```

### Student Management
```
GET  /institution/students/                 - Student Management
POST /institution/students/add/             - Add Single Student (AJAX)
POST /institution/students/bulk-upload/     - Upload CSV
```

### Fee Management
```
GET  /institution/fees/                     - Fee Structure View
GET  /institution/reports/                  - Financial Reports
GET  /institution/student/<id>/statement/   - Student Fee Statement
```

## View Functions

### Dashboard View
```python
@login_required
def institution_dashboard(request):
    """Returns dashboard with KPIs"""
    Returns:
        - students_count: Active student count
        - active_academic_year: Current year
        - total_fees_billed: Sum of all fees
        - total_outstanding: Outstanding balance
        - overdue_count: Overdue assignments
```

### Add Academic Year
```python
@login_required
@require_http_methods(["POST"])
def add_academic_year(request):
    """
    POST Parameters:
    - year_code: "2025/2026"
    - start_date: "2025-01-01"
    - end_date: "2025-12-31"
    - is_active: "on" (checkbox)
    
    Returns: JSON {"success": bool, "message": str}
    """
```

### Add Student
```python
@login_required
@require_http_methods(["POST"])
def add_student(request):
    """
    POST Parameters:
    - full_name: "John Doe"
    - admission_number: "ADM001"
    - email: "john@example.com" (optional)
    - program_id: 1
    - academic_year_id: 1
    
    Returns: JSON {"success": bool, "student_id": int|null}
    """
```

### Bulk Upload Students
```python
@login_required
def bulk_upload_students(request):
    """
    POST Parameters:
    - csv_file: File upload
    
    CSV Format:
    full_name,admission_number,email,program_id,academic_year_id
    "John Doe","ADM001","john@example.com",1,1
    
    Returns: Redirect with success/error messages
    """
```

## Python Usage Examples

### Create Institution Profile
```python
from institutions.models import InstitutionProfile
from django.contrib.auth.models import User

user = User.objects.get(email="admin@institution.com")
institution = InstitutionProfile.objects.create(
    user=user,
    institution_name="ABC University",
    institution_type="university",
    contact_email="contact@abc.edu",
    phone_number="+256 700 000000",
    address="Kampala, Uganda"
)
```

### Create Academic Year
```python
from institutions.models import AcademicYear

year = AcademicYear.objects.create(
    institution=institution,
    year_code="2025/2026",
    start_date="2025-01-01",
    end_date="2025-12-31",
    is_active=True
)
```

### Create Term
```python
from institutions.models import Term

term = Term.objects.create(
    academic_year=year,
    term_number=1,
    term_name="First Semester",
    start_date="2025-01-01",
    end_date="2025-05-31"
)
```

### Register Student
```python
from institutions.models import Student

student = Student.objects.create(
    institution=institution,
    program=program,
    academic_year=year,
    full_name="Jane Smith",
    admission_number="ADM001",
    email="jane@example.com"
)
```

### Create Fee Structure
```python
from institutions.models import FeeStructure, FeeItem

structure = FeeStructure.objects.create(
    institution=institution,
    version=1
)

# Add fee items
FeeItem.objects.create(
    fee_structure=structure,
    name="Tuition",
    fee_type="tuition",
    amount=5000000,  # in base currency
    is_mandatory=True
)

FeeItem.objects.create(
    fee_structure=structure,
    name="Accommodation",
    fee_type="accommodation",
    amount=1000000,
    is_mandatory=False
)
```

### Assign Fees to Student
```python
from institutions.models import StudentFeeAssignment

assignment = StudentFeeAssignment.objects.create(
    student=student,
    fee_structure=structure,
    academic_year=year,
    term=term,
    total_fees=6000000,  # tuition + accommodation
    discount_amount=0,
    penalty_amount=0,
    amount_paid=0,
    due_date="2025-05-31"
)

# Check outstanding balance
print(assignment.outstanding_balance)  # 6000000.00
print(assignment.is_paid_in_full)      # False
```

### Record Payment (Bursar)
```python
# Record a manual payment
assignment.amount_paid = 3000000
assignment.save()

# Check new balance
print(assignment.outstanding_balance)  # 3000000.00
print(assignment.is_paid_in_full)      # False

# Record full payment
assignment.amount_paid = 6000000
assignment.save()

print(assignment.is_paid_in_full)      # True
```

### Apply Discount
```python
# Apply 500,000 discount
assignment.discount_amount = 500000
assignment.total_fees = 5500000  # Adjusted total
assignment.save()

print(assignment.outstanding_balance)  # 5500000 - 500000 = 5000000
```

### Apply Penalty
```python
# Apply penalty for late payment
assignment.penalty_amount = 250000
assignment.save()

print(assignment.outstanding_balance)  # 5500000 - 500000 + 250000 = 5250000
```

### Query Outstanding Fees
```python
from django.db.models import F, Q, Sum

# Get all outstanding fees
outstanding = StudentFeeAssignment.objects.filter(
    student__institution=institution,
    amount_paid__lt=F('total_fees') - F('discount_amount') + F('penalty_amount')
)

# Get overdue records
overdue = StudentFeeAssignment.objects.filter(
    student__institution=institution,
    is_overdue=True
)

# Get total outstanding
total_outstanding = StudentFeeAssignment.objects.filter(
    student__institution=institution
).aggregate(
    total=Sum(
        F('total_fees') - F('discount_amount') + F('penalty_amount') - F('amount_paid')
    )
)['total']
```

### Generate Collection Statistics
```python
from django.db.models import Sum

assignments = StudentFeeAssignment.objects.filter(
    student__institution=institution,
    academic_year=current_year
)

stats = assignments.aggregate(
    total_billed=Sum('total_fees'),
    total_paid=Sum('amount_paid'),
    total_outstanding=Sum(
        F('total_fees') - F('discount_amount') + F('penalty_amount') - F('amount_paid')
    ),
    collection_rate=Case(
        When(total_billed__gt=0, then=(Sum('amount_paid') * 100) / Sum('total_fees')),
        default=0
    )
)

print(f"Billed: {stats['total_billed']}")
print(f"Paid: {stats['total_paid']}")
print(f"Outstanding: {stats['total_outstanding']}")
print(f"Collection Rate: {stats['collection_rate']:.1f}%")
```

### Log Institutional Changes
```python
from institutions.models import InstitutionAuditLog

InstitutionAuditLog.objects.create(
    institution=institution,
    actor=request.user,
    action="fee_structure_changed",
    entity_type="FeeStructure",
    entity_id=str(structure.pk),
    description="Updated tuition fee for 2025/2026",
    changes={"old_amount": 5000000, "new_amount": 5500000}
)
```

## Django ORM Query Examples

### Get institution with related data
```python
# Get all data for an institution
institution = InstitutionProfile.objects.prefetch_related(
    'academic_years',
    'academic_years__terms',
    'faculties',
    'faculties__programs',
    'students',
    'students__fee_assignments'
).get(pk=institution_id)
```

### Get student with fee history
```python
student = Student.objects.select_related(
    'institution',
    'program',
    'academic_year'
).prefetch_related(
    'fee_assignments'
).get(pk=student_id)

for assignment in student.fee_assignments.all():
    print(f"{assignment.academic_year}: {assignment.outstanding_balance}")
```

### Filter by date range
```python
from datetime import datetime, timedelta

# Get fees due in next 30 days
upcoming = StudentFeeAssignment.objects.filter(
    due_date__gte=datetime.now().date(),
    due_date__lte=(datetime.now() + timedelta(days=30)).date()
)
```

## Signal Handlers (Optional)

```python
# Add to models.py if needed
from django.db.models.signals import pre_save
from django.dispatch import receiver

@receiver(pre_save, sender=StudentFeeAssignment)
def update_overdue_status(sender, instance, **kwargs):
    """Auto-update overdue status before save"""
    if instance.due_date and instance.due_date < datetime.now().date():
        if not instance.is_paid_in_full:
            instance.is_overdue = True
```

## Template Tags (Custom)

```django
{# In templates #}
{{ assignment.outstanding_balance|floatformat:2 }}
{{ assignment.is_paid_in_full|yesno:"Paid,Pending" }}
{% if assignment.is_overdue %}
    <span class="badge bg-danger">Overdue</span>
{% endif %}
```

## Error Handling

```python
from django.core.exceptions import ValidationError
from django.db import IntegrityError

try:
    academic_year = AcademicYear(
        institution=institution,
        year_code="2025/2026",
        start_date="2025-12-31",  # Error: after end date
        end_date="2025-01-01"
    )
    academic_year.full_clean()  # Validation error
    academic_year.save()
except ValidationError as e:
    print(f"Validation error: {e}")
except IntegrityError as e:
    print(f"Duplicate entry: {e}")
```

---

**Last Updated**: January 23, 2026  
**API Version**: 1.0  
**Status**: Production Ready
