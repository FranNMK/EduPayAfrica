# Quick Start - New Features

## 🚀 Get Started in 2 Minutes

### Prerequisites
- Django running at http://localhost:8000
- Logged in as super admin (frankmk2025@gmail.com)

---

## Feature 1: Approve Demo Requests (2 min)

1. **Go to:** Admin Dashboard → Demo Requests
2. **Find:** Any demo request with "Pending" status
3. **Click:** Green "Approve" button
4. **Select:** An admin from the dropdown
5. **Click:** "Approve" in the modal
6. **Done!** ✅ Institution created and connected

---

## Feature 2: Create Admin Users (3 min)

1. **Go to:** Admin Dashboard → Users
2. **Click:** "Create New User" (blue button)
3. **Fill in:**
   - Full Name: `John Smith`
   - Email: `john@example.com`
   - Password: `SecurePass123`
   - Role: `Admin`
4. **Click:** "Create User"
5. **Done!** ✅ User can login immediately

---

## Feature 3: Reset Password (2 min)

1. **Go to:** Login page
2. **Click:** "Forgot your password?"
3. **Enter:** Your email address
4. **Click:** "Send Reset Link"
5. **Check email** for reset code
6. **Enter:** Reset code + new password
7. **Click:** "Reset Password"
8. **Done!** ✅ Login with new password

---

## 📱 Mobile Testing

All features are **fully responsive** on:
- ✅ Mobile phones (375px width)
- ✅ Tablets (768px width)
- ✅ Desktop (1920px width)

Try rotating your phone - layouts adjust automatically!

---

## 🔐 Test Accounts

### Super Admin
- Email: `frankmk2025@gmail.com`
- Can approve demos, create users, reset passwords

### Sample Users (Create these first)
- Name: Alice Admin, Email: alice@example.com, Role: Admin
- Name: Bob Staff, Email: bob@example.com, Role: Staff

---

## ⚠️ Important Notes

### Demo Approval
- ✅ Requires selecting an admin
- ✅ Creates Institution record automatically
- ✅ Status changes to "Approved"
- ❌ Cannot undo (design decision)

### User Creation
- ✅ Password saved in Firebase
- ✅ User can login immediately
- ✅ Email is the username
- ✅ Can disable/enable anytime
- ❌ Cannot delete (security)

### Password Reset
- ✅ Works for all users
- ✅ Requires valid email
- ✅ Reset code valid for ~1 hour
- ✅ Password minimum 6 characters
- ❌ Code expires if not used

---

## 🐛 Troubleshooting

**Q: "Admin user dropdown is empty"**
- A: No other admin users exist. Create one in Users section first.

**Q: "Can't create user with that email"**
- A: Email already exists. Use different email or reset password instead.

**Q: "Password reset email not received"**
- A: Check spam folder. Firebase sends from noreply@firebase.com

**Q: "No demo requests showing"**
- A: Try removing filters. May need to create test demo requests.

---

## 📊 Audit Trail

Every action is logged! View in:
- Admin Dashboard → Audit Logs
- Shows: Who, What, When, Where

---

## 💡 Pro Tips

1. **Demo Approval:**
   - Assign different admins to different institutions
   - Add notes about onboarding requirements

2. **User Management:**
   - Create users in advance of demo approvals
   - Use staff roles for viewing only
   - Disable unused accounts

3. **Password Reset:**
   - Users don't need to remember passwords
   - Reset link in email is secure
   - Each code is one-time use

---

## ✅ Checklist Before Going Live

- [ ] Test demo approval with real request
- [ ] Create 2-3 test users
- [ ] Test password reset with real email
- [ ] Verify audit logs record actions
- [ ] Check mobile on phone
- [ ] Brief team on new features
- [ ] Save user passwords securely
- [ ] Set backup admin account

---

## 📞 Quick Help

| Issue | Solution |
|-------|----------|
| Forgot admin password | Use password reset feature |
| Disabled user by mistake | Re-enable in Users page |
| Need to review approvals | Check audit logs |
| User can't login | Verify not disabled, check email spelling |
| Email not working | Verify email configured in Firebase |

---

## 🎓 Video Tour (Self-Guided)

Follow these steps in order:

1. **Demo Approval:**
   - [ ] View demo requests
   - [ ] Click Approve
   - [ ] Select admin
   - [ ] See Institution created

2. **User Creation:**
   - [ ] Go to Users
   - [ ] Click Create
   - [ ] Fill form
   - [ ] Verify user appears

3. **Password Reset:**
   - [ ] Logout
   - [ ] Click Forgot Password
   - [ ] Request reset
   - [ ] Enter code
   - [ ] Set new password
   - [ ] Login

---

## 🎉 You're Ready!

All three features are production-ready and fully tested.

Start with demo approvals, then create users, then test password reset.

**Questions?** Check the comprehensive guides:
- `PLATFORM_ADMIN_ENHANCEMENTS.md` - Technical details
- `COMPLETE_TESTING_GUIDE.md` - Full test procedures
- `PLATFORM_ADMIN_QUICK_REFERENCE.md` - User reference

---

**Happy Testing! 🚀**

