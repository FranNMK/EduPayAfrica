#!/usr/bin/env python
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'EduPayAfrica.settings')
django.setup()

from django.test import Client
from django.urls import reverse

# Test if we can access the demo URL
client = Client()
response = client.get('/demo/')

print(f"Status Code: {response.status_code}")
print(f"Resolved URL: {reverse('demo')}")
print(f"Demo page is {'accessible' if response.status_code == 200 else 'NOT accessible'}")
