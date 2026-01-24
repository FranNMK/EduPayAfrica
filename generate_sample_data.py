"""
Generate sample data for bulk upload practice (30 rows)
Run with: python manage.py shell < generate_sample_data.py
"""

import csv
import random
import sys
from datetime import datetime, timedelta

from institutions.models import InstitutionProfile, Program, AcademicYear

# Sample data
FIRST_NAMES = [
    "John", "Jane", "Michael", "Sarah", "David", "Emma", "Robert", "Olivia",
    "James", "Sophia", "William", "Ava", "Richard", "Isabella", "Joseph", "Mia",
    "Thomas", "Charlotte", "Charles", "Amelia", "Christopher", "Harper", "Daniel", "Evelyn",
    "Matthew", "Abigail", "Mark", "Emily", "Donald", "Elizabeth"
]

LAST_NAMES = [
    "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis",
    "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson",
    "Thomas", "Taylor", "Moore", "Jackson", "Martin", "Lee", "Perez", "Thompson",
    "White", "Harris", "Sanchez", "Clark", "Ramirez", "Lewis", "Robinson"
]

def generate_student_data():
    """Generate 30 sample student records."""
    
    # Get institution and program for filtering
    institution = InstitutionProfile.objects.first()
    program = Program.objects.filter(institution=institution).first()
    academic_year = AcademicYear.objects.filter(institution=institution).first()
    
    if not (institution and program and academic_year):
        print("❌ Error: Please create at least one Institution, Program, and Academic Year first!")
        return
    
    # Generate CSV
    filename = "../sample_students_30rows.csv"
    
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = [
            'full_name', 'admission_number', 'email', 'phone_number',
            'institution', 'program', 'academic_year', 'admission_date', 'is_active'
        ]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        
        for i in range(30):
            first_name = random.choice(FIRST_NAMES)
            last_name = random.choice(LAST_NAMES)
            full_name = f"{first_name} {last_name}"
            admission_number = f"ADM{datetime.now().year}{i+1:04d}"
            email = f"{first_name.lower()}.{last_name.lower()}{i+1}@edupay.com"
            phone_number = f"254{random.randint(100000000, 999999999)}"
            admission_date = (datetime.now() - timedelta(days=random.randint(1, 365))).strftime("%Y-%m-%d")
            
            writer.writerow({
                'full_name': full_name,
                'admission_number': admission_number,
                'email': email,
                'phone_number': phone_number,
                'institution': institution.id,
                'program': program.id,
                'academic_year': academic_year.id,
                'admission_date': admission_date,
                'is_active': 'True'
            })
    
    print(f"✅ Sample student data generated: {filename}")
    print(f"   📊 30 rows created")


def generate_staff_data():
    """Generate 30 sample staff records."""
    
    institution = InstitutionProfile.objects.first()
    
    if not institution:
        print("❌ Error: Please create at least one Institution first!")
        return
    
    filename = "../sample_staff_30rows.csv"
    
    DEPARTMENTS = ["Administration", "Finance", "Academic", "Support Services", "IT"]
    ROLES = ["Director", "Coordinator", "Officer", "Assistant", "Manager"]
    
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = [
            'first_name', 'last_name', 'email', 'phone_number',
            'institution', 'department', 'role', 'employment_date', 'is_active'
        ]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        
        for i in range(30):
            first_name = random.choice(FIRST_NAMES)
            last_name = random.choice(LAST_NAMES)
            email = f"{first_name.lower()}.{last_name.lower()}{i+1}@edupay-staff.com"
            phone_number = f"254{random.randint(100000000, 999999999)}"
            department = random.choice(DEPARTMENTS)
            role = random.choice(ROLES)
            employment_date = (datetime.now() - timedelta(days=random.randint(1, 730))).strftime("%Y-%m-%d")
            
            writer.writerow({
                'first_name': first_name,
                'last_name': last_name,
                'email': email,
                'phone_number': phone_number,
                'institution': institution.id,
                'department': department,
                'role': role,
                'employment_date': employment_date,
                'is_active': 'True'
            })
    
    print(f"✅ Sample staff data generated: {filename}")
    print(f"   📊 30 rows created")


if __name__ == "__main__" or True:
    print("=" * 60)
    print("📋 SAMPLE DATA GENERATOR FOR BULK UPLOAD")
    print("=" * 60)
    print()
    
    # Generate both by default when called from shell
    generate_student_data()
    generate_staff_data()
    
    print()
    print("=" * 60)
    print("✨ Sample data files created successfully!")
    print("=" * 60)

