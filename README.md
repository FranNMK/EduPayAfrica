EduPayAfrica — Django Platform for Institutions
==============================================

Overview
--------
EduPayAfrica is a Django-based platform for managing educational institutions: programs, academic years, staff, students, and fee structures, with an admin UI optimized for institutional workflows. It supports role-based administration, CSV bulk uploads, and streamlined data entry for school admins.

Key Features
------------
- Institution management: `InstitutionProfile`, academic years, terms, faculties, and programs
- Student records with program and academic year associations
- Staff management with password set/update in admin
- Admin UI improvements (Jazzmin theme overrides for readable dropdowns)
- Bulk data import workflows using CSV
- Sample data generators and quick commands

Tech Stack
----------
- Backend: Django
- Database: SQLite (development)
- Admin UI: Django Admin + Jazzmin tweaks
- Deployment: Render (Procfile, render.yaml)

Repository Structure
--------------------
- Root
   - `requirements.txt` — Python dependencies
   - `Procfile`, `render.yaml` — deployment configuration
   - `README.md` — this guide
   - `EduPayAfrica/` — main Django project and apps

Project Apps (high level)
-------------------------
- `institutions/` — core institutional models, admin customizations, management commands
- `accounts/` — authentication helpers and views
- `core/`, `leads/`, `platform_admin/` — additional domain modules

Getting Started
---------------
1) Install dependencies
    - Create/activate your virtual environment
    - Install requirements

```
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

2) Apply migrations

```
cd EduPayAfrica
python manage.py migrate
```

3) Create a superuser

```
python manage.py createsuperuser
```

4) Run the development server

```
python manage.py runserver
```

Admin Panel
-----------
- URL: `http://localhost:8000/admin/`
- Dropdowns for Institution/Program/Academic Year are styled for readability
- Staff admin allows setting/updating passwords via custom form fields

Environment & Secrets
---------------------
- Do not commit service account JSON or secrets to the repository.
- Use environment variables or external secret managers for credentials.

Deployment (Render)
-------------------
- The repo includes `Procfile` and `render.yaml` for Render deployment.
- Ensure environment variables are configured in Render dashboard.

Notes
-----
- Default database is SQLite for local development; switch to Postgres or MySQL in production.
- Keep `requirements.txt` updated when adding packages.
- Avoid placing secrets in the repo.

# EduPay Africa

## Overview

EduPay Africa is a continent-wide school payment platform designed specifically for African educational institutions. Starting in Kenya and expanding across Africa, the platform simplifies fee collection, management, and reconciliation for schools while providing parents with a seamless payment experience.

## Features

- **Institution Management**: Manage schools and educational institutions
- **Demo Request Workflow**: Handle demo requests with approval and institution linking
- **User Management**: Create and manage users with role-based access control
- **Institution Admins**: Track and manage institution administrators
- **Audit Logging**: Complete audit trail for all administrative actions
- **Firebase Authentication**: Secure authentication system
- **Demo Request Tracking**: Full workflow from request to completion

## Tech Stack

- **Backend**: Django 6.0.1
- **Database**: SQLite (Development)
- **Authentication**: Firebase
- **Frontend**: Bootstrap 5, HTML/CSS/JavaScript
- **Python**: 3.14.0

## Project Structure

```
EduPayAfrica/
├── accounts/              # User authentication
├── leads/                 # Demo request management
├── core/                  # Core application logic
├── platform_admin/        # Admin dashboard
├── static/                # CSS, JavaScript, images
├── templates/             # HTML templates
├── EduPayAfrica/          # Main Django settings
└── manage.py              # Django management script
```

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/FranNMK/EduPayAfrica.git
   cd EduPayAfrica
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Apply migrations:
   ```bash
   python manage.py migrate
   ```

5. Create a superuser:
   ```bash
   python manage.py createsuperuser
   ```

6. Run the development server:
   ```bash
   python manage.py runserver
   ```

## Admin Dashboard

Access the admin dashboard at `http://localhost:8000/admin/` with features including:
- Institution Management
- Demo Request Tracking
- User & Role Management
- Institution Admin Directory
- Audit Logs

## Usage

### Managing Institutions
Navigate to the Institutions section to:
- Add new institutions
- Assign institution admins
- Update institution details
- Change institution status (Approve, Activate, Suspend, etc.)

### Managing Users
In the Users section you can:
- Create new system users
- Assign roles and institutions
- Enable/disable accounts
- Track user activity

### Demo Requests
Track demo requests through the workflow:
1. Receive demo request
2. Approve and create institution
3. Assign admin
4. Track completion

## Contributing

1. Create a feature branch (`git checkout -b feature/AmazingFeature`)
2. Commit changes (`git commit -m 'Add AmazingFeature'`)
3. Push to branch (`git push origin feature/AmazingFeature`)
4. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support, email support@edupayafrica.com or open an issue on GitHub.

## Authors

- **FranNMK** - Initial work and maintenance
