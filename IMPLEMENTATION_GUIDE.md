# EduPay Africa - Implementation Guide

## Overview
This guide provides step-by-step instructions for implementing the EduPay Africa platform. The project is structured in 4 phases as outlined in the requirements document.

## Current Status: PHASE 1 - MVP (6 weeks)

### What's Been Done ✅
1. Django project structure initialized
2. 6 apps created (users, schools, students, fees, payments, notifications)
3. Database models designed with proper relationships
4. REST API endpoints scaffolded with DRF
5. Authentication system with token-based auth
6. Role-based access control (RBAC) implemented
7. API documentation setup (Swagger/ReDoc)

### What's Next ⏳

---

## PHASE 1 Implementation Checklist

### Week 1: Database & Data Seeding ✅
- [x] Create Django models
- [x] Create serializers
- [x] Create viewsets & URLs
- [ ] **TODO:** Create data fixtures for Kenya locations (countries, regions, counties)
- [ ] **TODO:** Load initial data into database

**Action Items:**
```bash
# Create a fixture file with Kenya data
python manage.py dumpdata --natural-foreign apps.schools.country regions counties > fixtures/kenya_locations.json

# Or manually create fixtures/kenya_locations.json
```

### Week 2: School Registration Flow
- [ ] **TODO:** Create multi-step registration form frontend (HTML/Bootstrap)
- [ ] **TODO:** Implement image optimization for logo upload
- [ ] **TODO:** Add location cascading dropdown API endpoints
- [ ] **TODO:** Document registration flow

**API Endpoints Ready:** 
- `GET /api/v1/schools/countries/`
- `GET /api/v1/schools/regions/?country=1`
- `GET /api/v1/schools/counties/?region=1`
- `POST /api/v1/schools/schools/` (registration)

### Week 3: Student Management & Bulk Upload
- [ ] **TODO:** Implement CSV/Excel upload endpoint
- [ ] **TODO:** Create CSV template generator
- [ ] **TODO:** Implement validation & error reporting
- [ ] **TODO:** Add duplicate detection
- [ ] **TODO:** Create progress tracking for bulk uploads

**API Endpoints Ready:**
- `POST /api/v1/students/students/` (single enrollment)
- `POST /api/v1/students/students/bulk_upload/` (needs implementation)

### Week 4: Fee Management
- [ ] **TODO:** Create fee structure configuration UI
- [ ] **TODO:** Implement fee assignment logic
- [ ] **TODO:** Add arrears calculation
- [ ] **TODO:** Create fee reporting endpoints

**API Endpoints Ready:**
- `POST /api/v1/fees/categories/`
- `POST /api/v1/fees/structures/`
- `POST /api/v1/fees/items/`
- `POST /api/v1/fees/student-fees/`

### Week 5: M-Pesa Integration
- [ ] **TODO:** Register for M-Pesa Daraja API
- [ ] **TODO:** Implement STK Push functionality
- [ ] **TODO:** Setup payment callback handling
- [ ] **TODO:** Implement transaction status tracking
- [ ] **TODO:** Add payment reconciliation

**Key Files to Update:**
- `apps/payments/views.py` - Implement M-Pesa integration
- `apps/payments/models.py` - Add M-Pesa specific fields
- `edupay/settings.py` - Add M-Pesa credentials

**Sample Code Structure:**
```python
# apps/payments/integrations/mpesa.py (create this)
class MPesaPaymentGateway:
    def __init__(self, consumer_key, consumer_secret):
        # Initialize M-Pesa API
        pass
    
    def initiate_stk_push(self, phone_number, amount, account_reference):
        # Trigger STK push on user's phone
        pass
    
    def handle_callback(self, data):
        # Process M-Pesa callback
        pass
```

### Week 6: Receipts & Basic Dashboard
- [ ] **TODO:** Implement receipt generation (PDF)
- [ ] **TODO:** Setup receipt numbering system
- [ ] **TODO:** Create basic school dashboard
- [ ] **TODO:** Create parent dashboard
- [ ] **TODO:** Implement notification service

