# Institutions App - Database Schema

## Entity Relationship Diagram

```
┌──────────────────────────────────────┐
│      InstitutionProfile              │
├──────────────────────────────────────┤
│ id (PK)                              │
│ user_id (FK to User) - unique        │
│ institution_name (immutable)         │
│ institution_type (immutable)         │
│ contact_email (mutable)              │
│ phone_number (mutable)               │
│ address (mutable)                    │
│ logo_url (mutable)                   │
│ is_active                            │
│ created_at, updated_at               │
└──────────────────────────────────────┘
         │                │
         │                ├──────────────────────┐
         │                │                      │
         │                ▼                      ▼
         │        ┌──────────────────┐  ┌──────────────────┐
         │        │  AcademicYear    │  │    Faculty       │
         │        ├──────────────────┤  ├──────────────────┤
         │        │ id (PK)          │  │ id (PK)          │
         │        │ institution_id   │  │ institution_id   │
         │        │ year_code        │  │ name             │
         │        │ start_date       │  │ code             │
         │        │ end_date         │  │ description      │
         │        │ is_active        │  │ is_active        │
         │        └──────────────────┘  └──────────────────┘
         │                │                      │
         │                ▼                      ▼
         │        ┌──────────────────┐  ┌──────────────────┐
         │        │      Term        │  │     Program      │
         │        ├──────────────────┤  ├──────────────────┤
         │        │ id (PK)          │  │ id (PK)          │
         │        │ academic_year_id │  │ faculty_id       │
         │        │ term_number      │  │ name             │
         │        │ term_name        │  │ code             │
         │        │ start_date       │  │ description      │
         │        │ end_date         │  │ duration_years   │
         │        └──────────────────┘  │ is_active        │
         │                                └──────────────────┘
         │                                        │
         └────────────────────┬────────────────────┘
                              │
                              ▼
                     ┌──────────────────┐
                     │     Student      │
                     ├──────────────────┤
                     │ id (PK)          │
                     │ institution_id   │
                     │ program_id       │
                     │ academic_year_id │
                     │ full_name        │
                     │ admission_number │
                     │ email            │
                     │ phone_number     │
                     │ date_of_birth    │
                     │ gender           │
                     │ is_active        │
                     └──────────────────┘
                              │
                              ▼
              ┌──────────────────────────────┐
              │ StudentFeeAssignment         │
              ├──────────────────────────────┤
              │ id (PK)                      │
              │ student_id (FK)              │
              │ fee_structure_id (FK)        │
              │ academic_year_id (FK)        │
              │ term_id (FK, optional)       │
              │ total_fees                   │
              │ discount_amount              │
              │ penalty_amount               │
              │ amount_paid                  │
              │ due_date                     │
              │ is_overdue                   │
              └──────────────────────────────┘

         ┌──────────────────────────────────────┐
         │       FeeStructure                   │
         ├──────────────────────────────────────┤
         │ id (PK)                              │
         │ institution_id (FK)                  │
         │ version (unique with institution)    │
         │ is_active                            │
         │ created_at, updated_at               │
         └──────────────────────────────────────┘
                     │
                     ▼
         ┌──────────────────────────────────────┐
         │         FeeItem                      │
         ├──────────────────────────────────────┤
         │ id (PK)                              │
         │ fee_structure_id (FK)                │
         │ name                                 │
         │ fee_type (tuition, accommodation...) │
         │ amount                               │
         │ is_mandatory                         │
         │ description                          │
         └──────────────────────────────────────┘

         ┌──────────────────────────────────────┐
         │  InstitutionAuditLog                 │
         ├──────────────────────────────────────┤
         │ id (PK)                              │
         │ institution_id (FK)                  │
         │ actor_id (FK to User)                │
         │ action (choices)                     │
         │ entity_type                          │
         │ entity_id                            │
         │ description                          │
         │ changes (JSON)                       │
         │ created_at                           │
         └──────────────────────────────────────┘
```

