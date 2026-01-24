# Quick Start Guide - Role-Based Institution Management

## 🚀 Getting Started in 5 Minutes

### Step 1: Verify Server is Running
```
http://127.0.0.1:8001/
```
Server should show "System check identified no issues"

### Step 2: Login as Admin
Navigate to Django admin:
```
http://127.0.0.1:8001/admin/
```

### Step 3: Create Institution Profile
1. Go to "Institutions > Institution profiles"
2. Click "Add Institution Profile"
3. Link to your user account
4. Fill in:
   - Institution Name: "Your School Name"
   - Institution Type: "university" | "college" | "school"
   - Contact Email & Phone
5. Save

### Step 4: Add Staff Members
1. Login as institution admin user
2. Go to `/institution/` (Dashboard)
3. Click "Manage Staff"
4. Fill form with staff details:
   - Full Name
   - Email
   - Phone
   - Role (select from dropdown)
5. Click "Add Staff Member"

---

## 👥 Staff Roles & Access

### Admin (Institution Administrator)
**Access**: Full system control
```
http://127.0.0.1:8001/institution/
├── Staff Management (/staff/)
├── Student Management (/students/)
├── Program Management (/programs/)
└── Academic Structure (/academic-structure/)
```

### Principal (School Principal)
**Access**: Messaging & Analytics
```
http://127.0.0.1:8001/institution/
├── Send Messages (/messages/)
└── View Analytics (/fee-analysis/)
```

### Bursar/Finance Officer
**Access**: Fee & Financial Management
```
http://127.0.0.1:8001/institution/
├── Fee Structures (/fee-structures/)
├── Programs (/programs/)
└── Fee Analysis (/fee-analysis/)
```

### Teacher
**Access**: Limited (View-Only)
```
http://127.0.0.1:8001/institution/
└── View Dashboard
```

---

## 📚 Common Tasks

### Add a New Academic Year
1. Admin → Dashboard
2. "Academic Structure"
3. Fill form:
   - Year Code: "2025/2026"
   - Start Date: 2025-01-01
   - End Date: 2025-12-31
   - Is Active: ✓
4. Submit

### Create an Academic Program
1. Admin/Bursar → Dashboard
2. "Manage Programs"
3. Fill form:
   - Program Name: "Bachelor of Science in CS"
   - Code: "BSC-CS"
   - Type: "non_modular"
   - Faculty: Select from list
   - Duration: 48 months
4. Submit

### Set Up Fee Structure
1. Bursar → Dashboard
2. "Manage Fee Structures"
3. Add Fee Items:
   - **Tuition**: 5,000,000 (Mandatory)
   - **Accommodation**: 1,000,000
   - **Technology**: 200,000
4. Create Structure

### Add Students (Single)
1. Admin → "Manage Students"
2. "Add Student" tab
3. Fill form:
   - Full Name
   - Admission Number
   - Email (optional)
   - Program
   - Academic Year
4. Add

### Add Students (Bulk Upload)
1. Admin → "Manage Students"
2. "Bulk Upload" tab
3. Prepare Excel/CSV:
   ```
   Full Name,Admission Number,Email,Program Code,Academic Year Code
   John Doe,STU001,john@example.com,BSC-CS,2025/2026
   Jane Smith,STU002,jane@example.com,BSC-CS,2025/2026
   ```
4. Upload file
5. System validates and reports errors/success

### Send Message to Parents (Principal)
1. Principal → Dashboard
2. "Send Message to Parents"
3. Fill form:
   - Type: "reminder" | "urgent" | "announcement"
   - Subject: "Fee Payment Reminder"
   - Content: "Your child's fees are due..."
   - Recipients: "All" | "Overdue Only" | "Specific"
4. Send

### View Fee Analytics
1. Principal/Bursar → Dashboard
2. "View Fee Analytics" or "Fee Analysis"
3. See:
   - Total students: X
   - Total billed: X
   - Total paid: X
   - Collection rate: X%
   - Breakdown by status
   - Detailed student table

---

## 🔑 Key URLs

| Purpose | URL | Access Level |
|---------|-----|--------------|
| Dashboard | `/institution/` | All Roles |
| Staff Mgmt | `/institution/staff/` | Admin |
| Students | `/institution/students/` | Admin |
| Programs | `/institution/programs/` | Admin, Bursar |
| Fee Structures | `/institution/fee-structures/` | Bursar |
| Messages | `/institution/messages/` | Principal |
| Analytics | `/institution/fee-analysis/` | Principal, Bursar |
| Academic | `/institution/academic-structure/` | Admin |

