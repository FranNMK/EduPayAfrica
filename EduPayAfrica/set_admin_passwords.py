#!/usr/bin/env python
"""
Script to set Django admin passwords for superusers.
This allows them to login to /admin/ with their credentials.
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'EduPayAfrica.settings')
django.setup()

from django.contrib.auth.models import User

# Get all superusers
superusers = User.objects.filter(is_superuser=True)

print("=" * 60)
print("SETTING DJANGO ADMIN PASSWORDS FOR SUPERUSERS")
print("=" * 60)
print(f"\nFound {superusers.count()} superuser(s):\n")

for user in superusers:
    print(f"  Username: {user.username}")
    print(f"  Email: {user.email}")
    print(f"  Has password set: {user.has_usable_password()}")
    print()

# Set passwords for each superuser
print("=" * 60)
print("SETTING PASSWORDS")
print("=" * 60)

password = input("\nEnter a password to set for all superusers: ").strip()

if not password:
    print("❌ Password cannot be empty!")
    sys.exit(1)

if len(password) < 6:
    print("❌ Password must be at least 6 characters!")
    sys.exit(1)

for user in superusers:
    user.set_password(password)
    user.save()
    print(f"✅ Password set for: {user.username} ({user.email})")

print("\n" + "=" * 60)
print("✅ COMPLETE!")
print("=" * 60)
print("\nYou can now login to Django admin at /admin/ with:")
print(f"  Username: {superusers.first().username} (or any superuser username)")
print(f"  Password: (the password you just entered)")
print("\n")
