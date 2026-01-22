# Quick Reference Guide - Platform Admin Enhancements

## Three New Features Implemented

### 🎓 1. Demo Request Approval System

**What it does:** Converts demo requests into active institutions and assigns them to admin users.

**How to use:**
1. Login as super admin
2. Go to **Platform Admin → Demo Requests**
3. Find a pending request
4. Click **Approve** button
5. Select the admin to assign this institution to
6. Add any onboarding notes (optional)
7. Click **Approve** button in the modal
8. Done! Institution is now active in the system

**Alternative:** Click **Reject** to decline a demo request with a reason.

**What gets created:**
- ✅ Institution record
- ✅ Links admin user to institution
- ✅ Audit trail entry
- ✅ Status history log

---

### 👥 2. User Management System

**What it does:** Create new admin users who can login with Firebase credentials.

**How to create a user:**
1. Login as super admin
2. Go to **Platform Admin → Users**
3. Click **Create New User** (blue button)
4. Fill in the form:
   - **Full Name** - e.g., "John Smith"
   - **Email** - Will use this to login, e.g., "john@company.com"
   - **Password** - Minimum 6 characters
   - **Role** - Choose from Admin, Staff, or Viewer
5. Click **Create User**
6. User is immediately created and can login

**What happens:**
- ✅ User created in Firebase
- ✅ User created in Django database
- ✅ User can login immediately with email/password
- ✅ Audit log entry created

**Managing users:**
- Disable an account: Click **Disable** button (user can't login)
- Enable an account: Click **Enable** button (user can login again)

---

### 🔐 3. Password Reset for Frontend Users

**What it does:** Allows users to reset their forgotten passwords.

**How to reset password:**
1. Go to Login page
2. Click **"Forgot your password?"** link
3. Enter the email address
4. Click **Send Reset Link**
5. Check email for reset link
6. Click link to get reset code
7. Enter reset code and new password
8. Click **Reset Password**
9. Login with new password

**Password requirements:**
- Minimum 6 characters
- Use any combination of letters, numbers, symbols
- Don't need to match old password

---

## Admin Dashboard Routes

| Page | URL | Purpose |
|------|-----|---------|
| Demo Requests | `/platform-admin/demo-requests/` | Approve/reject demo requests |
| Users | `/platform-admin/users/` | Create and manage admin users |
| Institutions | `/platform-admin/institutions/` | View all institutions |
| Dashboard | `/platform-admin/dashboard/` | Overview of system |
| Audit Logs | `/platform-admin/audit-logs/` | View all system actions |

---

## Common Tasks

### ✅ Approve a Demo Request
1. Navigate to Demo Requests
2. Click Approve on any pending request
3. Choose admin user
4. Click Approve in modal
5. **Status:** Demo request → Approved ✓

### ✅ Create a New Admin User
1. Navigate to Users
2. Click "Create New User"
3. Fill: Name, Email, Password (6+ chars), Role
4. Click Create
5. **Status:** User can login immediately ✓

### ✅ Reset Forgotten Password
1. Go to Login page
2. Click "Forgot your password?"
3. Enter email
4. Check email for code
5. Enter code + new password
6. Login with new password ✓

### ✅ Disable a User Account
1. Navigate to Users
2. Find the user
3. Click "Disable" button
4. User cannot login until re-enabled ✓

---

## Important Notes

⚠️ **Security:**
- Passwords are encrypted in Firebase
- Only super admins can approve demos
- All actions are logged in audit trail
- Cannot undo rejections or deletions

⚠️ **Email Passwords:**
- Users must use the email address to login
- Password can be reset if forgotten
- Reset emails come from Firebase

⚠️ **Admin Assignment:**
- Each approved institution must be assigned to an admin
- Admins receive the institution in their profile
- One admin can manage multiple institutions

---

## Troubleshooting

**Q: Can't see the new buttons?**
- A: Make sure you're logged in as super admin (frankmk2025@gmail.com)
- Check that you have `is_staff` and `is_superuser` permissions

**Q: Created user but they can't login?**
- A: Wait a few seconds for Firebase to sync
- Check email is spelled correctly
- Try password reset if issues persist
- Verify user is not disabled

**Q: Approved demo but don't see institution?**
- A: Go to **Institutions** page to see all institutions
- Refresh the page to reload data
- Check audit logs for confirmation

**Q: Reset password email not received?**
- A: Check spam/junk folder
- Verify email address is correct
- Note: Firebase is sending the email, not your app

---

## Data Flow Diagrams

### Demo Approval Flow
```
DemoRequest (Pending)
    ↓
Admin clicks "Approve"
    ↓
Select admin user to assign
    ↓
Add notes (optional)
    ↓
Click "Approve"
    ↓
✅ Institution created
✅ Admin assigned
✅ Audit log entry
✅ Demo status → Approved
```

### User Creation Flow
```
Click "Create New User"
    ↓
Fill form (Name, Email, Password, Role)
    ↓
Click "Create User"
    ↓
✅ User created in Firebase
✅ User created in Django
✅ User profile created
✅ Audit log entry
✅ Can login immediately
```

### Password Reset Flow
```
Click "Forgot Password?"
    ↓
Enter email
    ↓
Receive reset code email
    ↓
Enter code + new password
    ↓
Click "Reset Password"
    ↓
✅ Password updated
✅ Can login with new password
```

---

## Feature Comparison

| Feature | Before | After |
|---------|--------|-------|
| Approve Demos | ❌ Manual process | ✅ Automatic Institution creation |
| Create Users | ❌ Not available | ✅ Self-service admin panel |
| Assign Admins | ❌ Manual | ✅ During approval |
| Password Reset | ❌ Manual email | ✅ Firebase automated |
| Audit Logging | ✅ Existing | ✅ Enhanced with new actions |

---

## System Requirements

✅ Features work with:
- Modern browsers (Chrome, Firefox, Safari, Edge)
- Mobile responsive design
- All user roles (Admin, Staff, Viewer)
- All institution types

✅ User must be:
- Logged in as super admin (for approvals & user creation)
- Have valid email (for password reset)
- Know their password (or have reset code)

---

## Support & Questions

For issues with:
- **Demo approval:** Check if admin user is selected
- **User creation:** Ensure password is 6+ characters
- **Password reset:** Check email inbox and spam folder
- **General:** Check audit logs for activity record

---

**Last Updated:** [Date]
**Status:** ✅ Live and Ready
**Version:** 1.0
