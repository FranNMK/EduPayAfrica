# Render Deployment Quick Start Checklist

## Pre-Deployment (Local)

- [ ] Update `requirements.txt` with production packages (✓ Done: gunicorn, dj-database-url, psycopg2, whitenoise)
- [ ] Update `settings.py` for production (✓ Done: DATABASE_URL, ALLOWED_HOSTS, STATIC_ROOT, WhiteNoise)
- [ ] Create `Procfile` (✓ Done)
- [ ] Create `render.yaml` (✓ Done)
- [ ] Test locally: `python manage.py collectstatic --no-input`
- [ ] Commit all changes: `git add . && git commit -m "Prepare for Render deployment"`
- [ ] Push to GitHub: `git push origin main`

## Render Setup

### 1. Create Render Account
- [ ] Go to https://render.com
- [ ] Sign up with GitHub
- [ ] Connect GitHub repository

### 2. Create PostgreSQL Database
- [ ] Render Dashboard → New + → PostgreSQL
- [ ] **Name:** edupay-db
- [ ] **Region:** oregon (or closest to you)
- [ ] **PostgreSQL Version:** 15
- [ ] Create
- [ ] Copy the **Internal Database URL** (it's auto-populated later)

### 3. Create Web Service
- [ ] Render Dashboard → New + → Web Service
- [ ] Select your GitHub repository
- [ ] **Name:** edupay-africa
- [ ] **Environment:** Python 3
- [ ] **Region:** oregon (same as database)
- [ ] **Branch:** main
- [ ] **Build Command:** (Render will auto-detect from Procfile)
- [ ] **Start Command:** (Render will auto-detect from Procfile)

### 4. Add Environment Variables

Go to Web Service → Environment and add:

```
DEBUG=False
RENDER=true
SECRET_KEY=your-new-secure-key-here

ALLOWED_HOSTS=edupay-africa.onrender.com

DATABASE_URL=(copy from PostgreSQL database)

FIREBASE_API_KEY=your-firebase-key
FIREBASE_PROJECT_ID=your-firebase-project-id
FIREBASE_AUTH_DOMAIN=your-firebase-auth-domain
FIREBASE_STORAGE_BUCKET=your-firebase-storage-bucket
FIREBASE_CREDENTIALS_PATH=/opt/render/project/src/firebase-key.json

SUPER_ADMIN_EMAIL=your-admin-email@example.com

EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
```

### 5. Add Firebase Credentials Secret File

Option A: Base64 Environment Variable (Recommended)
```bash
# On your local machine, convert Firebase JSON to base64
cat edupay-africa-firebase-adminsdk-fbsvc-5166074225.json | base64 -w 0
```
- Add new env var: `FIREBASE_CREDENTIALS_BASE64` = (paste the base64 output)

Option B: Secret File
- Render Dashboard → Web Service → Environment → Secret Files
- **Filename:** `firebase-key.json`
- **Contents:** (paste entire Firebase JSON file)

### 6. Deploy
- [ ] Click "Create Web Service"
- [ ] Wait for deployment to complete
- [ ] Check logs for any errors
- [ ] Once "Deploy successful" appears, app is live!

## Post-Deployment

### 1. Create Superuser
- [ ] Go to Web Service → Shell
- [ ] Run: `python manage.py createsuperuser`
- [ ] Enter email, password

### 2. Test the App
- [ ] Visit `https://edupay-africa.onrender.com`
- [ ] Login at `/login` with superuser credentials
- [ ] Test admin dashboard at `/platform-admin/`

### 3. Update Domain (if you have custom domain)
- [ ] Render Dashboard → Settings → Custom Domain
- [ ] Add your domain name
- [ ] Update DNS records as shown in Render

### 4. Monitor and Troubleshoot
- [ ] View logs: Web Service → Logs
- [ ] Common issues:
  - **502 Bad Gateway:** Check build command output, env vars
  - **Static files not loading:** Run migrations, collectstatic
  - **Database connection error:** Verify DATABASE_URL format
  - **Authentication fails:** Check FIREBASE_* env vars

## Useful Links

- **Render Dashboard:** https://dashboard.render.com
- **Django on Render:** https://render.com/docs/deploy-django
- **Environment Variables:** https://render.com/docs/environment-variables
- **Troubleshooting:** https://render.com/docs/troubleshooting

## Cost Notes

**Free Tier:**
- Web Service: ~$0.10/hour (auto-spins down after 15 min inactivity)
- PostgreSQL: Free for 90 days, then upgrade required
- Static files served from Render (included)

**Recommendation for Production:**
- Upgrade to paid PostgreSQL database
- Consider paid web service plan for continuous uptime
- Configure backup for database

## After Everything Works

- [ ] Update `README.md` with live app URL
- [ ] Test all features thoroughly
- [ ] Set up error monitoring (Sentry, etc.)
- [ ] Configure custom domain (if applicable)
- [ ] Set up automated backups
- [ ] Monitor database usage
