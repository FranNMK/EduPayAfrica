# Generated manually for job_title field with choices

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('leads', '0003_demorequest_status_fields'),
    ]

    operations = [
        migrations.AlterField(
            model_name='demorequest',
            name='job_title',
            field=models.CharField(
                choices=[
                    ('director', 'Director'),
                    ('principal', 'Principal'),
                    ('bursar', 'Bursar'),
                    ('accountant', 'Accountant'),
                    ('registrar', 'Registrar'),
                    ('it_manager', 'IT Manager'),
                    ('administrator', 'Administrator'),
                    ('dean', 'Dean'),
                    ('finance_manager', 'Finance Manager'),
                    ('other', 'Other'),
                ],
                max_length=255
            ),
        ),
    ]
