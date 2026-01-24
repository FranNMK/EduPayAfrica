"""
Django management command to generate sample data
Place this file in: EduPayAfrica/institutions/management/commands/generate_sample_data.py
"""

import csv
import random
from datetime import datetime, timedelta
from django.core.management.base import BaseCommand
from institutions.models import InstitutionProfile, Program, AcademicYear

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

DEPARTMENTS = ["Administration", "Finance", "Academic", "Support Services", "IT"]
ROLES = ["Director", "Coordinator", "Officer", "Assistant", "Manager"]


class Command(BaseCommand):
    help = 'Generate sample data for bulk upload practice (30 rows)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--type',
            type=str,
            default='both',
            choices=['students', 'staff', 'both'],
            help='Type of data to generate'
        )

    def handle(self, *args, **options):
        data_type = options['type']

        if data_type in ['students', 'both']:
            self.generate_students()

        if data_type in ['staff', 'both']:
            self.generate_staff()

        self.stdout.write(self.style.SUCCESS(
            '✨ Sample data generated successfully!'
        ))

    def generate_students(self):
        """Generate 30 sample student records."""

        institution = InstitutionProfile.objects.first()
        program = Program.objects.filter(institution=institution).first()
        academic_year = AcademicYear.objects.filter(institution=institution).first()

        if not (institution and program and academic_year):
            self.stdout.write(self.style.ERROR(
                '❌ Error: Please create at least one Institution, Program, and Academic Year first!'
            ))
            return

        filename = "sample_students_30rows.csv"

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

        self.stdout.write(self.style.SUCCESS(
            f'✅ Sample student data generated: {filename}\n   📊 30 rows created'
        ))

    def generate_staff(self):
        """Generate 30 sample staff records."""

        institution = InstitutionProfile.objects.first()

        if not institution:
            self.stdout.write(self.style.ERROR(
                '❌ Error: Please create at least one Institution first!'
            ))
            return

        filename = "sample_staff_30rows.csv"

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

        self.stdout.write(self.style.SUCCESS(
            f'✅ Sample staff data generated: {filename}\n   📊 30 rows created'
        ))
