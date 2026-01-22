#!/usr/bin/env python
"""
Quick test script to verify email functionality
Run: python test_email.py
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'EduPayAfrica.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.core.mail import send_mail
from django.conf import settings
from leads.views import send_confirmation_email
from core.views import send_contact_confirmation_email

def test_demo_email():
    """Test demo request confirmation email"""
    print("=" * 60)
    print("Testing Demo Request Email")
    print("=" * 60)
    print(f"Email Backend: {settings.EMAIL_BACKEND}")
    print(f"From Email: {settings.DEFAULT_FROM_EMAIL}")
    print()
    
    try:
        send_confirmation_email("Test User", "test@example.com")
        print("✓ Demo email sent successfully (check console output above)")
    except Exception as e:
        print(f"✗ Demo email failed: {e}")
    
    print()

def test_contact_email():
    """Test contact inquiry confirmation email"""
    print("=" * 60)
    print("Testing Contact Inquiry Email")
    print("=" * 60)
    print(f"Email Backend: {settings.EMAIL_BACKEND}")
    print(f"From Email: {settings.DEFAULT_FROM_EMAIL}")
    print()
    
    try:
        send_contact_confirmation_email("Contact User", "contact@example.com")
        print("✓ Contact email sent successfully (check console output above)")
    except Exception as e:
        print(f"✗ Contact email failed: {e}")
    
    print()

def test_direct_email():
    """Test direct Django send_mail"""
    print("=" * 60)
    print("Testing Direct Django send_mail()")
    print("=" * 60)
    print(f"Email Backend: {settings.EMAIL_BACKEND}")
    print(f"From Email: {settings.DEFAULT_FROM_EMAIL}")
    print()
    
    try:
        send_mail(
            'Test Email Subject',
            'This is a test email body to verify email configuration.',
            settings.DEFAULT_FROM_EMAIL,
            ['direct@example.com'],
            fail_silently=False,
        )
        print("✓ Direct email sent successfully (check console output above)")
    except Exception as e:
        print(f"✗ Direct email failed: {e}")
    
    print()

if __name__ == '__main__':
    print("\n" + "=" * 60)
    print("EMAIL FUNCTIONALITY TEST")
    print("=" * 60)
    print(f"DEBUG Mode: {settings.DEBUG}")
    print()
    
    test_direct_email()
    test_demo_email()
    test_contact_email()
    
    print("=" * 60)
    print("Tests completed!")
    print("=" * 60)