**API Endpoints to Create:**
- `GET /api/v1/dashboard/school/` - School admin dashboard
- `GET /api/v1/dashboard/parent/` - Parent portal data
- `GET /api/v1/payments/receipts/{id}/download/` - Download receipt PDF

---

## Implementation Priority Order

### MUST HAVE (MVP - Week 1-3)
1. Kenya locations data in database
2. School registration form & API
3. Student enrollment (single & bulk)
4. Fee structure configuration
5. Payment creation endpoints

### SHOULD HAVE (Week 4-5)
6. M-Pesa integration
7. Receipt generation
8. Email notifications
9. Basic dashboards
10. Bulk student upload with validation

### NICE TO HAVE (Post MVP)
11. SMS notifications via Twilio
12. Student ID card generation
13. Advanced reporting
14. Multi-language support

---

## Development Tasks in Order

### Task 1: Load Kenya Locations Data
**File:** Create `fixtures/kenya_locations.json`
**Time:** 1-2 hours
**Steps:**
1. Research Kenya's counties (47) and their regions
2. Create JSON fixture with Country, Region, County data
3. Load into database: `python manage.py loaddata fixtures/kenya_locations.json`

### Task 2: Implement School Registration Frontend
**Files:** Create templates/schools/register.html
**Time:** 4-6 hours
**Steps:**
1. Create multi-step form (6 steps as per requirements)
2. Implement location cascading dropdowns
3. Add form validation
4. Connect to API endpoints

### Task 3: CSV Bulk Student Upload
**File:** `apps/students/services/bulk_upload.py`
**Time:** 6-8 hours
**Features:**
- CSV template generation
- File validation
- Duplicate detection
- Error reporting
- Progress tracking
- Sibling detection

**Sample Structure:**
```python
# apps/students/services/bulk_upload.py
class BulkStudentUploader:
    def __init__(self, school_id):
        self.school = School.objects.get(id=school_id)
    
    def validate_csv(self, file):
        # Validate CSV format
        pass
    
    def process_rows(self, rows):
        # Process and validate each row
        pass
    
    def detect_duplicates(self, rows):
        # Find duplicate entries
        pass
    
    def detect_siblings(self, rows):
        # Find students with same parent phone
        pass
    
    def create_students(self, rows):
        # Bulk create students
        pass
```

### Task 4: M-Pesa Integration
**Files:** `apps/payments/integrations/mpesa.py`, `apps/payments/views.py`
**Time:** 8-10 hours
**Steps:**
1. Get M-Pesa Daraja API credentials
2. Implement auth token generation
3. Implement STK push
4. Setup callback webhook handler
5. Implement transaction confirmation
6. Add error handling & retry logic

### Task 5: Receipt Generation
**File:** `apps/payments/services/receipt_generator.py`
**Time:** 4-5 hours
**Tools:** reportlab or weasyprint
**Features:**
- School-branded receipts
- Auto receipt numbering
- PDF generation
- Email delivery
- SMS delivery (optional)

### Task 6: Notifications Service
**File:** `apps/notifications/services/notification_service.py`
**Time:** 5-6 hours
**Channels:** Email, SMS, WhatsApp, In-app
**Integrations:**
- SendGrid for email
- Twilio for SMS
- WhatsApp Business API
- Django signals for in-app

---

## Key Integration Points

### M-Pesa Flow
```
User initiates payment
    ↓
API creates Payment record (status: pending)
    ↓
M-Pesa STK Push to user's phone
    ↓
User enters M-Pesa PIN
    ↓
M-Pesa confirms & sends callback
    ↓
Webhook handler processes callback
    ↓
Update Payment (status: confirmed)
    ↓
Generate Receipt
    ↓
Send confirmation notification
```

