# Render.com Deployment Guide for EduPay Africa

## Step-by-Step Deployment Instructions

### Prerequisites
1. GitHub account with your repository pushed
2. Render.com free account (https://render.com)
3. Firebase project credentials

### Step 1: Prepare Your Repository

Ensure your `.gitignore` includes sensitive files:
```
.env
*.json (Firebase credentials)
venv/
db.sqlite3
__pycache__/
```

Push all changes to GitHub:
```bash
git add .
git commit -m "Prepare for Render deployment"
git push origin main
```

### Step 2: Create Render Account and Connect GitHub

1. Go to https://render.com and sign up
2. Click "New +" → "Web Service"
3. Select "Build and deploy from a Git repository"
4. Connect your GitHub account
5. Select the `EduPayAfrica` repository

### Step 3: Configure Web Service

**Name:** edupay-africa
**Environment:** Python 3
**Region:** Choose closest to your users (e.g., Oregon)
**Branch:** main
**Build Command:**
```bash
pip install -r requirements.txt && python manage.py collectstatic --no-input && python manage.py migrate
```

**Start Command:**
```bash
gunicorn EduPayAfrica.wsgi:application
```

### Step 4: Add Environment Variables

In Render dashboard → Environment, add these variables:

```
SECRET_KEY=your-django-secret-key-here
DEBUG=False
ALLOWED_HOSTS=yourdomain.onrender.com
DATABASE_URL=postgresql://user:password@host:5432/database
RENDER=true

FIREBASE_API_KEY=your-firebase-api-key
FIREBASE_PROJECT_ID=your-firebase-project-id
FIREBASE_AUTH_DOMAIN=your-firebase-auth-domain
FIREBASE_STORAGE_BUCKET=your-firebase-storage-bucket
FIREBASE_CREDENTIALS_PATH=/opt/render/project/src/firebase-key.json

SUPER_ADMIN_EMAIL=your-admin-email@example.com
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
```

### Step 5: Add Firebase Credentials

Option A: Using Environment Variable (Recommended for Render)

1. Base64 encode your Firebase JSON:
   ```bash
   cat edupay-africa-firebase-adminsdk-fbsvc-5166074225.json | base64
   ```

2. Create environment variable `FIREBASE_CREDENTIALS_BASE64` with the encoded value

3. Update `accounts/firebase_auth.py` to decode it:
   ```python
   import base64
   
   if os.environ.get('FIREBASE_CREDENTIALS_BASE64'):
       cred_json = base64.b64decode(os.environ.get('FIREBASE_CREDENTIALS_BASE64')).decode('utf-8')
       cred_dict = json.loads(cred_json)
       cred = credentials.Certificate(cred_dict)
   ```

Option B: Add Firebase JSON to Render Secret Files
1. Add file path: `/opt/render/project/src/firebase-key.json`
2. Paste your Firebase credentials JSON content

### Step 6: Create Database

1. In Render dashboard → "Create +" → "PostgreSQL"
2. **Name:** edupay-db
3. **Region:** Same as your web service
4. **PostgreSQL Version:** 15
5. Create and copy the internal database URL

2. Add `DATABASE_URL` to your web service environment with this value

### Step 7: Configure Django Settings for Production

Update `EduPayAfrica/settings.py`:

```python
import dj_database_url

# Use DATABASE_URL environment variable
DATABASES = {
    'default': dj_database_url.config(
        default='sqlite:///db.sqlite3',
        conn_max_age=600
    )
}

# Allowed hosts
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', 'localhost').split(',')

# Security settings
SECURE_SSL_REDIRECT = not DEBUG
SESSION_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_SECURE = not DEBUG
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_SECURITY_POLICY = {
    "default-src": ("'self'",),
}

# Static files
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATIC_URL = '/static/'
```

Install `dj-database-url`:
```bash
pip install dj-database-url
```

Add to `requirements.txt`:
```
dj-database-url==2.1.0
gunicorn==21.2.0
python-dotenv==1.0.0
```

### Step 8: Deploy

1. Click "Create Web Service"
2. Render will automatically:
   - Install dependencies from `requirements.txt`
   - Run collectstatic
   - Run migrations
   - Start the web service

3. Wait for "Deploy successful" message
4. Your app is now live at: `https://edupay-africa.onrender.com`

### Step 9: Post-Deployment

1. **Create Superuser:**
   ```bash
   On Render Shell:
   python manage.py createsuperuser
   ```

2. **Test Admin Login:**
   - Navigate to `https://yourdomain.onrender.com/admin`
   - Login with superuser credentials

3. **Configure Email (Optional):**
   - Use Gmail App Password for EMAIL_HOST_PASSWORD
   - Or configure SendGrid/other email provider

4. **Monitor Logs:**
   - In Render dashboard → Logs
   - Check for any errors

### Important Notes

- **Free tier:** Limited resources, auto-spins down after 15 min inactivity
- **Database:** PostgreSQL free tier limited to 90 days (production: upgrade)
- **Static files:** Configure S3 or Cloudinary for production media storage
- **Email:** Console backend in development; use SMTP for production
- **CORS:** May need to update for production domain

### Troubleshooting

**502 Bad Gateway:**
- Check deployment logs in Render
- Verify Build Command succeeded
- Check environment variables are set

**Database Connection Error:**
- Verify DATABASE_URL format
- Check database is running
- Ensure migrations ran

**Static files not loading:**
- Run: `python manage.py collectstatic --no-input`
- Check STATIC_ROOT is set

**Login/Auth Issues:**
- Verify FIREBASE_* env vars are correct
- Check FIREBASE_CREDENTIALS_PATH exists
- Test locally with same env vars

### Useful Render Commands

**View logs:**
```
In Render dashboard → Your Service → Logs
```

**Run Django commands:**
```
In Render dashboard → Shell (for your web service)
python manage.py migrate
python manage.py createsuperuser
```

**Restart service:**
```
Render dashboard → Manual Deploy → Deploy latest commit
```
