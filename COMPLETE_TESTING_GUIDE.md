# Complete Testing Guide - Platform Admin Enhancements

## Pre-Testing Setup

### Required Environment
- Python 3.8+ with Django 6.0
- Firebase project configured with credentials
- Environment variables set (.env file)
- Virtual environment activated
- Database migrations applied

### Required Packages
```bash
pip install firebase-admin requests python-dotenv
```

### Environment Variables (.env)
```
FIREBASE_API_KEY=your_firebase_web_api_key
FIREBASE_CREDENTIALS_PATH=/path/to/firebase-adminsdk-*.json
FIREBASE_PROJECT_ID=your_project_id
SUPER_ADMIN_EMAIL=frankmk2025@gmail.com
```

---

## Test Scenarios

### SCENARIO 1: Demo Request Approval Workflow

**Setup:**
- Login as super admin
- Have at least 2 demo requests in pending status
- Have at least 1 other admin user created

**Test 1.1: Basic Approval**
```
1. Navigate to Admin Dashboard
2. Click "Demo Requests"
3. Verify page loads with demo request table
4. Find a demo request with "pending" status
5. Click the green "Approve" button
6. Modal dialog should appear with:
   ✓ Institution name displayed
   ✓ Contact details shown
   ✓ Admin user dropdown (not empty)
   ✓ Onboarding notes textarea
7. Select an admin from dropdown
8. (Optional) Add onboarding notes
9. Click "Approve" button
10. Modal should close
11. Page should show success message
12. Demo request status should change to "approved"
```

**Expected Results:**
- ✅ Institution record created in database
- ✅ Institution linked to selected admin
- ✅ AuditLog entry recorded
- ✅ InstitutionStatusLog entry created
- ✅ Success message displayed

**Test 1.2: Approval with Notes**
```
1. Click Approve on another demo request
2. Select an admin
3. Enter onboarding notes: "Schedule onboarding for Week 1"
4. Click Approve
5. Check Institution record created with notes
```

**Expected Results:**
- ✅ Notes saved in onboarding_notes field
- ✅ Visible in institutions list

**Test 1.3: Rejection Workflow**
```
1. Find a demo request with "pending" status
2. Click red "Reject" button
3. Modal should appear with:
   ✓ Institution name displayed
   ✓ Reason textarea
4. Enter rejection reason: "Not meeting requirements"
5. Click "Reject" button
6. Modal closes
7. Success message shown
8. Demo status changes to "rejected"
```

**Expected Results:**
- ✅ DemoRequest.status = "rejected"
- ✅ AuditLog entry with rejection reason
- ✅ No Institution record created

**Test 1.4: Filtering and Sorting**
```
1. Apply filters:
   - Institution type: "University"
   - Status: "pending"
   - Date range: Last 30 days
2. Verify filtered results
3. Clear filters
4. Verify all requests show again
```

**Expected Results:**
- ✅ Filters applied correctly
- ✅ Results update after filtering

**Test 1.5: Already Approved Request**
```
1. Find an already-approved demo request
2. Verify buttons are NOT shown
3. Verify "No actions available" message shown
```

**Expected Results:**
- ✅ Approve/Reject buttons hidden
- ✅ Read-only view maintained

---

### SCENARIO 2: User Management and Creation

**Setup:**
- Login as super admin
- Access Users page
- Have a list of existing users visible

**Test 2.1: Create New User**
```
1. Navigate to Admin Dashboard → Users
2. Click blue "Create New User" button
3. Modal form should appear with fields:
   ✓ Full Name (required)
   ✓ Email (required)
   ✓ Password (required)
   ✓ Role dropdown
4. Fill form:
   - Full Name: "Alice Johnson"
   - Email: "alice.johnson@example.com"
   - Password: "SecurePass123"
   - Role: "Admin"
5. Click "Create User" button
6. Modal closes
7. Success message shows: "User alice.johnson@example.com created successfully"
8. New user appears in table
9. Status shows "Active"
```

**Expected Results:**
- ✅ Firebase user created
- ✅ Django user created
- ✅ PlatformUserProfile created
- ✅ AuditLog entry recorded
- ✅ User visible in list immediately
- ✅ User can login with credentials

**Test 2.2: Password Validation**
```
1. Try creating user with password < 6 characters
2. Enter password: "short"
3. Click Create User
4. Error message: "Password must be at least 6 characters"
5. Modal stays open
```

