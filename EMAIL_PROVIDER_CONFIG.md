# Email Provider Configuration Guide

Quick reference for configuring different email providers for production.

## Gmail

### Setup:
1. Go to https://myaccount.google.com/apppasswords
2. Select Mail → Select your device type
3. Copy the 16-character App Password

### .env Configuration:
```
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=xxxx xxxx xxxx xxxx
DEFAULT_FROM_EMAIL=noreply@edupayafrica.com
```

## SendGrid

### Setup:
1. Create account at https://sendgrid.com
2. Generate API Key from Settings → API Keys
3. Use 'apikey' as username and the key as password

### .env Configuration:
```
EMAIL_HOST=smtp.sendgrid.net
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=apikey
EMAIL_HOST_PASSWORD=SG.xxxxxxxxxxxxxxxxxxxxx
DEFAULT_FROM_EMAIL=noreply@edupayafrica.com
```

## Mailgun

### Setup:
1. Create account at https://www.mailgun.com
2. Verify your domain
3. Get SMTP credentials from Domain Settings

### .env Configuration:
```
EMAIL_HOST=smtp.mailgun.org
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=postmaster@your-domain.mailgun.org
EMAIL_HOST_PASSWORD=your-mailgun-password
DEFAULT_FROM_EMAIL=noreply@edupayafrica.com
```

## AWS SES (Simple Email Service)

### Setup:
1. Create AWS account and go to SES console
2. Verify sender email
3. Create SMTP credentials (not same as AWS key)
4. Request production access (if in sandbox)

### .env Configuration:
```
EMAIL_HOST=email-smtp.us-east-1.amazonaws.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-ses-smtp-username
EMAIL_HOST_PASSWORD=your-ses-smtp-password
DEFAULT_FROM_EMAIL=verified-email@yourdomain.com
```

## Office 365

### Setup:
1. Use your Office 365 email account
2. Enable SMTP authentication in your account

### .env Configuration:
```
EMAIL_HOST=smtp.office365.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@company.com
EMAIL_HOST_PASSWORD=your-office365-password
DEFAULT_FROM_EMAIL=noreply@company.com
```

## Google Workspace

### Setup:
Similar to Gmail but with company domain

### .env Configuration:
```
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=admin@company.com
EMAIL_HOST_PASSWORD=xxxx xxxx xxxx xxxx
DEFAULT_FROM_EMAIL=noreply@company.com
```

## Recommended for Africa/Kenya

### Best Options:
1. **Gmail/Google Workspace** - Most reliable, affordable
2. **SendGrid** - Excellent support, good for high volume
3. **Mailgun** - Good documentation, developer-friendly

### Local Providers:
- **Liquid Intelligent Technologies** (formerly Africell)
- **Safaricom Business** (M-Pesa integration possible)
- **Jamii Forum** (local email solution)

## Testing Your Configuration

After setting environment variables:

```bash
python manage.py shell
```

Then:

```python
from django.core.mail import send_mail
from django.conf import settings

# Test send
send_mail(
    'Test Subject',
    'This is a test email',
    settings.DEFAULT_FROM_EMAIL,
    ['your-email@example.com'],
    fail_silently=False,
)

# Should print "Message sent" or similar
```

## Common Issues

### "Authentication failed"
- Check EMAIL_HOST_USER and EMAIL_HOST_PASSWORD are correct
- For Gmail: Use App Password, not account password
- Ensure 2-Step Verification is enabled (Gmail)

### "Connection refused"
- Check EMAIL_HOST and EMAIL_PORT are correct
- Verify firewall allows outbound port 587
- Check if provider requires different port (usually 587 or 465)

### "Email marked as spam"
- Configure SPF and DKIM records for your domain
- Use domain in FROM address (not generic)
- Reduce email frequency if sending many

### "Still not working?"
- Check production environment variables are set: `echo $EMAIL_HOST`
- Verify DEBUG=False in settings.py for production
- Check server logs: `tail -f /var/log/django.log`

## Environment Setup (Production Server)

### Heroku:
```bash
heroku config:set EMAIL_HOST=smtp.gmail.com
heroku config:set EMAIL_PORT=587
heroku config:set EMAIL_USE_TLS=True
heroku config:set EMAIL_HOST_USER=your-email@gmail.com
heroku config:set EMAIL_HOST_PASSWORD=your-app-password
```

### Railway / Render:
- Set variables in dashboard → Environment
- No need for `.env` file, they read from dashboard

### AWS / DigitalOcean:
- Create `.env` file on server
- Keep out of git repo
- Load in settings.py with python-dotenv

## Django Admin Email Notifications

Once configured, Django admin emails also work:
- New user registrations
- Password resets
- Admin alerts

No additional setup needed!
