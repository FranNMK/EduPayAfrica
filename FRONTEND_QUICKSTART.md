# EduPay Africa Frontend - Quick Setup Guide

## 🚀 Quick Start

### Step 1: Install Dependencies
```bash
pip install django django-restframework python-dotenv
```

### Step 2: Apply Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### Step 3: Create Admin User
```bash
python manage.py createsuperuser
```

### Step 4: Collect Static Files
```bash
python manage.py collectstatic --noinput
```

### Step 5: Run Development Server
```bash
python manage.py runserver
```

### Step 6: Access the Platform
- **Website**: http://localhost:8000
- **Admin Panel**: http://localhost:8000/admin
- **Home Page**: http://localhost:8000/
- **Book Demo**: http://localhost:8000/demo/
- **About Us**: http://localhost:8000/about/
- **Contact**: http://localhost:8000/contact/
- **News**: http://localhost:8000/news/
- **Login**: http://localhost:8000/login/

---

## 📋 What's Included

### ✅ Complete Frontend Implementation
- **7 Main Pages**: Home, About, Contact, News, Demo, Login, Error pages
- **Responsive Design**: Works on mobile, tablet, and desktop
- **Professional Styling**: Bootstrap 5 + Custom CSS
- **Form Validation**: Client and server-side
- **Database Models**: DemoRequest model for lead capture
- **Django Views**: All URL patterns connected
- **Admin Interface**: Manage demo requests in admin panel

### ✅ Brand Identity
- **Logo Integration**: Uses EduPay Africa logo from static/images folder
- **Color Scheme**: Professional blue, purple, and orange palette
- **Typography**: Clean, readable fonts with proper hierarchy
- **Icons**: Font Awesome icons throughout

### ✅ User Experience
- **Navigation**: Clear, intuitive navigation bar
- **Mobile Menu**: Hamburger menu for mobile devices
- **Animations**: Smooth transitions and hover effects
- **Messaging**: Success/error alerts with auto-hide
- **Forms**: Professional form layouts with validation
- **Accessibility**: Semantic HTML, ARIA labels

---

## 🎨 Customization Guide

### Change Logo
Replace `static/images/EduPay Africa Logo.png` with your logo

### Change Colors
Edit CSS variables in `base.html`:
```css
:root {
    --primary-color: #1e40af;      /* Blue */
    --secondary-color: #7c3aed;    /* Purple */
    --accent-color: #f97316;       /* Orange */
}
```

### Edit Company Information
Update in footer and pages:
- Phone: +254 700 000 000
- Email: info@edupayafrica.com
- Location: Nairobi, Kenya

### Add Social Media Links
Update in `base.html` footer social links section

---

## 📧 Email Configuration

### Gmail Setup
In `settings.py`:
```python
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your-email@gmail.com'
EMAIL_HOST_PASSWORD = 'your-app-password'
DEFAULT_FROM_EMAIL = 'your-email@gmail.com'
```

### SendGrid Setup
```python
EMAIL_BACKEND = 'sendgrid_backend.SendgridBackend'
SENDGRID_API_KEY = 'your-sendgrid-key'
```

---

## 🔐 Security Setup

### Environment Variables
Create `.env` file:
```
DEBUG=False
SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=localhost,127.0.0.1,yourdomain.com
DATABASE_URL=postgresql://user:password@localhost/dbname
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
```

### Load Environment Variables
In `settings.py`:
```python
import os
from dotenv import load_dotenv
load_dotenv()
DEBUG = os.getenv('DEBUG', 'False') == 'True'
SECRET_KEY = os.getenv('SECRET_KEY')
```

---

## 📊 Admin Dashboard Features

### Demo Request Management
- View all demo bookings
- Filter by status, institution type, date
- Search by name, email, institution
- Add notes to requests
- Mark as scheduled/completed/cancelled
- Export data

### Access Admin
1. Go to http://localhost:8000/admin
2. Login with superuser credentials
3. Navigate to "Demo Requests"

---

## 🧪 Testing