## Table Specifications

### InstitutionProfile
| Column | Type | Constraints | Notes |
|--------|------|-------------|-------|
| id | AutoField | PK | |
| user_id | ForeignKey | UNIQUE | One-to-one with User |
| institution_name | CharField(255) | | Immutable |
| institution_type | CharField(50) | | Immutable |
| contact_email | EmailField | | Mutable |
| phone_number | CharField(20) | BLANK | |
| address | TextField | BLANK | |
| logo_url | URLField | NULL, BLANK | |
| is_active | BooleanField | Default=True | |
| created_at | DateTimeField | auto_now_add | |
| updated_at | DateTimeField | auto_now | |

### AcademicYear
| Column | Type | Constraints | Notes |
|--------|------|-------------|-------|
| id | AutoField | PK | |
| institution_id | ForeignKey | | CASCADE on delete |
| year_code | CharField(20) | UNIQUE with institution | e.g., "2025/2026" |
| start_date | DateField | | |
| end_date | DateField | | |
| is_active | BooleanField | Default=False | Only one per institution |
| created_at | DateTimeField | auto_now_add | |
| updated_at | DateTimeField | auto_now | |

### Term
| Column | Type | Constraints | Notes |
|--------|------|-------------|-------|
| id | AutoField | PK | |
| academic_year_id | ForeignKey | | CASCADE on delete |
| term_number | IntegerField | UNIQUE with year | 1, 2, or 3 |
| term_name | CharField(100) | BLANK | e.g., "First Semester" |
| start_date | DateField | | |
| end_date | DateField | | |
| created_at | DateTimeField | auto_now_add | |
| updated_at | DateTimeField | auto_now | |

### Faculty
| Column | Type | Constraints | Notes |
|--------|------|-------------|-------|
| id | AutoField | PK | |
| institution_id | ForeignKey | | CASCADE on delete |
| name | CharField(255) | | |
| code | CharField(50) | UNIQUE with institution | |
| description | TextField | BLANK | |
| is_active | BooleanField | Default=True | |
| created_at | DateTimeField | auto_now_add | |
| updated_at | DateTimeField | auto_now | |

### Program
| Column | Type | Constraints | Notes |
|--------|------|-------------|-------|
| id | AutoField | PK | |
| faculty_id | ForeignKey | | CASCADE on delete |
| name | CharField(255) | | |
| code | CharField(50) | UNIQUE with faculty | |
| description | TextField | BLANK | |
| duration_years | IntegerField | Min=1 | Default=4 |
| is_active | BooleanField | Default=True | |
| created_at | DateTimeField | auto_now_add | |
| updated_at | DateTimeField | auto_now | |

### Student
| Column | Type | Constraints | Notes |
|--------|------|-------------|-------|
| id | AutoField | PK | |
| institution_id | ForeignKey | | CASCADE on delete |
| program_id | ForeignKey | NULL | SET_NULL on delete |
| academic_year_id | ForeignKey | NULL | SET_NULL on delete |
| full_name | CharField(255) | | |
| admission_number | CharField(50) | UNIQUE with institution | |
| email | EmailField | BLANK | |
| phone_number | CharField(20) | BLANK | |
| date_of_birth | DateField | NULL, BLANK | |
| gender | CharField(10) | BLANK | M/F/Other |
| is_active | BooleanField | Default=True | |
| created_at | DateTimeField | auto_now_add | |
| updated_at | DateTimeField | auto_now | |

### FeeStructure
| Column | Type | Constraints | Notes |
|--------|------|-------------|-------|
| id | AutoField | PK | |
| institution_id | ForeignKey | | CASCADE on delete |
| version | IntegerField | UNIQUE with institution | Auto-increment |
| is_active | BooleanField | Default=True | |
| created_at | DateTimeField | auto_now_add | |
| updated_at | DateTimeField | auto_now | |

