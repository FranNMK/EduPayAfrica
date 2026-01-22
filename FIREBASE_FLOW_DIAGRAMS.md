# Firebase Authentication Flow - Visual Guide

## 1. LOGIN SEQUENCE

```
USER VISITS /LOGIN/
      ↓
SEES LOGIN FORM
├─ Email field
├─ Password field  
├─ "Remember me" checkbox
└─ "Sign In" button
      ↓
USER ENTERS CREDENTIALS
├─ Email: frankmk2025@gmail.com
├─ Password: ••••••••
└─ Submits form (POST /login/)
      ↓
DJANGO RECEIVES REQUEST (accounts/views.py)
├─ Extracts email & password
├─ Validates not empty
└─ Calls firebase_login()
      ↓
FIREBASE SERVICE (accounts/firebase_auth.py)
├─ authenticate_firebase_user()
│  ├─ Calls Firebase REST API
│  ├─ URL: https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword
│  ├─ Sends: {email, password, apiKey}
│  └─ Receives: {idToken, refreshToken, ...}
│       ↓
│     verify_firebase_token()
│     ├─ Verifies token signature
│     ├─ Decodes JWT
│     └─ Extracts claims: {uid, email, name, ...}
│       ↓
│     get_or_create_django_user()
│     ├─ Queries Django database
│     ├─ User exists? Update
│     └─ User missing? Create
│       ↓
└─ RETURNS Django User object
      ↓
PERMISSION CHECK
├─ Email == frankmk2025@gmail.com?
├─ YES → Set is_staff=True, is_superuser=True
└─ NO → Regular user
      ↓
CREATE SESSION
├─ request.session created
├─ Check "Remember me"?
├─ YES → 30 day timeout
└─ NO → Browser session
      ↓
REDIRECT
├─ If Super Admin → /platform-admin/
└─ If Regular → /home/
      ↓
SUCCESS! ✅
```

---

## 2. DATA FLOW

```
FIREBASE CONSOLE                    DJANGO DATABASE
    ↓                                   ↓
User: {                         User: {
  email: "frank...",              username: "frank...",
  password_hash: "***",           email: "frank...",
  uid: "xyz123",                  is_staff: True,
  ...                             is_superuser: True,
}                                 ...
    ↓                             }
    └─ CREATE/UPDATE ─→ ┌─────────────────────┐
                        │  PlatformUserProfile│
                        │ {                   │
                        │   user: User,       │
                        │   role: "super_admin"
                        │ }                   │
                        └─────────────────────┘
                                   ↓
                        ACCESSIBLE VIA
                        └─ auth.user.platform_profile
```

---

## 3. AUTHENTICATION COMPARISON

### BEFORE (Django Default)
```
User Input
    ↓
Django authenticate()
    ↓
Django checks local database
    ↓
If password matches, return User
    ↓
❌ PROBLEM: Passwords stored in database
```

### AFTER (Firebase)
```
User Input
    ↓
Firebase REST API
    ↓
Firebase verifies credentials
    ↓
Firebase returns secure token
    ↓
Django verifies token
    ↓
Django creates/updates user
    ↓
✅ SECURE: No passwords in Django database
```

---

## 4. USER CREATION FLOW

```
FIRST LOGIN WITH FIREBASE USER
      ↓
Django receives request
      ↓
firebase_login() called
      ↓
Firebase authenticates
      ↓
Token verified
      ↓
get_or_create_django_user()
│
├─ Query: User.objects.get(username="frank@email.com")
│    ↓
│    ❌ NOT FOUND (first time)
│
├─ CREATE NEW USER
│  User.objects.create(
│    username="frank@email.com",
│    email="frank@email.com",
│    first_name="Frank",
│    last_name="",
│  )
│
├─ Check SUPER_ADMIN_EMAIL
│  ├─ Is super admin? YES
│  ├─ Set is_staff=True
│  └─ Set is_superuser=True
│
└─ Return User object
      ↓
SUBSEQUENT LOGINS WITH SAME USER
      ↓
get_or_create_django_user()
│
├─ Query: User.objects.get(username="frank@email.com")
│    ↓
│    ✅ FOUND
│
├─ Update existing user
│  user.email = "frank@email.com"
│  user.save()
│
└─ Return User object
      ↓
MIDDLEWARE
│
├─ PlatformUserProfileMiddleware runs
├─ PlatformUserProfile.objects.get_or_create(user=user)
└─ Profile auto-created if missing
```