**Expected Results:**
- ✅ Client-side validation blocks submission
- ✅ Server-side validation also checks

**Test 2.3: Email Validation**
```
1. Try creating user with invalid email
2. Enter email: "notanemail"
3. Click Create User
4. Error message: "Enter a valid email address"
```

**Expected Results:**
- ✅ Form validation prevents submission

**Test 2.4: Duplicate Email**
```
1. Try creating user with existing email
2. Enter email of already-created user
3. Click Create User
4. Error: "A user with this email already exists"
```

**Expected Results:**
- ✅ Duplicate check working
- ✅ Firebase handles conflict

**Test 2.5: Disable User Account**
```
1. Find an active user in list
2. Click "Disable" button
3. User status changes to "Disabled"
4. AuditLog entry shows disable action
5. Try logging in with disabled user
6. Login should fail with "Account disabled"
```

**Expected Results:**
- ✅ is_active set to False
- ✅ User cannot login
- ✅ AuditLog records action

**Test 2.6: Re-enable User Account**
```
1. Find a disabled user
2. Click "Enable" button
3. User status changes to "Active"
4. User can login again
```

**Expected Results:**
- ✅ is_active set to True
- ✅ User can login
- ✅ AuditLog records action

**Test 2.7: Different Roles**
```
1. Create user with Role = "Staff"
2. Create user with Role = "Viewer"
3. Verify roles displayed correctly in list
```

**Expected Results:**
- ✅ Roles saved and displayed
- ✅ Role badges shown in table

---

### SCENARIO 3: Password Reset Functionality

**Setup:**
- Logout from admin account
- Be on login page
- Have a valid email account to receive reset emails

**Test 3.1: Request Password Reset**
```
1. On login page, click "Forgot your password?"
2. Should redirect to /password-reset/
3. Form with:
   ✓ Email input field
   ✓ "Send Reset Link" button
   ✓ "Back to Login" link
4. Enter test user email: "user@example.com"
5. Click "Send Reset Link"
6. Success message: "Password reset link sent to user@example.com"
7. Should redirect to login page
```

**Expected Results:**
- ✅ Firebase API called
- ✅ Email sent to provided address
- ✅ Reset code included in email
- ✅ User redirected to login

**Test 3.2: Invalid Email (Reset Request)**
```
1. On password reset form
2. Enter non-existent email: "fake@example.com"
3. Click "Send Reset Link"
4. Firebase returns error
5. Error message displayed
```

**Expected Results:**
- ✅ Graceful error handling
- ✅ User informed of error

**Test 3.3: Confirm Password Reset**
```
1. After receiving reset email
2. Click reset link in email
3. Should go to /password-reset-confirm/
4. Form with fields:
   ✓ Reset Code input
   ✓ New Password input
   ✓ Confirm Password input
5. Enter:
   - Reset Code: [from email]
   - New Password: "NewPassword123"
   - Confirm: "NewPassword123"
6. Click "Reset Password"
7. Success: "Password reset successfully"
8. Redirect to login
9. Login with new password
```

**Expected Results:**
- ✅ Password changed in Firebase
- ✅ User can login with new password
- ✅ Old password no longer works

**Test 3.4: Password Mismatch**
```
1. On password reset confirm form
2. Enter:
   - New Password: "Password123"
   - Confirm: "Password456"
3. Click "Reset Password"
4. Error: "Passwords do not match"
```

**Expected Results:**
- ✅ Client validation prevents submission
- ✅ Server validation also checks

**Test 3.5: Invalid Reset Code**
```
1. On password reset confirm
2. Enter invalid/expired code
3. Click "Reset Password"
4. Firebase error: "Invalid reset code"
5. Error message shown
```

**Expected Results:**
- ✅ Error handled gracefully
- ✅ User informed to request new link

**Test 3.6: Password Visibility Toggle**
```
1. On reset form, password field
2. Click eye icon
3. Password should show as plain text
4. Click eye icon again
5. Password should be hidden
6. Same for Confirm Password field
```

**Expected Results:**
- ✅ Password visibility toggled
- ✅ Both fields have toggle buttons
- ✅ Icons change (eye ↔ eye-slash)

---

### SCENARIO 4: Integration Tests

**Test 4.1: End-to-End Demo Approval**
```
1. New demo request submitted via web form
2. Super admin approves demo
3. Institution created
4. Newly created admin can login
5. Admin can see their institution dashboard
```

