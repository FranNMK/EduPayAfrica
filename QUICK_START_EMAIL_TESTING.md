# Quick Start: Testing Automated Emails

## 5-Minute Local Test

### Step 1: Start the Server
```bash
cd C:\Users\mc\Desktop\Edu\EduPayAfrica
python manage.py runserver
```

### Step 2: Open Website
Go to: http://localhost:8000

### Step 3: Test Demo Email
1. Click on "BOOK A DEMO" button
2. Fill in the demo form:
   - Full Name: John Doe
   - Email: john@example.com
   - Phone: +254 700 000 000
   - Job Title: Principal
   - Institution Name: Test School
   - Institution Type: Secondary School
   - Student Count: 500
   - Country: Kenya
   - Challenge: Budget Management
   - Preferred Time: Morning
3. Check "I agree to Privacy Policy..."
4. Click "Submit"
5. **Watch the terminal window** - you'll see the confirmation email printed

Expected output in terminal:
```
Message object:
    from: noreply@edupayafrica.com
    to: john@example.com
    subject: Welcome to EduPay Africa - Demo Request Confirmed
    
    Hello John Doe,

    Thank you for requesting a demo of EduPay Africa...
```

### Step 4: Test Contact Email
1. Click on "CONTACT US" button
2. Fill in the contact form:
   - Full Name: Jane Smith
   - Email: jane@example.com
   - Phone: +254 700 111 111
   - Subject: Integration Query
   - Message: How to integrate with our system?
3. Check "I agree to Privacy Policy..."
4. Click "Submit"
5. **Watch the terminal window** - you'll see the contact confirmation email printed

Expected output in terminal:
```
Message object:
    from: noreply@edupayafrica.com
    to: jane@example.com
    subject: We received your message - EduPay Africa
    
    Hello Jane Smith,

    Thank you for contacting EduPay Africa...
```

## Automated Test

### Option 1: Using Test Script
```bash
cd C:\Users\mc\Desktop\Edu
python test_email.py
```

This will:
- Test direct send_mail
- Test demo email function
- Test contact email function
- Print all emails to console

### Option 2: Django Shell
```bash
cd C:\Users\mc\Desktop\Edu\EduPayAfrica
python manage.py shell
```

Then run:
```python
from leads.views import send_confirmation_email
from core.views import send_contact_confirmation_email

# Test demo email
send_confirmation_email("Test User", "test@example.com")

# Test contact email
send_contact_confirmation_email("Contact User", "contact@example.com")

# Exit shell
exit()
```

## Verification Checklist

✓ **Emails printing to console?** → Development mode working ✅
✓ **Email contains correct info?** → Content templates correct ✅
✓ **Forms still submit after email?** → Error handling working ✅
✓ **Success message displayed?** → User feedback working ✅

## What's Working

### Development (DEBUG=True)
- ✅ Console Backend active
- ✅ All emails printed to terminal
- ✅ No SMTP server needed
- ✅ Perfect for testing

### When You Deploy (DEBUG=False)
- Set environment variables with your email provider
- Emails will be sent via SMTP instead of printing to console
- No code changes needed!

## Common Questions

### Q: Why are emails printing instead of sending?
**A:** Because DEBUG=True in settings.py (development mode). This is intentional - safer and faster for testing.

### Q: How do I make emails actually send?
**A:** Set environment variables with your email provider (Gmail, SendGrid, etc.) when deploying to production.

### Q: Will existing forms still work?
**A:** Yes! Email is optional - if it fails, the form submission still succeeds.

### Q: Can I test real email sending?
**A:** Yes, create `.env` file with Gmail credentials:
```
DEBUG=False
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
```

Then restart server. See EMAIL_PROVIDER_CONFIG.md for setup.

## Troubleshooting

### Emails Not Printing in Terminal
1. Check DEBUG=True in settings.py
2. Check EMAIL_BACKEND in settings.py is 'django.core.mail.backends.console.EmailBackend'
3. Restart server
4. Check terminal is not scrolled up (emails appear inline)

### Form Not Submitting
1. Check browser console for JavaScript errors (F12)
2. Check Django terminal for Python errors
3. Make sure all required form fields are filled
4. Make sure privacy checkbox is checked

### Different Email Than Expected
1. Check you submitted the form (not just refreshed)
2. Check the form validation passed
3. Look for "Thank you" success message on page

## Next Steps After Testing

1. ✅ Email functionality working locally? 
   → Great! Move to deployment

2. Set up email provider (Gmail recommended):
   - See EMAIL_PROVIDER_CONFIG.md

3. Configure environment variables on production server

4. Test again in production

5. Monitor email delivery in production

## Production Deployment Checklist

- [ ] Environment variables configured on server
- [ ] DEBUG=False in production settings
- [ ] TEST: Send a demo request → check inbox
- [ ] TEST: Send a contact inquiry → check inbox
- [ ] Monitor email delivery for first week
- [ ] Set up email bounce handling (optional)
- [ ] Configure domain SPF/DKIM (optional, for better deliverability)

That's it! 🎉