---

## 📊 Dashboard Content by Role

### Admin Dashboard
- KPI Cards: Students, Billed, Outstanding, Overdue
- Quick Actions: Staff, Students, Programs, Academic
- Staff List: Name, Role, Email, Status

### Principal Dashboard
- Cards: Messages Sent, Staff Count, Active Year
- Quick Actions: Send Message, View Analytics
- Recent Messages: Subject, Type, Recipients, Date

### Bursar Dashboard
- KPI Cards: Billed, Paid, Outstanding, Collection %
- Quick Actions: Fee Structures, Programs, Analytics
- Programs List & Fee Structures List

### Teacher Dashboard
- Simple overview
- Student count
- Coming soon features message

---

## ⚙️ Configuration

### Add New Role Type
Edit `institutions/models.py`:
```python
ROLE_CHOICES = [
    ("admin", "Institution Admin"),
    ("principal", "Principal"),
    ("your_role", "Your Role Display Name"),  # Add here
]
```

### Customize Dashboard Content
Edit `institutions/views.py`:
```python
elif staff_role == "your_role":
    context["custom_data"] = YourData.objects.filter(...)
    return render(request, "institutions/dashboards/your_dashboard.html", context)
```

### Add New Permission Check
```python
@require_role("admin", "bursar")
def sensitive_view(request):
    # Only admin and bursar can access
    pass
```

---

## 🐛 Troubleshooting

### "You don't have an institution profile"
**Solution**: Admin needs to create institution profile in Django admin

### "You don't have permission"
**Solution**: 
1. Check InstitutionStaff record exists
2. Verify role assignment is correct
3. Check is_active = True

### Staff can't see their dashboard
**Solution**:
1. Verify staff role is set
2. Check user is linked to InstitutionStaff
3. Ensure institution is active

### Messages not appearing
**Solution**:
1. Principal role must be assigned
2. Students must be assigned to message
3. Check target_students M2M relationship

### Program creation fails
**Solution**:
1. Faculty must exist first
2. Program code must be unique per institution
3. Duration must be > 0

### Fee structure issues
**Solution**:
1. Confirm fee items are created
2. Check amounts are positive
3. Verify institution association

---

## 📋 Features Checklist

### Core Features ✅
- [x] Role-based access control
- [x] Staff management system
- [x] Program management (modular/non-modular)
- [x] Fee structure versioning
- [x] Principal messaging system
- [x] Fee analytics dashboard
- [x] Bulk student upload (Excel/CSV)
- [x] Audit logging

### User Interfaces ✅
- [x] Admin dashboard
- [x] Principal dashboard
- [x] Bursar dashboard
- [x] Staff management panel
- [x] Program management interface
- [x] Fee structure editor
- [x] Messaging panel
- [x] Analytics dashboard

### Data Models ✅
- [x] InstitutionStaff (with roles)
- [x] ParentGuardian
- [x] PrincipalMessage
- [x] FeeAnalysisSnapshot
- [x] Enhanced Program model

---

## 🔒 Security Notes

✅ All views enforce role-based access  
✅ Data automatically scoped to institution  
✅ All actions audit logged  
✅ User accounts auto-created on staff add  
✅ Active status tracking prevents hard deletes  

---

## 💾 Database

### New Tables (Read-Only after creation)
```
institutions_institutionstaff
institutions_parentguardian
institutions_principalmessage
institutions_feeanalysissnapshot
institutions_principalmessage_target_students (M2M)
```

### Migrations Applied
```
python manage.py migrate institutions
```

---

## 📞 Support

### Debug Mode
Check Django system status:
```bash
python manage.py check
```

### View Audit Logs
1. Admin panel
2. Institutions > Institution Audit Logs
3. Filter by institution or user

### Check Staff Assignments
```bash
python manage.py shell
>>> from institutions.models import InstitutionStaff
>>> InstitutionStaff.objects.all()
```

---

## 🎯 Next Steps

1. **Test Each Role** - Login as different staff members
2. **Add Sample Data** - Create programs, students, fees
3. **Send Test Message** - Test principal messaging
4. **View Analytics** - Check fee dashboard
5. **Deploy** - Follow production checklist

---

**Ready to use!** 🚀  
Start at: `http://127.0.0.1:8001/institution/`