**Test 4.2: Full User Workflow**
```
1. Create new admin user
2. User receives credentials via email (if setup)
3. User logs in with provided credentials
4. User can access dashboard
5. User can view their institutions
6. User resets password (forgot password)
7. User logs back in with new password
```

**Test 4.3: Audit Trail Verification**
```
1. Create user → Check audit log
2. Approve demo → Check audit log
3. Disable user → Check audit log
4. Reset password → Check audit log (if tracked)
5. Verify all entries have:
   ✓ Timestamp
   ✓ Actor (admin user)
   ✓ Action description
   ✓ Entity type and ID
```

---

## Browser Testing

Test in multiple browsers:
- ✅ Google Chrome (latest)
- ✅ Firefox (latest)
- ✅ Safari (if on Mac)
- ✅ Microsoft Edge (latest)
- ✅ Mobile browsers (iOS Safari, Chrome Mobile)

### Responsive Testing
- ✅ Desktop (1920x1080)
- ✅ Tablet (768x1024)
- ✅ Mobile (375x667)

Verify modals, forms, and tables display correctly on all sizes.

---

## Performance Testing

**Test Response Times:**
- Demo approval submission: < 2 seconds
- User creation: < 3 seconds
- Password reset request: < 2 seconds
- Page loads: < 1 second

**Load Testing (Optional):**
- Approve 100 demos rapidly
- Create 50 users in batch
- Multiple simultaneous password resets

---

## Security Testing

**Test 4.1: Authorization Checks**
```
1. Logout as super admin
2. Try accessing /platform-admin/demo-requests/
3. Should redirect to login
4. Try accessing /platform-admin/users/
5. Should redirect to login
```

**Test 4.2: CSRF Protection**
```
1. Submit forms and verify CSRF token present
2. Try submitting without token
3. Request should fail
```

**Test 4.3: SQL Injection**
```
1. Try entering SQL in form fields
2. Should be escaped/safe
3. No database errors
```

**Test 4.4: Password Security**
```
1. Verify passwords not logged
2. Verify passwords not in error messages
3. Verify passwords encrypted in Firebase
```

---

## Data Validation Testing

**Test 5.1: Form Validation**
- ✅ Email format validation
- ✅ Password length validation
- ✅ Required field validation
- ✅ Custom validations

**Test 5.2: Data Integrity**
- ✅ No orphaned records
- ✅ All relationships maintained
- ✅ Audit logs complete

---

## Error Handling Testing

| Error Scenario | Expected Behavior |
|---|---|
| Firebase credentials invalid | Clear error message |
| Network timeout | Retry or timeout message |
| Database error | User-friendly error |
| Invalid input | Form validation error |
| Duplicate email | Specific error message |
| Expired reset code | Request new code message |

---

## Rollback Testing

**Test that rollback works:**
```bash
git checkout [files]
python manage.py runserver
# Verify features no longer work
```

---

## Sign-Off Checklist

- [ ] All unit tests pass
- [ ] All integration tests pass
- [ ] Demo approval creates institution
- [ ] User creation works
- [ ] Password reset works
- [ ] Audit logs complete
- [ ] UI responsive on mobile
- [ ] No SQL injection vulnerabilities
- [ ] No unauthorized access possible
- [ ] Error messages user-friendly
- [ ] Performance acceptable
- [ ] Documentation complete
- [ ] Team trained on features

---

## Test Data

Use this sample data for testing:

**Sample Demo Requests:**
- School: "Thomas Education Academy"
- Contact: "Dr. Michael Brown"
- Email: "michael.brown@thomas-edu.com"
- Phone: "+1-555-0123"

**Sample Users to Create:**
- Name: "Sarah Admin", Email: "sarah@company.com", Role: "Admin"
- Name: "John Staff", Email: "john@company.com", Role: "Staff"
- Name: "Lisa Viewer", Email: "lisa@company.com", Role: "Viewer"

---

## Known Limitations

- Firebase email not configured for local development (need SMTP setup)
- Password reset links only work if email is received
- Bulk operations not optimized for large datasets
- No automatic retry on network failures

---

## Support Contact

For issues during testing:
- Check browser console for JavaScript errors
- Check Django console for backend errors
- Check `/platform-admin/audit-logs/` for action history
- Review error messages carefully

---

**Test Plan Version:** 1.0  
**Created:** [Date]  
**Status:** Ready for Testing  
**Approved By:** [Name]
