# Role-Based Institution Management System - Implementation Guide

## Overview

This document describes the implementation of a comprehensive role-based access control system for the EduPayAfrica Institutions App. Staff members now have specific roles with tailored dashboards and functionality.

## Implemented Roles

### 1. **Institution Admin**
- **Permissions**: Full system access
- **Primary Responsibilities**:
  - Add and manage staff members (all roles)
  - Student management (add, bulk upload, view)
  - Create and manage academic structure
  - Monitor overall institutional operations
  
**Dashboard Features**:
- Total students count
- Total fees billed
- Outstanding balance overview
- Overdue fees tracking
- Quick action buttons to access all management panels
- Staff member list with status

**Key Views**:
- `/institution/staff/` - Staff management
- `/institution/students/` - Student management
- `/institution/academic-structure/` - Academic calendar management
- `/institution/programs/` - Academic program management

---

### 2. **Principal**
- **Permissions**: View students, send messages, view analytics
- **Primary Responsibilities**:
  - Send mass messages to parents about fees
  - View fee collection analytics
  - Monitor institutional performance
  - Send reminders for overdue fees

**Dashboard Features**:
- Messages sent count
- Staff member count
- Active academic year display
- Recent messages with recipient count

**Key Views**:
- `/institution/messages/` - Messaging panel
  - Send message by type (reminder, urgent, announcement, congratulation)
  - Target recipients (all students, overdue only, specific students)
  - Message history
- `/institution/fee-analysis/` - Fee analytics
  - Collection rate, payment status breakdown
  - Student-level fee details

**Message Types**:
- **Reminder**: Fee payment due soon
- **Urgent**: Immediate payment required
- **Announcement**: General school announcements
- **Congratulation**: Academic achievement notifications

---

### 3. **Bursar / Finance Officer**
- **Permissions**: Financial management, fee structure setup
- **Primary Responsibilities**:
  - Define fee structures for different programs
  - Create modular and non-modular fee templates
  - Manage program fee configurations
  - View collection analytics

**Dashboard Features**:
- Total fees billed
- Total fees collected
- Outstanding balance
- Collection rate percentage
- Active programs list
- Fee structure versions

**Key Views**:
- `/institution/fee-structures/` - Fee structure management
  - Create fee structures with multiple fee items
  - Version control for fee changes
  - Support for flexible fee types (tuition, accommodation, etc.)
- `/institution/programs/` - Program management
  - Create programs with modular/non-modular options
  - Set program duration
  - Assign to faculties
  - Track program types (modular, non-modular, semester-based, year-round)
- `/institution/fee-analysis/` - Fee analytics

**Fee Structure Features**:
- Version-based versioning for tracking changes
- Multiple fee items per structure
- Flexible fee types (tuition, accommodation, technology, etc.)
- Mandatory vs optional fees
- Per-program customization

---

### 4. **Teacher**
- **Permissions**: View student data
- **Primary Responsibilities**:
  - View student list
  - Access to basic institutional information
  - (More features coming in future phases)

**Dashboard Features**:
- Total student count
- Active academic year
- Institution name
- Placeholder for future features (class management, attendance, grading)

---

### 5. **Accountant**
- **Permissions**: Same as Bursar (financial management)
- **Primary Responsibilities**:
  - Same as Bursar role

---

### 6. **Registrar** & **Deputy Principal** & **Support Staff**
- **Permissions**: Generic access
- **Primary Responsibilities**:
  - Receive generic dashboard with basic navigation
  - (Can be extended with specific functionality)

---

## Data Models

### New Models Added

#### **InstitutionStaff**
```python
class InstitutionStaff(models.Model):
    institution = ForeignKey(InstitutionProfile)
    user = ForeignKey(User)  # Unique per institution
    full_name = CharField
    role = CharField(choices=ROLE_CHOICES)  # admin, principal, bursar, etc.
    email = EmailField
    phone_number = CharField
    is_active = BooleanField
    date_hired = DateField
    created_at, updated_at = DateTimeField
```

