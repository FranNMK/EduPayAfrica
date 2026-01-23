from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('platform_admin', '0001_initial'),
        ('leads', '0002_alter_demorequest_status'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterField(
            model_name='demorequest',
            name='status',
            field=models.CharField(
                choices=[
                    ('pending', 'Pending'),
                    ('approved', 'Approved'),
                    ('rejected', 'Rejected'),
                    ('new', 'New'),
                    ('contacted', 'Contacted'),
                    ('demo_completed', 'Demo Completed'),
                    ('converted', 'Converted'),
                ],
                default='pending',
                max_length=50,
            ),
        ),
        migrations.AddField(
            model_name='demorequest',
            name='approved_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='demorequest',
            name='approved_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='approved_demo_requests', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='demorequest',
            name='institution',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='demo_requests', to='platform_admin.institution'),
        ),
    ]