### Bulk Upload Flow
```
School admin uploads CSV
    ↓
Validate file format & headers
    ↓
Preview first 10 rows
    ↓
Admin confirms
    ↓
Background job processes file
    ↓
Validate each row
    ↓
Detect duplicates & siblings
    ↓
Create Student records
    ↓
Generate report
    ↓
Email success/error report
```

---

## Database Migrations

```bash
# Create migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Create Kenya locations fixture
python manage.py dumpdata apps.schools > fixtures/initial_data.json

# Load fixture
python manage.py loaddata fixtures/initial_data.json
```

---

## Testing the API

### 1. User Registration
```bash
curl -X POST http://localhost:8000/api/v1/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "school_admin",
    "email": "admin@school.com",
    "password": "SecurePass123",
    "password_confirm": "SecurePass123",
    "first_name": "John",
    "last_name": "Doe",
    "role": "school_admin"
  }'
```

### 2. School Registration
```bash
curl -X POST http://localhost:8000/api/v1/schools/schools/ \
  -H "Authorization: Token YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Nairobi High School",
    "registration_number": "NHSC001",
    "institution_type": "secondary",
    "ownership_type": "public",
    "country": 1,
    "region": 1,
    "county": 1,
    "physical_address": "123 School Road",
    "town_city": "Nairobi",
    "email": "nhsc@school.ke",
    "phone_numbers": "+254700000000",
    "mpesa_paybill": "400100"
  }'
```

### 3. Student Enrollment
```bash
curl -X POST http://localhost:8000/api/v1/students/students/ \
  -H "Authorization: Token YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "school": 1,
    "admission_number": "ADM001",
    "first_name": "Jane",
    "last_name": "Doe",
    "date_of_birth": "2008-05-15",
    "gender": "F",
    "enrollment_date": "2024-01-15",
    "school_class": 1
  }'
```

---

## Deployment Preparation

### Environment Setup
```bash
# Create .env file
cp .env.example .env

# Configure:
DEBUG=False
SECRET_KEY=your-secure-key-here
DB_ENGINE=django.db.backends.postgresql
DB_NAME=edupay_production
DB_USER=edupay_user
DB_PASSWORD=strong_password
DB_HOST=db.example.com
MPESA_CONSUMER_KEY=your_key
MPESA_CONSUMER_SECRET=your_secret
```

### Production Checklist
- [ ] PostgreSQL database setup
- [ ] Redis cache setup
- [ ] Gunicorn WSGI server
- [ ] Nginx reverse proxy
- [ ] SSL/TLS certificates (Let's Encrypt)
- [ ] Environment variables configured
- [ ] Static files collected
- [ ] Database migrations run
- [ ] Backups configured
- [ ] Monitoring setup (New Relic, Sentry)
- [ ] Logging configured
- [ ] Rate limiting enabled

---

## Common Issues & Solutions

### Issue: ModuleNotFoundError
**Solution:** Ensure virtual environment is activated and all dependencies installed
```bash
pip install -r requirements.txt
```

### Issue: Database connection failed
**Solution:** Check PostgreSQL is running and credentials in .env are correct
```bash
psql -U postgres -d edupayafrica
```

### Issue: Migrations not applied
**Solution:** Run migrations explicitly
```bash
python manage.py migrate --run-syncdb
```

### Issue: Static files not loading
**Solution:** Collect static files
```bash
python manage.py collectstatic --noinput
```

---

## Resources & References

- [Django Documentation](https://docs.djangoproject.com/)
- [Django REST Framework](https://www.django-rest-framework.org/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [M-Pesa Daraja API](https://developer.safaricom.co.ke/)
- [Twilio Documentation](https://www.twilio.com/docs/)
- [SendGrid API](https://docs.sendgrid.com/)

---

## Contact & Support

**Questions?** Create an issue on GitHub or email support@edupayafrica.com

---

**Last Updated:** January 4, 2026
**Current Phase:** 1 (MVP Development)
**Next Review:** Upon completion of week 2 tasks