### FeeItem
| Column | Type | Constraints | Notes |
|--------|------|-------------|-------|
| id | AutoField | PK | |
| fee_structure_id | ForeignKey | | CASCADE on delete |
| name | CharField(255) | | |
| fee_type | CharField(50) | CHOICES | tuition, accommodation, etc |
| amount | DecimalField(12,2) | Min=0 | |
| is_mandatory | BooleanField | Default=True | |
| description | TextField | BLANK | |
| created_at | DateTimeField | auto_now_add | |
| updated_at | DateTimeField | auto_now | |

### StudentFeeAssignment
| Column | Type | Constraints | Notes |
|--------|------|-------------|-------|
| id | AutoField | PK | |
| student_id | ForeignKey | | CASCADE on delete |
| fee_structure_id | ForeignKey | | PROTECT on delete |
| academic_year_id | ForeignKey | | PROTECT on delete |
| term_id | ForeignKey | NULL | SET_NULL on delete |
| total_fees | DecimalField(12,2) | Default=0 | |
| discount_amount | DecimalField(12,2) | Default=0 | |
| penalty_amount | DecimalField(12,2) | Default=0 | |
| amount_paid | DecimalField(12,2) | Default=0 | |
| due_date | DateField | NULL | |
| is_overdue | BooleanField | Default=False | |
| created_at | DateTimeField | auto_now_add | |
| updated_at | DateTimeField | auto_now | |

### InstitutionAuditLog
| Column | Type | Constraints | Notes |
|--------|------|-------------|-------|
| id | AutoField | PK | |
| institution_id | ForeignKey | | CASCADE on delete |
| actor_id | ForeignKey | NULL | SET_NULL on delete |
| action | CharField(100) | CHOICES | |
| entity_type | CharField(100) | BLANK | |
| entity_id | CharField(100) | BLANK | |
| description | TextField | BLANK | |
| changes | JSONField | NULL, BLANK | Before/after data |
| created_at | DateTimeField | auto_now_add | |

## Unique Constraints

| Table | Constraint | Reason |
|-------|-----------|--------|
| InstitutionProfile | (user_id) | One profile per user |
| AcademicYear | (institution, year_code) | No duplicate years per institution |
| Term | (academic_year, term_number) | One term number per year |
| Faculty | (institution, code) | Unique faculty code per institution |
| Program | (faculty, code) | Unique program code per faculty |
| Student | (institution, admission_number) | Unique admission number per institution |
| FeeStructure | (institution, version) | Version tracking |
| StudentFeeAssignment | (student, fee_structure, academic_year, term) | Unique fee per period |

## Indexes (Recommended for Performance)

```sql
-- Speed up lookups
CREATE INDEX idx_student_institution ON student(institution_id);
CREATE INDEX idx_student_admission ON student(admission_number);
CREATE INDEX idx_fee_assignment_student ON studentfeeassignment(student_id);
CREATE INDEX idx_fee_assignment_overdue ON studentfeeassignment(is_overdue);
CREATE INDEX idx_auditlog_institution ON institutionautditlog(institution_id);
CREATE INDEX idx_auditlog_created ON institutionautditlog(created_at);
```

## Calculated Fields (Properties)

### StudentFeeAssignment
```python
outstanding_balance = total_fees - discount_amount + penalty_amount - amount_paid
is_paid_in_full = outstanding_balance <= 0
```

## Validation Rules

1. **Academic Year**: start_date < end_date (via validator)
2. **Academic Year**: No overlapping years for same institution (via validator)
3. **Term**: Must belong to valid academic year
4. **Program**: Duration must be >= 1 year
5. **FeeItem**: Amount must be >= 0
6. **StudentFeeAssignment**: Student must be in institution
7. **StudentFeeAssignment**: FeeStructure must be from institution

---

**Database Version**: Django ORM  
**Support for Migrations**: Yes  
**Backup Strategy**: Django migration files  
**Migration Status**: ✅ Applied
