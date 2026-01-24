import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'EduPayAfrica.settings')
sys.path.insert(0, '.')

django.setup()

from django.core.management import execute_from_command_line

if __name__ == '__main__':
    sys.argv = ['manage.py', 'makemigrations', 'institutions']
    execute_from_command_line(sys.argv)