---

## 5. SESSION MANAGEMENT

```
AFTER SUCCESSFUL LOGIN
      ↓
Check "Remember me" checkbox?
      ↓
YES ──────────────────────┐
    │                      │
    ├─ request.session.set_expiry(30 * 24 * 60 * 60)
    │                      │
    └─ Session lives 30 days
       (even after browser close)
    
NO ───────────────────────┐
    │                      │
    ├─ request.session.set_expiry(0)
    │                      │
    └─ Session expires when browser closes
       (after you close all tabs)
```

---

## 6. ERROR HANDLING

```
LOGIN ATTEMPT
      ↓
VALIDATION
├─ Email empty? → "Please enter email"
├─ Password empty? → "Please enter password"
└─ Continue...
      ↓
FIREBASE CALL
├─ Firebase API error?
│  └─ "Authentication failed - try again"
├─ Invalid credentials?
│  └─ "Invalid email or password"
└─ Success → Continue
      ↓
TOKEN VERIFICATION
├─ Token invalid?
│  └─ "Invalid credentials"
├─ Token expired?
│  └─ "Session expired - login again"
└─ Valid → Continue
      ↓
USER CREATION
├─ Database error?
│  └─ "System error - please try again"
├─ Success?
│  └─ Create session → Redirect
```

---

## 7. ENVIRONMENT VARIABLES

```
.env FILE (project root)
│
├─ FIREBASE_API_KEY
│  └─ Used for REST API authentication
│
├─ FIREBASE_AUTH_DOMAIN
│  └─ Identifies Firebase project
│
├─ FIREBASE_PROJECT_ID
│  └─ Firebase project identifier
│
├─ FIREBASE_CREDENTIALS_PATH
│  └─ Path to service account JSON key
│     Used for Admin SDK token verification
│
├─ SUPER_ADMIN_EMAIL
│  └─ Email that gets super admin permissions
│
└─ Other config...
```

---

## 8. PERMISSION MATRIX

```
                    REGULAR USER    SUPER ADMIN
                    ────────────    ───────────
View Home                   ✅             ✅
View Dashboard              ❌             ✅
Institution Mgmt            ❌             ✅
Demo Tracking               ❌             ✅
User Oversight              ❌             ✅
Settings Config             ❌             ✅
Audit Logs                  ❌             ✅
Edit User Data              ❌             ✅
```

---

## 9. DATABASE SCHEMA RELATIONSHIPS

```
Django AUTH Database
├─ auth_user
│  ├─ id (PK)
│  ├─ username: "frankmk2025@gmail.com"
│  ├─ email: "frankmk2025@gmail.com"
│  ├─ password: "!sha256$..." (not used with Firebase)
│  ├─ is_staff: True ←─────────────────┐
│  ├─ is_superuser: True ←─────────────┤─ Set by firebase_auth.py
│  ├─ first_name: "Frank"              │
│  ├─ is_active: True ←─────────────────┘
│  └─ ...
│
└─ auth_session
   ├─ session_key: "abc123..."
   ├─ session_data: {...}
   ├─ expire_date: (datetime)
   └─ ...

Platform Admin Database
└─ platform_admin_platformuserprofile
   ├─ id (PK)
   ├─ user_id (FK) → auth_user.id
   ├─ role: "super_admin"
   ├─ role_conflict: False
   └─ ...
```

---

## 10. REQUEST LIFECYCLE (COMPLETE)

