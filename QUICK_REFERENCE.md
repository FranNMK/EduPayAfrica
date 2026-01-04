# EduPay Africa - Quick Reference Guide

## 🚀 Getting Started in 5 Minutes

### 1. Install Dependencies
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure Environment
```bash
cp .env.example .env
# Edit .env with your database credentials
```

### 3. Setup Database
```bash
python manage.py migrate
python manage.py createsuperuser
```

### 4. Run Server
```bash
python manage.py runserver
```

### 5. View API
Visit: **http://localhost:8000/api/docs/**

---

## 📊 Project Architecture

### Database Models
```
User (Custom)
├── School (registered schools)
├── Academic Year
├── School Class
│   └── Stream
├── Student
│   └── Parent
│   └── Fee
│   └── Payment
│       └── Receipt
├── Fee Category
├── Fee Structure
└── Notification
```

### API Routes
```
/api/v1/
├── auth/          # Login, register, logout
├── schools/       # School registration & management
├── students/      # Student enrollment
├── fees/          # Fee configuration
├── payments/      # Payment processing
└── notifications/ # Alerts & templates
```

---

## 👤 User Roles & Permissions

| Role | Can Do | Cannot Do |
|------|--------|-----------|
| **Super Admin** | Everything | N/A |
| **School Admin** | Manage school, students, fees | Verify schools |
| **Teacher** | View classes, students, fees | Manage schools |
| **Parent** | Pay fees, view statements | Manage anything |
| **Student** | View own fees | Pay directly |

---

## 📝 API Endpoints Summary

### Authentication
```
POST   /api/v1/auth/register/        Register new user
POST   /api/v1/auth/login/           User login
POST   /api/v1/auth/logout/          User logout (requires auth)
GET    /api/v1/auth/users/profile    Get current user (requires auth)
```

### Schools
```
GET    /api/v1/schools/countries/               List all countries
GET    /api/v1/schools/regions/?country=1      Get regions for country
GET    /api/v1/schools/counties/?region=1      Get counties for region
POST   /api/v1/schools/schools/                 Register new school
GET    /api/v1/schools/schools/                 List schools (filtered by user)
PUT    /api/v1/schools/schools/{id}/            Update school
POST   /api/v1/schools/schools/{id}/verify/    Verify school (super_admin only)
GET    /api/v1/schools/academic-years/         List academic years
POST   /api/v1/schools/classes/                 Create class
POST   /api/v1/schools/streams/                 Create stream
```

### Students
```
POST   /api/v1/students/students/               Enroll new student
GET    /api/v1/students/students/               List students (with filters)
GET    /api/v1/students/students/{id}/          Get student details
PUT    /api/v1/students/students/{id}/          Update student
POST   /api/v1/students/students/bulk_upload/   Bulk upload (TODO)
POST   /api/v1/students/parents/                Register parent
GET    /api/v1/students/parents/                List parents
```

### Fees
```
POST   /api/v1/fees/categories/                 Create fee category
GET    /api/v1/fees/categories/                 List fee categories
POST   /api/v1/fees/structures/                 Create fee structure
GET    /api/v1/fees/structures/                 List fee structures
POST   /api/v1/fees/items/                      Add fee item
POST   /api/v1/fees/student-fees/               Assign fee to student
GET    /api/v1/fees/student-fees/               List student fees (with filters)
```

### Payments
```
POST   /api/v1/payments/methods/                Create payment method
GET    /api/v1/payments/methods/                List payment methods
POST   /api/v1/payments/payments/               Initiate payment
GET    /api/v1/payments/payments/               List payments (with filters)
POST   /api/v1/payments/payments/{id}/confirm/  Confirm payment
GET    /api/v1/payments/receipts/               List receipts
POST   /api/v1/payments/receipts/{id}/void/    Void receipt
```

### Notifications
```
GET    /api/v1/notifications/notifications/    Get user notifications
POST   /api/v1/notifications/notifications/{id}/mark_as_read/  Mark as read
POST   /api/v1/notifications/templates/        Create template
GET    /api/v1/notifications/templates/        List templates
```

---

## 🔐 Authentication

Every API call (except register) requires:
```
Authorization: Token YOUR_TOKEN_HERE
```

Get token from login response:
```bash
curl -X POST http://localhost:8000/api/v1/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "user", "password": "pass"}'
```

---

## 📂 Key Files & Their Purpose

