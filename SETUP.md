# Setup Instructions for EduPay Africa

## Prerequisites
- Python 3.11 or higher
- PostgreSQL 15 or higher (or SQLite for development)
- Redis 7.0+ (optional, for caching)
- Git
- Virtual environment tool (venv, conda, etc)

## Step-by-Step Setup

### 1. Clone the Repository
```bash
git clone https://github.com/FranNMK/EduPayAfrica.git
cd EduPayAfrica
```

### 2. Create Virtual Environment
```bash
# On Windows
python -m venv venv
venv\Scripts\activate

# On macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Environment Configuration
```bash
# Copy example env file
cp .env.example .env

# Edit .env with your configuration
# On Windows
notepad .env

# On macOS/Linux
nano .env
```

**Required .env variables:**
```
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database (PostgreSQL)
DB_ENGINE=django.db.backends.postgresql
DB_NAME=edupayafrica
DB_USER=postgres
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432

# Or SQLite for development
# DB_ENGINE=django.db.backends.sqlite3
# DB_NAME=db.sqlite3
```

### 5. Database Setup

#### Option A: PostgreSQL (Recommended)
```bash
# Install PostgreSQL if not already installed
# Create database and user:
psql -U postgres
CREATE DATABASE edupayafrica;
CREATE USER edupayuser WITH PASSWORD 'your_password';
ALTER ROLE edupayuser SET client_encoding TO 'utf8';
ALTER ROLE edupayuser SET default_transaction_isolation TO 'read committed';
ALTER ROLE edupayuser SET default_transaction_deferrable TO on;
ALTER ROLE edupayuser SET default_transaction_level TO 'read committed';
ALTER ROLE edupayuser SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE edupayafrica TO edupayuser;
\q
```

#### Option B: SQLite (Development Only)
```bash
# Just set in .env:
DB_ENGINE=django.db.backends.sqlite3
DB_NAME=db.sqlite3
```

### 6. Run Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### 7. Create Superuser
```bash
python manage.py createsuperuser
# Follow the prompts to create admin account
```

### 8. Load Initial Data (Optional)
```bash
# Create Kenya locations fixture file first
# Then load it:
python manage.py loaddata fixtures/kenya_locations.json
```

### 9. Run Development Server
```bash
python manage.py runserver
```

Server runs at: **http://localhost:8000**

### 10. Access the Application
- **API Documentation:** http://localhost:8000/api/docs/
- **Alternative Docs:** http://localhost:8000/api/redoc/
- **Admin Panel:** http://localhost:8000/admin/

---

## Troubleshooting

### Issue: ModuleNotFoundError
```
Error: No module named 'django'
```
**Solution:** Ensure virtual environment is activated
```bash
source venv/bin/activate  # macOS/Linux
# or
venv\Scripts\activate  # Windows
```

### Issue: Database connection refused
```
Error: could not connect to server
```
**Solution:** 
- Ensure PostgreSQL is running
- Check credentials in .env
- Verify database exists

```bash
# Test PostgreSQL connection
psql -U postgres -d edupayafrica -h localhost
```

### Issue: Port 8000 already in use
```
Error: Address already in use
```
**Solution:** Use different port
```bash
python manage.py runserver 8001
```

### Issue: Static files not loading
**Solution:** Collect static files
```bash
python manage.py collectstatic --noinput
```

### Issue: Migration errors
```
Error: No changes detected in app
```
**Solution:** 
```bash
python manage.py makemigrations apps.users
python manage.py migrate
```

### Issue: Permission denied on .env
```
Error: Permission denied: '.env'
```
**Solution:** Change file permissions
```bash
chmod 644 .env  # macOS/Linux
```

---

## Running Tests

```bash
# Run all tests
python manage.py test

# Run specific app tests
python manage.py test apps.users

# Run with verbose output
python manage.py test --verbosity=2

# Run with coverage
pip install coverage
coverage run --source='.' manage.py test
coverage report
```

---

## Development Workflow

### 1. Create a Feature Branch
```bash
git checkout -b feature/school-registration
```

### 2. Make Changes & Test
```bash
# Create migrations if you changed models
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Test your changes
python manage.py test
```

### 3. Commit & Push
```bash
git add .
git commit -m "Add school registration feature"
git push origin feature/school-registration
```

### 4. Create Pull Request
- Go to GitHub
- Click "Pull Request"
- Describe your changes
- Wait for review

---

## File Structure Overview

```
EduPayAfrica/
├── edupay/                     # Project settings
│   ├── __init__.py
│   ├── settings.py            # ← EDIT FOR CONFIG
│   ├── urls.py
│   └── wsgi.py
├── apps/                       # Django apps
│   ├── users/                 # Auth & user management
│   ├── schools/               # School management
│   ├── students/              # Student enrollment
│   ├── fees/                  # Fee management
│   ├── payments/              # Payment processing
│   └── notifications/         # Notifications
├── fixtures/                  # Data fixtures (create this)
├── static/                    # Static files (CSS, JS, images)
├── media/                     # Uploaded files
├── logs/                      # Log files
├── manage.py                  # Django CLI
├── requirements.txt           # Python dependencies
├── .env.example              # Environment template
├── .gitignore                # Git ignore rules
├── README.md                 # Project overview
├── IMPLEMENTATION_GUIDE.md   # Detailed guide
└── QUICK_REFERENCE.md        # Quick reference
```

---

## Database Setup with Fixtures

### Create Kenya Locations Fixture
```bash
# Create fixtures directory
mkdir -p fixtures