```
┌─────────────────────────────────────────────────────────┐
│1. USER OPENS http://localhost:8000/login/              │
└─────────────────────────────────────────────────────────┘
              ↓
┌─────────────────────────────────────────────────────────┐
│2. DJANGO RENDERS login.html FORM                        │
│   - Email field                                         │
│   - Password field                                      │
│   - Remember me checkbox                               │
│   - Submit button                                       │
└─────────────────────────────────────────────────────────┘
              ↓
┌─────────────────────────────────────────────────────────┐
│3. USER FILLS FORM & SUBMITS                             │
│   POST /login/                                          │
│   Body: {email: "frank@...", password: "...", ...}     │
└─────────────────────────────────────────────────────────┘
              ↓
┌─────────────────────────────────────────────────────────┐
│4. DJANGO RECEIVES REQUEST (login_view function)         │
│   - Extract form data                                   │
│   - Validate input                                      │
│   - Call firebase_login(request, email, password)      │
└─────────────────────────────────────────────────────────┘
              ↓
┌─────────────────────────────────────────────────────────┐
│5. FIREBASE SERVICE PROCESSES LOGIN                      │
│   accounts/firebase_auth.py:firebase_login()            │
│   a) authenticate_firebase_user(email, password)        │
│      - REST API POST to Firebase                        │
│      - Firebase checks password                         │
│      - Returns idToken                                  │
│   b) verify_firebase_token(idToken)                     │
│      - Admin SDK verifies token                         │
│      - Returns decoded claims                           │
│   c) get_or_create_django_user(claims)                  │
│      - Create/update Django user                        │
│      - Extract email, name, etc.                        │
│   d) Check if super admin                               │
│      - Email == frankmk2025@gmail.com?                  │
│      - Set is_staff, is_superuser if yes               │
│   e) Return User object                                 │
└─────────────────────────────────────────────────────────┘
              ↓
┌─────────────────────────────────────────────────────────┐
│6. DJANGO CREATES SESSION                                │
│   django.contrib.auth.login(request, user)              │
│   - Session ID generated                                │
│   - User ID stored in session                           │
│   - Session cookie sent to browser                      │
│   - Remember me timeout set                             │
└─────────────────────────────────────────────────────────┘
              ↓
┌─────────────────────────────────────────────────────────┐
│7. DJANGO REDIRECTS USER                                 │
│   if user.is_superuser:                                 │
│     return redirect('platform_admin:dashboard')         │
│   else:                                                 │
│     return redirect('home')                             │
└─────────────────────────────────────────────────────────┘
              ↓
┌─────────────────────────────────────────────────────────┐
│8. BROWSER FOLLOWS REDIRECT                              │
│   GET /platform-admin/                                  │
│   (with session cookie in request headers)              │
└─────────────────────────────────────────────────────────┘
              ↓
┌─────────────────────────────────────────────────────────┐
│9. DJANGO CHECKS PERMISSION                              │
│   @super_admin_required decorator                       │
│   if not user.is_staff or not user.is_superuser:        │
│     → Redirect to login                                 │
│   else:                                                 │
│     → Continue to view                                  │
└─────────────────────────────────────────────────────────┘
              ↓
┌─────────────────────────────────────────────────────────┐
│10. DJANGO RENDERS DASHBOARD                             │
│    platform_admin/templates/platform_admin/dashboard.html
│    - Query aggregated data                              │
│    - Render template                                    │
│    - Return HTML to browser                             │
└─────────────────────────────────────────────────────────┘
              ↓
┌─────────────────────────────────────────────────────────┐
│11. BROWSER DISPLAYS DASHBOARD                           │
│    - Metrics cards                                      │
│    - Navigation menu                                    │
│    - Links to features                                  │
│    - User can interact                                  │
└─────────────────────────────────────────────────────────┘
              ↓
         ✅ SUCCESS!
```

---

## 11. TROUBLESHOOTING FLOWCHART

```
LOGIN FAILS
    ↓
CHECK: Is .env file created?
├─ NO → Create .env with Firebase values
└─ YES → Continue
    ↓
CHECK: Are all Firebase config values filled?
├─ NO → Copy from Firebase Console
└─ YES → Continue
    ↓
CHECK: Does firebase-serviceAccountKey.json exist?
├─ NO → Download from Firebase Console
└─ YES → Continue
    ↓
CHECK: Does Firebase user exist?
├─ NO → Create user in Firebase Console
└─ YES → Continue
    ↓
CHECK: Is password correct?
├─ NO → Reset password in Firebase
└─ YES → Continue
    ↓
CHECK: Is Email/Password auth enabled in Firebase?
├─ NO → Enable in Firebase Console
└─ YES → Continue
    ↓
CHECK: Django console for errors
├─ See error? Fix based on error message
└─ No error? Clear cache and retry
    ↓
IF STILL FAILING:
├─ Restart Django server
├─ Check FIREBASE_CREDENTIALS_PATH points to valid file
├─ Verify all Firebase config in .env matches Console
└─ Check internet connection
```

---

**This guide covers the complete flow from login to super admin dashboard!**
