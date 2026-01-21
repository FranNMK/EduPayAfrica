#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'EduPayAfrica.settings')
django.setup()

from django.test import Client

client = Client()

payload = {
    'full_name': 'Test User',
    'email': 'test@example.com',
    'phone': '+254700000000',
    'job_title': 'ict_officer',
    'institution_name': 'Test Institution',
    'institution_type': 'college',
    'student_count': '100_500',
    'country': 'Kenya',
    'challenge': 'tracking',
    'message': 'Looking forward to the demo',
    'preferred_time': 'morning',
    'include_team': 'on',
    'agree': 'on',
}

response = client.post('/demo/', data=payload, follow=False)
print('Status:', response.status_code)
print('Location:', response.get('Location'))

# Follow redirect if any
if response.status_code in (301, 302, 303, 307):
    resp2 = client.get(response.get('Location'))
    print('Follow-up status:', resp2.status_code)
    # messages appear in template; we just confirm page loads OK
    print('OK after redirect')