#### **ParentGuardian**
```python
class ParentGuardian(models.Model):
    student = ForeignKey(Student)
    full_name = CharField
    relationship = CharField(choices=RELATIONSHIP_CHOICES)
    email = EmailField
    phone_number = CharField
    is_primary_contact = BooleanField
```

#### **PrincipalMessage**
```python
class PrincipalMessage(models.Model):
    institution = ForeignKey(InstitutionProfile)
    sent_by = ForeignKey(InstitutionStaff)  # Must be principal
    subject = CharField
    message_type = CharField(choices=['reminder', 'urgent', 'announcement', 'congratulation'])
    content = TextField
    target_students = ManyToManyField(Student)
    is_active = BooleanField
    sent_date = DateTimeField
```

#### **FeeAnalysisSnapshot**
```python
class FeeAnalysisSnapshot(models.Model):
    institution = ForeignKey(InstitutionProfile)
    academic_year = ForeignKey(AcademicYear)
    total_students = IntegerField
    total_fees_billed = DecimalField
    total_fees_paid = DecimalField
    total_outstanding = DecimalField
    overdue_count = IntegerField
    fully_paid_count = IntegerField
    partially_paid_count = IntegerField
    not_paid_count = IntegerField
    collection_rate = DecimalField  # Percentage
    snapshot_date = DateField
```

#### **Enhanced Program Model**
```python
class Program(models.Model):
    institution = ForeignKey(InstitutionProfile)
    faculty = ForeignKey(Faculty)
    program_name = CharField
    program_code = CharField
    program_type = CharField(choices=['modular', 'non_modular', 'semester', 'year_round'])
    duration_months = IntegerField
    description = TextField
    is_active = BooleanField
```

---

## Views & URL Structure

### Access Control Decorator
```python
@require_role("admin", "bursar")
def some_view(request):
    """Only admin and bursar can access"""
    pass
```

### URL Routes
```
/institution/                       - Dashboard (role-specific)
/institution/staff/                 - Staff management (admin only)
/institution/staff/add/             - Add staff (admin only)
/institution/programs/              - Program management (admin, bursar, accountant)
/institution/programs/add/          - Add program (admin, bursar, accountant)
/institution/fee-structures/        - Fee management (bursar, accountant only)
/institution/fee-structures/create/ - Create fee structure (bursar, accountant only)
/institution/messages/              - Messaging panel (principal only)
/institution/messages/send/         - Send message (principal only)
/institution/fee-analysis/          - Fee analytics (principal, bursar, accountant)
```

---

## Feature Implementations

### 1. Staff Management (Admin)
**Endpoint**: `POST /institution/staff/add/`

**Parameters**:
- `full_name`: Staff member's full name
- `email`: Email address (used to create/link user account)
- `phone_number`: Contact number
- `role`: Staff role (admin, principal, bursar, teacher, accountant, registrar, deputy_principal, support_staff)

**Functionality**:
- Auto-creates Django User if doesn't exist
- Creates InstitutionStaff record with role assignment
- Logs action to InstitutionAuditLog
- Supports adding multiple staff members

**Example**:
```python
staff = InstitutionStaff.objects.create(
    institution=institution,
    user=user,
    full_name="John Doe",
    role="bursar",
    email="john@institution.edu",
    phone_number="+256 700 123456"
)
```

---

### 2. Program Management (Bursar/Accountant)
**Endpoint**: `POST /institution/programs/add/`

**Parameters**:
- `program_name`: "Bachelor of Science in Computer Science"
- `program_code`: "BSC-CS"
- `program_type`: "modular" | "non_modular" | "semester" | "year_round"
- `faculty_id`: Faculty the program belongs to
- `duration_months`: Program length in months (default: 12)
- `description`: Program description

**Functionality**:
- Creates Program linked to institution
- Supports multiple program types
- Enables flexible duration configuration
- Allows multiple programs per faculty

**Program Types**:
- **Modular**: Structured in modules/blocks
- **Non-Modular**: Year/semester-based structure
- **Semester-Based**: Semester system (2-3 per year)
- **Year Round**: Continuous enrollment

