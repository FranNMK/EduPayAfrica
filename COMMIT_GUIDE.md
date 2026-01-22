# 🚀 Quick Commit Guide - Secure Firebase Fix

## ✅ What to Do Right Now

### Step 1: Verify .env is NOT Tracked
```bash
cd C:\Users\mc\Desktop\Edu\EduPayAfrica
git status
```

**Expected:** `.env` should NOT appear in the list of files
**If it does:** Run `git reset HEAD .env` to unstage it

### Step 2: Stage Safe Files Only
```bash
# Stage the security fixes
git add .gitignore
git add .env.example
git add EduPayAfrica/settings.py
git add EduPayAfrica/context_processors.py
git add static/js/firebase-init.js
git add templates/base.html

# Check what you're about to commit
git status
```

**Verify:** `.env` is NOT in the "Changes to be committed" list

### Step 3: Commit the Changes
```bash
git commit -m "Security: Move Firebase secrets to .env file

- Add .env support using python-dotenv
- Create context processor for Firebase config
- Update firebase-init.js to use config from backend
- Add .gitignore to protect sensitive files
- Add .env.example as template

Fixes: GitHub security alert for exposed API keys"
```

### Step 4: Before Pushing - CRITICAL!

**⚠️ DO THIS FIRST:** Rotate your Firebase keys!

1. Go to https://console.firebase.google.com/
2. Select project: edupay-africa
3. Project Settings → General
4. Under "Your apps" → Web app section
5. Click "Delete app" or create a new web app with new keys
6. Update your `.env` file with the NEW keys
7. Test locally: `python manage.py runserver`

### Step 5: Push to GitHub
```bash
git push origin main
```

---

## 🔐 Critical Security Checks

Before pushing, run these commands:

### Check 1: .env is NOT staged
```bash
git diff --cached --name-only
```
**Should NOT see:** `.env`

### Check 2: .env is in .gitignore
```bash
cat .gitignore | grep ".env"
```
**Should see:** `.env` listed

### Check 3: Firebase config removed from firebase-init.js
```bash
grep -i "AIzaSyAzt6kYUBdhL7VwZ4SfACISlY71uZN_Nag" static/js/firebase-init.js
```
**Should see:** No results (key not found)

### Check 4: .env exists locally
```bash
ls .env
```
**Should see:** `.env` file listed

---

## 🧪 Test Before Pushing

### Test 1: Server Starts
```bash
python manage.py runserver
```
**Expected:** Server starts without errors

### Test 2: Firebase Loads
1. Open http://localhost:8000
2. Open browser console (F12)
3. **Expected:** "Firebase initialized successfully"

### Test 3: .env Values Load
```bash
python manage.py shell
```
```python
from django.conf import settings
print(settings.FIREBASE_CONFIG['apiKey'])
# Should print your API key from .env
exit()
```

---

## ❌ What NOT to Commit

**Never commit these:**
- `.env` (contains secrets)
- `db.sqlite3` (database file)
- `__pycache__/` (Python cache)
- `*.pyc` (compiled Python)
- `.vscode/` or `.idea/` (editor configs)

**All blocked by .gitignore** ✅

---

## 🔄 If You Accidentally Committed .env

If you see `.env` in `git status` or in your commit:

```bash
# Remove from staging
git reset HEAD .env

# Remove from last commit (if already committed)
git reset --soft HEAD~1
git reset HEAD .env
git commit -m "Security: Move Firebase secrets to .env"

# If already pushed - contact me immediately!
```

---

## 📝 Commit Checklist

Before `git push`:

- [ ] `.env` file created with Firebase keys
- [ ] `.env.example` created (template only)
- [ ] `.gitignore` created and includes `.env`
- [ ] `git status` does NOT show `.env`
- [ ] Firebase keys rotated in Firebase Console
- [ ] `.env` updated with NEW keys
- [ ] `python manage.py check` passes
- [ ] Server starts: `python manage.py runserver`
- [ ] Browser console shows "Firebase initialized successfully"
- [ ] No Firebase API key in `static/js/firebase-init.js`

---

## 🎯 After Pushing

### Monitor GitHub Alert
- GitHub security alert should clear within 24 hours
- Check: https://github.com/FranNMK/EduPayAfrica/security

### If Alert Persists
1. Ensure old keys are rotated (invalidated)
2. Verify no secrets in current files
3. May need to remove from git history (see SECURITY_FIX_FIREBASE.md)

---

## 🆘 Emergency: If Something Goes Wrong

### Server Won't Start
1. Check `.env` file exists in same directory as `manage.py`
2. Check all values in `.env` have no quotes
3. Run: `python -m pip install python-dotenv`

### Firebase Not Loading
1. Open browser console (F12)
2. Check for error messages
3. Verify `.env` values are correct
4. Check `window.firebaseConfig` in console

### .env Got Committed
1. Run: `git reset HEAD .env`
2. Run: `git commit --amend` to fix last commit
3. **Do NOT push** until `.env` is removed

---

## ✅ Success Indicators

You'll know everything worked when:
- ✅ `git push` completes successfully
- ✅ GitHub shows `.env` is NOT in repository
- ✅ GitHub shows `.gitignore` and `.env.example` ARE in repository
- ✅ `static/js/firebase-init.js` has no API keys
- ✅ Server starts locally without errors
- ✅ Firebase works on website
- ✅ GitHub security alert clears (24h)

---

**Ready to commit?** Follow Step 1-5 above in order!

**Questions?** See SECURITY_FIX_FIREBASE.md for detailed explanation