### Test Demo Booking
1. Go to http://localhost:8000/demo/
2. Fill out the form
3. Submit
4. Check admin panel for the new request
5. Check email inbox for confirmation

### Test Contact Form
1. Go to http://localhost:8000/contact/
2. Fill out the contact form
3. Submit
4. Verify success message

### Test Responsive Design
1. Open browser DevTools (F12)
2. Toggle device toolbar (Ctrl+Shift+M)
3. Test on different screen sizes

---

## 🚀 Deployment

### Deployment Steps
1. Set DEBUG=False in settings
2. Configure allowed hosts
3. Use PostgreSQL database
4. Set up email service (SendGrid/Gmail)
5. Collect static files
6. Use Gunicorn as application server
7. Set up WhiteNoise for static files
8. Use SSL/HTTPS certificate
9. Set up backups
10. Configure error logging

### Recommended Platforms
- **Render**: Easy Django deployment
- **Railway**: Simple and affordable
- **Heroku**: Popular option (paid)
- **AWS**: Scalable solution
- **DigitalOcean**: Good performance

---

## 🐛 Troubleshooting

### Static Files Not Loading
```bash
python manage.py collectstatic --clear --noinput
```

### Logo Not Showing
- Ensure `static/images/EduPay Africa Logo.png` exists
- Check STATIC_URL in settings
- Run `python manage.py collectstatic`

### Forms Not Submitting
- Check CSRF token in form
- Verify email configuration
- Check browser console for errors
- Check Django logs

### Database Errors
```bash
python manage.py migrate --fake-initial
python manage.py migrate
```

### Port Already in Use
```bash
python manage.py runserver 8080
```

---

## 📚 File Structure Summary

```
EduPayAfrica/
├── templates/
│   ├── base.html              # ← Main template (navbar, footer)
│   ├── 404.html               # ← Error pages
│   ├── 500.html               # ← Error pages
│   ├── core/
│   │   ├── index.html         # ← Home
│   │   ├── about.html         # ← About Us
│   │   ├── contact.html       # ← Contact Us
│   │   └── news.html          # ← News & Careers
│   ├── leads/
│   │   └── demo.html          # ← Book Demo
│   └── accounts/
│       └── login.html         # ← Login
├── core/
│   ├── views.py               # ← Home, About, Contact, News views
│   ├── models.py
│   └── admin.py
├── leads/
│   ├── views.py               # ← Demo booking view
│   ├── models.py              # ← DemoRequest model
│   └── admin.py               # ← Admin interface
├── accounts/
│   ├── views.py               # ← Login view
│   └── models.py
├── static/
│   ├── images/
│   │   └── EduPay Africa Logo.png  # ← Brand logo
│   ├── css/
│   │   └── main.css           # ← Custom styles
│   └── js/
│       └── main.js            # ← Custom scripts
├── EduPayAfrica/
│   ├── settings.py            # ← Configuration
│   ├── urls.py                # ← URL routing
│   ├── wsgi.py
│   └── asgi.py
└── manage.py
```

---

## 🎯 Next Steps

1. **Customize Content**: Update company info, messages, and branding
2. **Configure Email**: Set up email service for notifications
3. **Add Firebase**: Integrate Firebase for authentication (Phase 2)
4. **Deploy**: Deploy to production platform
5. **Promote**: Share the URL with target institutions
6. **Monitor**: Track demo requests and website analytics
7. **Iterate**: Get feedback and improve features

---

## 📞 Support

For issues or questions:
- Check FRONTEND_IMPLEMENTATION.md for detailed documentation
- Review Django error logs
- Test in different browsers
- Check email configuration
- Verify database connectivity

---

## 🎉 Success!

Your EduPay Africa frontend is now fully implemented with:
✓ Professional design
✓ Mobile responsiveness
✓ Form handling
✓ Database integration
✓ Email notifications
✓ Admin interface
✓ Security best practices

**Ready to launch!**

---

**Last Updated**: January 20, 2024  
**Status**: ✅ Complete
