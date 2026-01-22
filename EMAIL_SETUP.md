# Email Configuration Setup

## Overview
The EduPay Africa application now has automated confirmation emails for:
1. **Demo Requests** - Sent via `leads/views.py:send_confirmation_email()`
2. **Contact Inquiries** - Sent via `core/views.py:send_contact_confirmation_email()`

## Development Environment

### Current Configuration
In **development mode** (`DEBUG = True`):
- **Email Backend:** Console Backend
- **Behavior:** All emails are printed to the console/terminal instead of being sent
- **No Setup Required:** Just run the server and check terminal output

### Testing Locally
1. Start the development server:
   ```bash
   python manage.py runserver
   ```

2. Submit a demo booking or contact form on the website

3. Check the terminal/console output - you'll see the full email content printed there

Example output:
```
[Email] Message object:
    from: noreply@edupayafrica.com
    to: user@example.com
    subject: Welcome to EduPay Africa - Demo Request Confirmed
    Hello John Doe,

Thank you for requesting a demo...
```

## Production Configuration

### Using Gmail
1. **Enable 2-Step Verification** on your Gmail account
2. **Generate App Password** (not your regular password):
   - Go to https://myaccount.google.com/apppasswords
   - Select Mail and your device type
   - Copy the generated 16-character password

3. **Add Environment Variables** (create `.env` file in project root):
   ```
   EMAIL_HOST=smtp.gmail.com
   EMAIL_PORT=587
   EMAIL_USE_TLS=True
   EMAIL_HOST_USER=your-email@gmail.com
   EMAIL_HOST_PASSWORD=your-app-password
   DEFAULT_FROM_EMAIL=noreply@edupayafrica.com
   ```

4. **Update settings.py** to load from `.env`:
   ```bash
   pip install python-dotenv
   ```

5. **Modify `settings.py`** (at the top):
   ```python
   from dotenv import load_dotenv
   load_dotenv()
   ```

### Using Other Email Providers
- **SendGrid:** EMAIL_HOST = smtp.sendgrid.net, EMAIL_PORT = 587
- **Mailgun:** EMAIL_HOST = smtp.mailgun.org, EMAIL_PORT = 587
- **AWS SES:** EMAIL_HOST = email-smtp.{region}.amazonaws.com, EMAIL_PORT = 587

Contact the provider for specific credentials.

## Email Templates

### Demo Request Confirmation
- **Sent to:** Requestor's email
- **Trigger:** After successful demo form submission
- **Content:** Welcome message + 24-hour follow-up expectation

### Contact Inquiry Confirmation
- **Sent to:** Inquiry sender's email
- **Trigger:** After successful contact form submission
- **Content:** Acknowledgment + 24-48 hour response expectation

## Code Implementation

### Demo Request Email (leads/views.py)
```python
send_confirmation_email(full_name, email)
```

### Contact Inquiry Email (core/views.py)
```python
send_contact_confirmation_email(full_name, email)
```

Both functions use Django's `send_mail()` with:
- Error handling (won't break form submission if email fails)
- Try-except blocks to log failures
- `fail_silently=False` to catch errors

## Troubleshooting

### Email Not Sending in Development
- Verify `DEBUG = True` in settings.py
- Check terminal/console output for "Email" message
- Ensure `EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'`

### Email Not Sending in Production
- Verify environment variables are set correctly
- Check server logs for SMTP connection errors
- Verify firewall/network allows port 587 (or your configured port)
- Ensure credentials are correct
- Check if Gmail 2-Step verification is required (use App Password, not regular password)

### Test Email Sending
Run this command to test:
```bash
python manage.py shell
```

Then:
```python
from django.core.mail import send_mail
from django.conf import settings

send_mail(
    'Test Subject',
    'This is a test email',
    settings.DEFAULT_FROM_EMAIL,
    ['recipient@example.com'],
    fail_silently=False,
)
```

## Security Notes

1. **Never commit `.env` file** - Add to `.gitignore`
2. **Use App Passwords** for Gmail instead of account password
3. **Rotate credentials regularly** in production
4. **Monitor email delivery** for failures
5. **Use TLS encryption** (EMAIL_USE_TLS = True)

## Next Steps

1. Test locally with development backend
2. Configure production email provider when deploying
3. Set up email logging to monitor delivery
4. Add email templates as HTML for better formatting (optional)
5. Implement email resend functionality if needed