---

### 3. Fee Structure Management (Bursar/Accountant)
**Endpoint**: `POST /institution/fee-structures/create/`

**Parameters**:
- `version`: Structure version number
- `fee_name[]`: Array of fee item names
- `fee_type[]`: Array of fee types (tuition, accommodation, etc.)
- `fee_amount[]`: Array of fee amounts
- `fee_mandatory[]`: Array of mandatory flags

**Functionality**:
- Creates versioned fee structure
- Supports multiple fee items per structure
- Tracks version history for compliance
- Links to institutions for multi-institutional support

**Fee Item Structure**:
```python
FeeItem.objects.create(
    fee_structure=structure,
    name="Tuition",
    fee_type="tuition",
    amount=5000000,
    is_mandatory=True
)
```

---

### 4. Messaging System (Principal)
**Endpoint**: `POST /institution/messages/send/`

**Parameters**:
- `subject`: Message subject
- `content`: Message body
- `message_type`: "reminder" | "urgent" | "announcement" | "congratulation"
- `target_type`: "all" | "overdue" | "specific"
- `student_ids[]`: Student IDs if specific targeting

**Functionality**:
- Send mass messages to parents
- Target by student payment status
- Message type tracking
- Audit trail of all messages
- Recipient count tracking

**Automatic Targeting**:
```python
# Target students with overdue fees
if target_type == "overdue":
    students = Student.objects.filter(
        fee_assignments__is_overdue=True,
        is_active=True
    ).distinct()

# Target all active students
elif target_type == "all":
    students = Student.objects.filter(
        institution=institution,
        is_active=True
    )
```

---

### 5. Fee Analysis Dashboard (Principal, Bursar, Accountant)
**Endpoint**: `GET /institution/fee-analysis/`

**Metrics Displayed**:
- Total students
- Total fees billed
- Total fees collected
- Outstanding balance
- Collection rate percentage
- Payment status breakdown:
  - Fully paid students
  - Partially paid students
  - Not paid students
  - Overdue cases

**Data Visualization**:
- Progress bars for payment statuses
- Summary cards for KPIs
- Detailed table of student fees
- Key insights panel

---

## Excel/CSV Upload Enhancement

**Endpoint**: `POST /institution/students/bulk-upload/`

**File Format**:
```
Full Name,Admission Number,Email,Program Code,Academic Year Code
John Doe,ADM001,john@example.com,BSC-CS,2025/2026
Jane Smith,ADM002,jane@example.com,BSC-CS,2025/2026
```

**Features**:
- Support for both Excel (.xlsx) and CSV formats
- Error reporting with row numbers
- Partial success handling
- Audit logging of bulk uploads

**Error Handling**:
```python
for row_idx, row in enumerate(reader, 2):
    try:
        # Parse row and create student
        students_added += 1
    except Exception as e:
        errors.append(f"Row {row_idx}: {str(e)}")
```

---

## Database Schema Relationships

```
InstitutionProfile
├── InstitutionStaff (role-based access)
│   └── PrincipalMessage (principal sends)
├── Student
│   ├── ParentGuardian (contact info)
│   └── StudentFeeAssignment
│       ├── FeeStructure
│       │   └── FeeItem
│       └── AcademicYear
├── Program (modular/non-modular)
│   ├── Faculty
│   └── Student
├── AcademicYear
│   ├── Term
│   └── FeeAnalysisSnapshot
└── InstitutionAuditLog (all actions)
```

---

## Security & Access Control

### Role-Based Access Control (RBAC)
```python
def require_role(*allowed_roles):
    """Decorator to enforce role-based access"""
    def decorator(view_func):
        def wrapper(request, *args, **kwargs):
            institution = get_institution_or_404(request)
            staff_role = get_staff_role(request, institution)
            if staff_role not in allowed_roles:
                messages.error(request, "Insufficient permissions")
                return redirect("institution_dashboard")
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator
```

### Institution-Level Isolation
All views filter data by institution to prevent cross-institutional data leakage:
```python
# All queries scoped to user's institution
students = Student.objects.filter(institution=institution)
```

