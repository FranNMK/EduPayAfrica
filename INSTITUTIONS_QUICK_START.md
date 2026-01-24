# Institutions App - Quick Start Guide

## 🚀 Getting Started

### Access Points
- **Dashboard**: `http://localhost:8001/institution/`
- **Admin Panel**: `http://localhost:8001/admin/` → Institutions section

### Role-Based Access
- **Institution Admin**: Full access to institution settings, academic structure, user management
- **Bursar**: Access to fee management and financial reporting

## 📋 Typical Workflow

### 1. Institution Setup (Admin)
```
Dashboard → Profile Settings
├─ Update contact email
├─ Update phone number
├─ Update address
└─ Upload logo
```

### 2. Academic Calendar (Admin)
```
Dashboard → Academic Structure
├─ Add Academic Years (e.g., 2025/2026)
├─ Create Terms (Term 1, 2, 3)
├─ Set up Faculties
└─ Define Programs/Courses
```

### 3. Student Registration (Admin)
```
Dashboard → Student Management
├─ Option A: Add manually
│   ├─ Enter full name
│   ├─ Admission number
│   ├─ Select program
│   └─ Select academic year
│
└─ Option B: Bulk upload CSV
    ├─ Prepare CSV file with: full_name, admission_number, email, program_id, academic_year_id
    └─ Upload file
```

### 4. Fee Configuration (Bursar)
```
Dashboard → Fee Management
├─ Create Fee Structure (versioned)
├─ Add Fee Items
│   ├─ Tuition
│   ├─ Accommodation
│   ├─ Lab fees
│   ├─ Library fees
│   └─ Other fees
└─ Assign to students
```

### 5. Balance Tracking (Bursar)
```
Dashboard → Financial Reports
├─ View summary (total billed, paid, outstanding)
├─ See all fee assignments
├─ Check overdue records
└─ Generate student statements
```

## 📊 Key Metrics

**Dashboard shows:**
- Total Students (active)
- Total Fees Billed
- Outstanding Balance
- Overdue Records

**Reports show:**
- Total Billed
- Total Paid
- Outstanding Balance
- Collection Rate (%)

## 🔧 Admin Panel Operations

### Creating Institution Profile
```
1. Go to Admin → Institution Profiles
2. Click "Add Institution Profile"
3. Select user (institution admin)
4. Enter: institution name, type, contact details
5. Save
```

### Managing Faculties & Programs
```
Admin → Faculties
├─ Add faculty with name and code

Admin → Programs
├─ Select faculty
├─ Add program with name, code, duration
└─ Save
```

### Viewing Audit Logs
```
Admin → Institution Audit Logs
├─ Filter by institution or action
├─ See who did what and when
└─ View description of changes
```

## 💾 CSV Format for Bulk Upload

**Required columns:**
```
full_name,admission_number,email,program_id,academic_year_id
"John Doe","ADM001","john@example.com",1,1
"Jane Smith","ADM002","jane@example.com",2,1
```

**Notes:**
- `program_id`: Get from Admin → Programs
- `academic_year_id`: Get from Admin → Academic Years
- Email is optional

## 🔍 Important Concepts

### Fee Assignment vs Payment
- **Fee Assignment** = Accounting entry (student owes money)
- **Payment** = Actually receiving money (not implemented yet)

### Academic Year Overlap
- Years cannot overlap (system validates)
- Only one academic year can be marked as "current"

### Versioned Fee Structures
- Each fee structure has a version number
- New changes = new version
- Historical data preserved
- Only one version can be "active"

## 📄 Generating Reports

### Student Fee Statement
```
Reports → Find student
→ Click "View Statement"
→ Print or Export (use browser print)
```

### Fee Summary Report
```
Reports → Print Report button
→ Opens printable summary
→ Shows all fee assignments
```

## 🐛 Troubleshooting

### Issue: Student not appearing in list
**Solution:** Check if student is marked as active

### Issue: Academic year not saving
**Solution:** Verify start date is before end date and doesn't overlap

### Issue: Fee assignment not created
**Solution:** Ensure fee structure is active and term is selected

## 🔐 Data Isolation

Each institution:
- ✅ Can only see their own students
- ✅ Can only manage their own faculties/programs
- ✅ Can only see their own fee structures
- ✅ Has separate audit logs
- ❌ Cannot access other institutions' data

## 📝 Audit Trail

Every action is logged:
- ✓ User account creation/deactivation
- ✓ Fee structure changes
- ✓ Student additions
- ✓ Fee assignments
- ✓ Institution profile updates
- ✓ Academic calendar changes

View logs: Admin → Institution Audit Logs

## 🎯 Next Steps

1. **Create Institution Profile** (via Admin)
2. **Set up Academic Years** (Dashboard)
3. **Add Faculties & Programs** (Admin)
4. **Register Students** (Dashboard)
5. **Configure Fees** (Dashboard)
6. **Monitor Balances** (Reports)

---

**Ready to begin!** 🚀

Access the app at: `http://localhost:8001/institution/`
