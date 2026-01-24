#!/usr/bin/env python
"""
Quick script to add 50 students directly
Run from project root: python add_students_quick.py
"""

import os
import sys
import django
import random
from datetime import datetime, timedelta

# Setup Django
sys.path.insert(0, os.path.dirname(__file__))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'EduPayAfrica.settings')
django.setup()

from institutions.models import InstitutionProfile, Program, AcademicYear, Student

FIRST_NAMES = [
    "John", "Jane", "Michael", "Sarah", "David", "Emma", "Robert", "Olivia",
    "James", "Sophia", "William", "Ava", "Richard", "Isabella", "Joseph", "Mia",
    "Thomas", "Charlotte", "Charles", "Amelia", "Christopher", "Harper", "Daniel", "Evelyn",
    "Matthew", "Abigail", "Mark", "Emily", "Donald", "Elizabeth", "Kenneth", "Abigail",
    "Steven", "Ella", "Paul", "Madison", "Andrew", "Chloe", "Joshua", "Camila",
    "Kevin", "Sophia", "Brian", "Hannah", "Edward", "Lily", "Ronald", "Scarlett",
    "Anthony", "Grace", "Frank", "Victoria"
]

LAST_NAMES = [
    "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis",
    "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson",
    "Thomas", "Taylor", "Moore", "Jackson", "Martin", "Lee", "Perez", "Thompson",
    "White", "Harris", "Sanchez", "Clark", "Ramirez", "Lewis", "Robinson", "Walker",
    "Young", "King", "Wright", "Hill", "Scott", "Green", "Adams", "Nelson",
    "Carter", "Roberts", "Byrne", "Mitchell", "Campbell", "Parker", "Evans", "Edwards",
    "Collins", "Stewart", "Sanchez", "Morris", "Murphy", "Cook"
]

# Get institution, program, and academic year
institution = InstitutionProfile.objects.first()
program = Program.objects.filter(institution=institution).first()
academic_year = AcademicYear.objects.filter(institution=institution).first()

if not (institution and program and academic_year):
    print("❌ Error: Please create at least one Institution, Program, and Academic Year first!")
    sys.exit(1)

print(f"🏫 Institution: {institution.institution_name}")
print(f"📚 Program: {program.program_name}")
print(f"📅 Academic Year: {academic_year.year_code}")
print(f"\n🚀 Adding 50 students...\n")

students_created = 0
existing_admission_numbers = set(Student.objects.values_list('admission_number', flat=True))

for i in range(1, 51):
    first_name = random.choice(FIRST_NAMES)
    last_name = random.choice(LAST_NAMES)
    full_name = f"{first_name} {last_name}"
    
    # Generate unique admission number
    admission_number = f"ADM{datetime.now().year}{i:04d}"
    while admission_number in existing_admission_numbers:
        admission_number = f"ADM{datetime.now().year}{random.randint(1, 9999):04d}"
    existing_admission_numbers.add(admission_number)
    
    email = f"{first_name.lower()}.{last_name.lower()}{i}@edupay.com"
    phone_number = f"254{random.randint(100000000, 999999999)}"
    admission_date = (datetime.now() - timedelta(days=random.randint(1, 365))).date()
    is_active = random.choice([True, True, True, True, False])  # 80% active
    
    try:
        student = Student.objects.create(
            full_name=full_name,
            admission_number=admission_number,
            email=email,
            phone_number=phone_number,
            institution=institution,
            program=program,
            academic_year=academic_year,
            date_of_birth=(datetime.now() - timedelta(days=random.randint(6570, 7300))).date(),
            gender=random.choice(['M', 'F', 'Other']),
            is_active=is_active
        )
        students_created += 1
        print(f"✓ [{i:2d}] {full_name:25s} | {admission_number:12s} | {email}")
    except Exception as e:
        print(f"✗ [{i:2d}] Error: {str(e)}")

print(f"\n{'='*70}")
print(f"✅ Successfully added {students_created} students!")
print(f"📊 Total students in database: {Student.objects.count()}")
print(f"{'='*70}")
