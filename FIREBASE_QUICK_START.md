# Firebase Authentication - Quick Setup Guide

## What Was Done

✅ **Firebase authentication is now fully integrated!** When you log in, the system will:
1. Authenticate your email/password with Firebase
2. Automatically create a Django user account
3. Grant you Super Admin permissions
4. Redirect you to the Super Admin dashboard

---

## 3 Steps to Get Started

### Step 1: Set Up Environment Variables

Create `.env` file in: `c:/Users/mc/Desktop/Edu/EduPayAfrica/.env`

Add these lines with your Firebase credentials:

```env
# Firebase Web Configuration (from Firebase Console)
FIREBASE_API_KEY=AIzaSyD...YOUR_KEY_HERE...
FIREBASE_AUTH_DOMAIN=your-project.firebaseapp.com
FIREBASE_PROJECT_ID=your-project-id
FIREBASE_STORAGE_BUCKET=your-project.appspot.com
FIREBASE_MESSAGING_SENDER_ID=1234567890
FIREBASE_APP_ID=1:1234567890:web:abcdef123456
FIREBASE_MEASUREMENT_ID=G-XXXXXXXXXX

# Firebase Admin SDK
FIREBASE_CREDENTIALS_PATH=/path/to/firebase-serviceAccountKey.json

# Super Admin Email
SUPER_ADMIN_EMAIL=frankmk2025@gmail.com
```

**Where to find these:**
- Login to [Firebase Console](https://console.firebase.google.com)
- Select your project
- Go to **Project Settings** → find web config
- Download service account JSON from **Service Accounts** tab

### Step 2: Create Firebase User

In Firebase Console:
1. Go to **Authentication** → **Users**
2. Click **Add user**
3. Email: `frankmk2025@gmail.com`
4. Password: `YourSecurePassword` (set something strong!)
5. Click **Add user**

### Step 3: Test Login

```bash
# Start Django server
cd c:/Users/mc/Desktop/Edu/EduPayAfrica
python manage.py runserver
```

Then:
1. Open browser: `http://localhost:8000/login/`
2. Enter your Firebase credentials
3. Click **Sign In**
4. ✅ You should see the Super Admin dashboard!

---

## How It Works

| When You Login | System Does |
|---|---|
| Enter email & password | Sends to Firebase for verification |
| Firebase verifies | Returns secure ID token |
| System checks token | Confirms it's valid |
| Creates Django user | Syncs your Firebase profile with Django |
| Detects Super Admin email | Grants `is_staff` and `is_superuser` |
| Creates session | Logs you in as Super Admin |
| Redirects | Takes you to `/platform-admin/` dashboard |

---

## Key Features

🔐 **Secure**
- Passwords never stored in Django
- Firebase handles all authentication
- ID tokens verified server-side

🚀 **Automatic**
- User profile auto-synced from Firebase
- Super Admin permissions auto-granted
- Dashboard auto-selected based on role

🎯 **Flexible**
- "Remember me" option (extends session to 30 days)
- Auto-redirects to correct dashboard
- Works with multiple Firebase users

---

## Files Modified/Created

```
✅ accounts/firebase_auth.py          (NEW - Firebase auth service)
✅ accounts/views.py                  (UPDATED - uses Firebase)
✅ EduPayAfrica/settings.py           (UPDATED - Firebase config)
✅ FIREBASE_AUTH_SETUP.md             (NEW - detailed guide)
✅ FIREBASE_QUICK_START.md            (NEW - this file)
```

---

## Troubleshooting

### "Invalid email or password" error?
- Check Firebase user exists with that email
- Verify password is correct in Firebase Console
- Make sure Email/Password auth is enabled in Firebase

### "Firebase credentials not configured"?
- Create `.env` file in project root
- Add `FIREBASE_CREDENTIALS_PATH` pointing to your JSON key file
- Restart Django server

### Can't access Super Admin dashboard?
- Verify email matches `SUPER_ADMIN_EMAIL` in `.env`
- Check browser console for JavaScript errors
- Clear browser cache and retry

---

## What's Next?

With Firebase Auth set up, you can now:

1. ✅ **Log in as Super Admin** with frankmk2025@gmail.com
2. ✅ **Access the platform admin dashboard** at `/platform-admin/`
3. ✅ **Manage institutions** (approve, activate, suspend)
4. ✅ **Track demo requests** from leads
5. ✅ **Manage users and roles**
6. ✅ **View audit logs** of all actions

---

## Quick Commands

```bash
# Verify setup
python manage.py check

# Start development server
python manage.py runserver

# Create additional super admin (Django shell)
python manage.py shell
>>> from django.contrib.auth import get_user_model
>>> User = get_user_model()
>>> User.objects.create_superuser('admin@example.com', 'admin@example.com', 'password')
```

---

## Need Help?

Check these files:
- **Setup Details**: `FIREBASE_AUTH_SETUP.md`
- **Auth Code**: `accounts/firebase_auth.py`
- **Login View**: `accounts/views.py`
- **Config**: `EduPayAfrica/settings.py`
- **Error Logs**: Django console output

Good luck! 🚀
