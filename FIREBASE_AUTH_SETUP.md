# Firebase Authentication Setup for EduPay Africa

## Overview
The login system now uses **Firebase Authentication** to verify users. When you log in with your Firebase credentials, the system:
1. Authenticates against Firebase
2. Syncs user data with Django
3. Automatically grants Super Admin permissions to the designated admin email
4. Redirects to the appropriate dashboard

---

## Prerequisites

### 1. Firebase Project Setup
You need a Firebase project with Email/Password authentication enabled.

**Steps:**
1. Go to [Firebase Console](https://console.firebase.google.com)
2. Create or select your project
3. Go to **Authentication** → **Sign-in method**
4. Enable **Email/Password** authentication
5. Go to **Project Settings** → **Service Accounts**
6. Click **Generate New Private Key** and download the JSON file

### 2. Get Firebase Configuration

In Firebase Console:
- **Project Settings** → **General tab**
- Scroll down to "Your apps" section
- Click the Web app (if not created, create one)
- Copy the firebaseConfig object

---

## Environment Variables Setup

Create a `.env` file in your project root (`c:/Users/mc/Desktop/Edu/EduPayAfrica/.env`):

```env
# Django Settings
SECRET_KEY=your-django-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Firebase Web Configuration (from Console)
FIREBASE_API_KEY=AIzaSyD...
FIREBASE_AUTH_DOMAIN=your-project.firebaseapp.com
FIREBASE_PROJECT_ID=your-project-id
FIREBASE_STORAGE_BUCKET=your-project.appspot.com
FIREBASE_MESSAGING_SENDER_ID=123456789
FIREBASE_APP_ID=1:123456789:web:abc123def456
FIREBASE_MEASUREMENT_ID=G-XXXXXXXXXX

# Firebase Admin SDK (Service Account)
FIREBASE_CREDENTIALS_PATH=/path/to/serviceAccountKey.json

# Super Admin Email (this account gets is_staff and is_superuser)
SUPER_ADMIN_EMAIL=frankmk2025@gmail.com

# Email Configuration
DEFAULT_FROM_EMAIL=noreply@edupayafrica.com
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
```

### About `FIREBASE_CREDENTIALS_PATH`
- Download your Firebase service account key (JSON file)
- Save it in a secure location (e.g., `c:/Users/mc/Desktop/Edu/firebase-key.json`)
- Set `FIREBASE_CREDENTIALS_PATH` to the full path
- **DO NOT commit this file to version control** - add it to `.gitignore`

---

## How It Works

### Login Flow

```
1. User enters email (frankmk2025@gmail.com) and password
   ↓
2. System calls Firebase REST API to authenticate
   ↓
3. Firebase returns an ID Token if credentials are valid
   ↓
4. System verifies the token with Firebase Admin SDK
   ↓
5. Django user created/updated from Firebase user data
   ↓
6. If email matches SUPER_ADMIN_EMAIL → grant is_staff + is_superuser
   ↓
7. User logged into Django session
   ↓
8. Redirected to /platform-admin/ dashboard (if Super Admin)
```

### Key Features

| Feature | Description |
|---------|-------------|
| **Stateless** | No passwords stored in Django; Firebase handles authentication |
| **Auto-sync** | User info synced from Firebase on each login |
| **Super Admin Detection** | Email in SUPER_ADMIN_EMAIL automatically gets admin permissions |
| **Session Management** | "Remember me" option extends session timeout |
| **Error Handling** | Clear error messages for invalid credentials |

---

## Testing the Login

### Step 1: Create Firebase User
1. Firebase Console → **Authentication** → **Users tab**
2. Click **Add user**
3. Email: `frankmk2025@gmail.com`
4. Password: `YourSecurePassword123`
5. Click **Add user**

### Step 2: Start Django Server
```bash
cd c:/Users/mc/Desktop/Edu/EduPayAfrica
python manage.py runserver
```

### Step 3: Test Login
1. Navigate to `http://localhost:8000/login/`
2. Enter:
   - Email: `frankmk2025@gmail.com`
   - Password: `YourSecurePassword123`
   - Optionally check "Remember me"
3. Click **Sign In**
4. Should redirect to `/platform-admin/` dashboard

### Expected Results
- ✅ User created/updated in Django
- ✅ `is_staff` set to True
- ✅ `is_superuser` set to True
- ✅ Can access Super Admin dashboard
- ✅ All data in platform admin visible

---

## Troubleshooting

### Error: "Firebase credentials not configured"
**Solution**: Ensure `.env` file has `FIREBASE_CREDENTIALS_PATH` set to valid JSON file path.

```bash
# Check if file exists
Test-Path "c:/Users/mc/Desktop/Edu/firebase-key.json"
```

### Error: "FIREBASE_API_KEY not configured"
**Solution**: Add `FIREBASE_API_KEY` to `.env` file (from Firebase Console).

### Error: "Invalid email or password"
**Possible causes:**
1. Firebase user doesn't exist - create it in Firebase Console
2. Wrong password - verify in Firebase user settings
3. Email/password authentication not enabled in Firebase

### Can't access Super Admin dashboard after login
**Solution**: Check that:
1. Email matches `SUPER_ADMIN_EMAIL` in `.env`
2. No SQL errors - check Django console output
3. Clear browser cache and try again

---

## Architecture

```
┌─────────────────────────────────────────────┐
│         Login Page (HTML Form)              │
│    frankmk2025@gmail.com + password         │
└────────────┬────────────────────────────────┘
             │ POST /login/
             ↓
┌─────────────────────────────────────────────┐
│    Django accounts/views.py                 │
│      (login_view function)                  │
└────────────┬────────────────────────────────┘
             │
             ↓
┌─────────────────────────────────────────────┐
│    Firebase Auth Service                    │
│  (accounts/firebase_auth.py)                │
│                                             │
│  1. Call Firebase REST API                  │
│  2. Verify ID Token with Admin SDK          │
│  3. Create/Update Django User               │
│  4. Set is_staff/is_superuser if needed     │
└────────────┬────────────────────────────────┘
             │
             ↓
┌─────────────────────────────────────────────┐
│         Django Session Created              │
│      User Logged In Successfully            │
└────────────┬────────────────────────────────┘
             │
             ↓
┌─────────────────────────────────────────────┐
│   Redirect to /platform-admin/              │
│     (Super Admin Dashboard)                 │
└─────────────────────────────────────────────┘
```

---

## Security Notes

✅ **Best Practices Implemented:**
- No passwords stored in Django
- Firebase handles password security
- ID tokens verified server-side
- Session timeout support
- Automatic user role synchronization
- Super Admin email configuration via environment variable

⚠️ **Additional Recommendations for Production:**
1. Use environment variables for all secrets
2. Enable Firebase security rules (default deny)
3. Implement rate limiting on login endpoint
4. Monitor authentication failures
5. Use HTTPS only
6. Implement 2FA in Firebase Console
7. Regularly rotate service account keys

---

## API Reference

### `firebase_login(request, email: str, password: str) -> User`
Main authentication function. Call this from your view.

**Parameters:**
- `request`: Django HttpRequest
- `email`: User email (must exist in Firebase)
- `password`: User password (set in Firebase)

**Returns:**
- Django User object if successful
- None if authentication fails

**Usage:**
```python
from accounts.firebase_auth import firebase_login

user = firebase_login(request, email, password)
if user:
    login(request, user)
    return redirect('home')
else:
    messages.error(request, 'Invalid credentials')
```

### `verify_firebase_token(id_token: str) -> dict`
Verify a Firebase ID token.

**Parameters:**
- `id_token`: Firebase ID token from client

**Returns:**
- Decoded token claims (dict) if valid
- None if invalid

---

## Next Steps

1. ✅ Set up `.env` file with Firebase credentials
2. ✅ Create Firebase user with your email
3. ✅ Test login at `/login/`
4. ✅ Access Super Admin dashboard at `/platform-admin/`
5. Create additional institution admin users as needed
6. Implement role-based dashboards for other user types

---

## Support

For Firebase documentation: https://firebase.google.com/docs/auth
For Django integration issues, check:
- `accounts/firebase_auth.py` - Authentication service
- `accounts/views.py` - Login view
- `.env` - Configuration
- Django console output for detailed error messages