| File | Purpose |
|------|---------|
| `edupay/settings.py` | Django configuration, database, apps |
| `edupay/urls.py` | Main URL routing |
| `apps/users/models.py` | Custom User model with roles |
| `apps/schools/models.py` | School, locations, classes, streams |
| `apps/students/models.py` | Student, parent, enrollment |
| `apps/fees/models.py` | Fee categories, structures, items |
| `apps/payments/models.py` | Payment, receipt, methods |
| `apps/notifications/models.py` | Notifications, templates |
| `requirements.txt` | Python dependencies |
| `.env.example` | Environment variable template |
| `manage.py` | Django management command |
| `README.md` | Project overview |
| `IMPLEMENTATION_GUIDE.md` | Detailed implementation steps |

---

## 🛠 Common Commands

```bash
# Activate virtual environment
source venv/bin/activate

# Install packages
pip install -r requirements.txt

# Create migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Run development server
python manage.py runserver

# Load data from fixture
python manage.py loaddata fixture_file.json

# Create dump of data
python manage.py dumpdata app_name > fixture.json

# Run tests
python manage.py test

# Django shell (interactive)
python manage.py shell

# Create new app
python manage.py startapp app_name
```

---

## 🧪 Testing the API with cURL

### Register User
```bash
curl -X POST http://localhost:8000/api/v1/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "SecurePass123",
    "password_confirm": "SecurePass123",
    "first_name": "Test",
    "last_name": "User",
    "role": "school_admin"
  }'
```

### Login
```bash
curl -X POST http://localhost:8000/api/v1/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser", "password": "SecurePass123"}'
```

### Get Token & Make Authenticated Request
```bash
TOKEN="your_token_from_login"
curl -X GET http://localhost:8000/api/v1/auth/users/profile/ \
  -H "Authorization: Token $TOKEN"
```

---

## 🐛 Debugging Tips

### View all SQL queries (development only)
```python
from django.db import connection
from django.test.utils import CaptureQueriesContext

with CaptureQueriesContext(connection) as context:
    # Your code here
    pass

print(context.captured_queries)
```

### Enable SQL logging in settings.py
```python
LOGGING = {
    'version': 1,
    'handlers': {
        'console': {'class': 'logging.StreamHandler'},
    },
    'loggers': {
        'django.db.backends': {
            'handlers': ['console'],
            'level': 'DEBUG',
        }
    }
}
```

### Check active migrations
```bash
python manage.py showmigrations
```

### Rollback migrations
```bash
python manage.py migrate app_name 0001
```

---

## 📚 Next Steps

1. **Load Kenya Locations Data**
   - Create `fixtures/kenya_locations.json`
   - Load with: `python manage.py loaddata fixtures/kenya_locations.json`

2. **Test All Endpoints**
   - Use http://localhost:8000/api/docs/ (Swagger)
   - Test each endpoint with sample data

3. **Implement M-Pesa Integration**
   - Register at https://developer.safaricom.co.ke/
   - Add credentials to .env
   - Implement STK push in `apps/payments/views.py`

4. **Create Bulk Upload Feature**
   - Implement CSV validation
   - Add duplicate detection
   - Create progress tracking

5. **Build Dashboards**
   - Create `/api/v1/dashboard/school/` endpoint
   - Create `/api/v1/dashboard/parent/` endpoint

6. **Setup Notifications**
   - Configure SendGrid for emails
   - Configure Twilio for SMS
   - Implement notification service

---

## 🔗 Useful Links

- **Django Docs:** https://docs.djangoproject.com/
- **DRF Docs:** https://www.django-rest-framework.org/
- **PostgreSQL:** https://www.postgresql.org/docs/
- **M-Pesa API:** https://developer.safaricom.co.ke/
- **Twilio:** https://www.twilio.com/docs/
- **SendGrid:** https://docs.sendgrid.com/
- **Bootstrap:** https://getbootstrap.com/docs/
- **Redis:** https://redis.io/documentation

---

## ❓ FAQ

**Q: Why PostgreSQL?**
A: Better for large datasets, JSONB fields, and production scalability.

**Q: Why Django REST Framework?**
A: Excellent tooling, serializers, permissions, authentication, automatic API docs.

**Q: Why Celery + Redis?**
A: For async tasks like sending notifications, processing bulk uploads, generating reports.

**Q: Can I use SQLite for development?**
A: Yes, edit `settings.py` DATABASES to use `sqlite3`, but PostgreSQL is recommended.

**Q: How do I deploy to production?**
A: See IMPLEMENTATION_GUIDE.md for deployment checklist.

---

## 📞 Support

- **Documentation:** README.md, IMPLEMENTATION_GUIDE.md
- **API Docs:** http://localhost:8000/api/docs/
- **Email:** support@edupayafrica.com
- **GitHub Issues:** https://github.com/FranNMK/EduPayAfrica/issues

---

**Last Updated:** January 4, 2026
**Version:** 0.1.0
**Status:** MVP Development Phase 1