### Audit Logging
Every action is logged:
```python
InstitutionAuditLog.objects.create(
    institution=institution,
    actor=request.user,
    action="staff_added",
    entity_type="InstitutionStaff",
    description=f"Added {full_name} as {role}"
)
```

---

## Migration Information

### New Tables Created
- `institutions_institutionstaff`
- `institutions_parentguardian`
- `institutions_principalmessage`
- `institutions_feeanalysissnapshot`
- `institutions_principalmessage_target_students` (M2M)

### Updated Tables
- `institutions_program` (added institution, program_type, duration_months, renamed fields)

### Migration Command
```bash
python manage.py makemigrations institutions
python manage.py migrate institutions
```

---

## Testing Workflow

### 1. Create Institution
```python
user = User.objects.create_user(email='admin@institution.edu')
institution = InstitutionProfile.objects.create(
    user=user,
    institution_name="Test University",
    institution_type="university"
)
```

### 2. Add Staff with Different Roles
```python
# Add admin
admin = InstitutionStaff.objects.create(
    institution=institution,
    user=admin_user,
    role="admin"
)

# Add principal
principal = InstitutionStaff.objects.create(
    institution=institution,
    user=principal_user,
    role="principal"
)

# Add bursar
bursar = InstitutionStaff.objects.create(
    institution=institution,
    user=bursar_user,
    role="bursar"
)
```

### 3. Create Programs
```python
program = Program.objects.create(
    institution=institution,
    faculty=faculty,
    program_name="Bachelor of Science in Computer Science",
    program_code="BSC-CS",
    program_type="non_modular",
    duration_months=48
)
```

### 4. Create Fee Structure
```python
fee_structure = FeeStructure.objects.create(institution=institution, version=1)
FeeItem.objects.create(
    fee_structure=fee_structure,
    name="Tuition",
    fee_type="tuition",
    amount=5000000,
    is_mandatory=True
)
```

### 5. Add Students
```python
student = Student.objects.create(
    institution=institution,
    program=program,
    academic_year=year,
    full_name="Test Student",
    admission_number="STU001"
)
```

### 6. Assign Fees
```python
assignment = StudentFeeAssignment.objects.create(
    student=student,
    fee_structure=fee_structure,
    academic_year=year,
    term=term,
    total_fees=5000000,
    amount_paid=0,
    due_date="2026-05-31"
)
```

### 7. Send Message (Principal)
```python
message = PrincipalMessage.objects.create(
    institution=institution,
    sent_by=principal_staff,
    subject="Fee Payment Reminder",
    message_type="reminder",
    content="Please pay your fees..."
)
message.target_students.add(student)
```

---

## Next Phase Features

1. **SMS/Email Notifications**
   - Send SMS reminders via Twilio
   - Email notifications to parents
   - Automated reminder scheduling

2. **Payment Integration**
   - M-Pesa integration
   - Bank transfer processing
   - Card payment gateway

3. **Student Parent Portal**
   - Student login to view fees
   - Parent portal for monitoring
   - Payment history tracking

4. **Advanced Analytics**
   - Departmental fee reports
   - Trend analysis
   - Predictive payment behavior

5. **Refund Management**
   - Process refunds
   - Track refund history
   - Reconciliation

---

## Troubleshooting

### Staff can't see their dashboard
- Check InstitutionStaff record exists
- Verify user is linked correctly
- Check is_active flag is True

### Messages not sending
- Verify principal role assignment
- Check target_students are set
- Review audit logs for errors

### Program creation fails
- Ensure faculty exists
- Check institution assignment
- Verify program_code is unique

### Fee structure issues
- Confirm FeeItem objects created
- Check amounts are positive
- Verify fee structure linked to institution

---

## Admin Interface

All new models are registered in Django admin with:
- Custom list displays
- Filters by institution
- Search functionality
- Read-only audit fields
- M2M filters for PrincipalMessage

**Access at**: `/admin/institutions/`

---

**Last Updated**: January 23, 2026  
**Version**: 2.0 - Role-Based System