# Create kenya_locations.json with:
# - 1 Country (Kenya)
# - 47 Regions (regions of Kenya)
# - Kenya's 47 Counties
```

Example structure:
```json
[
  {
    "model": "schools.country",
    "pk": 1,
    "fields": {
      "name": "Kenya",
      "code": "KE",
      "currency": "KES"
    }
  },
  {
    "model": "schools.region",
    "pk": 1,
    "fields": {
      "country": 1,
      "name": "Nairobi"
    }
  }
  // ... more counties
]
```

Load fixture:
```bash
python manage.py loaddata fixtures/kenya_locations.json
```

---

## Using the Django Shell

```bash
# Enter Django shell
python manage.py shell

# Example queries
from apps.schools.models import School, Country
from apps.users.models import User

# Create a country
country = Country.objects.create(name="Kenya", code="KE", currency="KES")

# Get all schools
schools = School.objects.all()

# Get user by username
user = User.objects.get(username="admin")

# Create a school
school = School.objects.create(
    name="Nairobi High School",
    registration_number="NHS001",
    country=country,
    # ... other required fields
)

# Exit shell
exit()
```

---

## Common Django Commands

```bash
# List all migrations
python manage.py showmigrations

# Create new app
python manage.py startapp app_name

# Create empty migration
python manage.py makemigrations --empty apps.users --name add_phone_field

# Rollback specific migration
python manage.py migrate apps.users 0001

# Show database schema
python manage.py sqlmigrate apps.users 0001

# Run custom command (create one in management/commands/)
python manage.py your_command

# Interactive Python shell
python manage.py shell

# Change user password
python manage.py changepassword username

# Flush database (DELETE ALL DATA!)
python manage.py flush

# Export data
python manage.py dumpdata apps.schools > schools.json

# Import data
python manage.py loaddata schools.json
```

---

## Performance Tips

1. **Database Indexing**
   - Add `db_index=True` to frequently queried fields
   
2. **Query Optimization**
   - Use `select_related()` for ForeignKey
   - Use `prefetch_related()` for reverse relations
   
3. **Caching**
   - Use Redis for caching
   - Cache expensive queries

4. **Pagination**
   - Limit results in API responses
   - Default is 20 items per page

5. **Monitoring**
   - Enable query logging in development
   - Use Django Debug Toolbar

---

## Security Checklist

### Development
- [ ] Don't commit .env file
- [ ] Use secure passwords for test accounts
- [ ] Enable DEBUG only in development
- [ ] Don't store credentials in code

### Production
- [ ] Change SECRET_KEY to random value
- [ ] Set DEBUG=False
- [ ] Use HTTPS only
- [ ] Set secure ALLOWED_HOSTS
- [ ] Use strong database passwords
- [ ] Enable CSRF protection
- [ ] Set up regular backups
- [ ] Enable logging & monitoring
- [ ] Keep dependencies updated

---

## Useful Packages to Install Later

```bash
# For API development
pip install django-cors-headers        # CORS support
pip install django-filter              # Filtering
pip install django-extensions          # Shell_plus, etc

# For security
pip install django-ratelimit           # Rate limiting
pip install django-guardian             # Object-level permissions

# For performance
pip install django-cachalot            # ORM cache
pip install django-debug-toolbar       # Debug toolbar

# For monitoring
pip install sentry-sdk                 # Error tracking
pip install newrelic                   # Performance monitoring

# Testing
pip install pytest-django              # Pytest integration
pip install factory-boy                # Test fixtures
```

Install with:
```bash
pip install package_name
pip freeze > requirements.txt
```

---

## Next Steps After Setup

1. ✅ **Environment**: This setup guide
2. ⏳ **Create Data**: Load Kenya locations
3. ⏳ **Develop**: Implement features from IMPLEMENTATION_GUIDE.md
4. ⏳ **Test**: Write tests and test API
5. ⏳ **Deploy**: Follow deployment checklist

---

## Getting Help

1. **API Documentation**: http://localhost:8000/api/docs/
2. **Django Docs**: https://docs.djangoproject.com/
3. **DRF Docs**: https://www.django-rest-framework.org/
4. **GitHub Issues**: https://github.com/FranNMK/EduPayAfrica/issues
5. **Email**: support@edupayafrica.com

---

**Last Updated:** January 4, 2026
**Version:** 0.1.0
**Status:** MVP Development
