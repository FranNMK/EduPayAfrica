"# EduPay Africa - School Payment Management Platform

A Django-based REST API for managing school fee payments across Africa with support for multiple payment methods and real-time reconciliation.

## Project Status

**Phase 1 - MVP Development**
- ✅ Project structure initialized
- ✅ Database models created
- ✅ REST API endpoints scaffolded
- ⏳ Integration features (M-Pesa, notifications)
- ⏳ Frontend development

## Quick Start

```bash
# 1. Clone and navigate
git clone https://github.com/FranNMK/EduPayAfrica.git
cd EduPayAfrica

# 2. Setup environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# 3. Configure
cp .env.example .env
# Edit .env with your database and API credentials

# 4. Initialize database
python manage.py migrate
python manage.py createsuperuser

# 5. Run server
python manage.py runserver
```

Visit: http://localhost:8000/api/docs/ for API documentation

## Tech Stack

- **Backend:** Django 5.0.6, Django REST Framework 3.14.0
- **Database:** PostgreSQL 15+
- **Cache:** Redis 7.0+
- **Task Queue:** Celery
- **Frontend:** Bootstrap 5 (coming soon)

## Project Structure

```
EduPayAfrica/
├── edupay/                  # Django project config
├── apps/
│   ├── users/               # Authentication & user management
│   ├── schools/             # School registration & management
│   ├── students/            # Student enrollment
│   ├── fees/                # Fee structures & tracking
│   ├── payments/            # Payment processing
│   └── notifications/       # Alerts & communications
├── manage.py
└── requirements.txt
```

## Key Features Implemented

✅ User authentication (register/login/logout)
✅ Role-based access control (5 roles)
✅ School registration with location cascading
✅ Student enrollment & parent linking
✅ Fee structure configuration
✅ Payment transaction tracking
✅ Receipt management
✅ Notification templates
✅ RESTful API with Swagger documentation

## API Endpoints (Phase 1)

**Auth:** POST /api/v1/auth/register, /login, /logout
**Schools:** GET/POST /api/v1/schools/schools
**Students:** GET/POST /api/v1/students/students
**Fees:** GET/POST /api/v1/fees/student-fees
**Payments:** GET/POST /api/v1/payments/payments
**Notifications:** GET /api/v1/notifications/notifications

## Next: Getting Started

1. **Setup PostgreSQL** (localhost:5432)
2. **Run migrations:** `python manage.py migrate`
3. **Create admin user:** `python manage.py createsuperuser`
4. **Load country data:** (fixture file needed)
5. **Start server:** `python manage.py runserver`
6. **Test API:** Visit http://localhost:8000/api/docs/

## Development Roadmap

### Phase 1 (Current MVP - 6 weeks)
- [x] Core models & API structure
- [ ] M-Pesa integration
- [ ] Bulk student upload (CSV)
- [ ] Receipt generation
- [ ] Email/SMS notifications

### Phase 2 (8 weeks)
- [ ] Admin dashboard
- [ ] Parent portal
- [ ] Advanced reporting
- [ ] Swahili localization

### Phase 3 (Expansion - 6 weeks)
- [ ] Mobile apps (iOS/Android)
- [ ] Multi-country support
- [ ] White-label solutions
- [ ] AI-powered insights

## Documentation

- [Full Requirements](EduPayAfricaRequirements.txtx) - Complete specification
- [API Docs](http://localhost:8000/api/docs/) - Interactive API documentation
- [Contributing Guide](CONTRIBUTING.md) - How to contribute

## Support & Contact

**Email:** support@edupayafrica.com
**Phone:** +254 700 000 000
**GitHub:** https://github.com/FranNMK/EduPayAfrica

---

**Last Updated:** January 4, 2026 | **Version:** 0.1.0 | **Status:** MVP Development" 
