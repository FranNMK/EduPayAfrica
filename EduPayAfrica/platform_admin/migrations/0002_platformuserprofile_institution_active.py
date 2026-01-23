from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('platform_admin', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='platformuserprofile',
            name='institution',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='profiles', to='platform_admin.institution'),
        ),
        migrations.AddField(
            model_name='platformuserprofile',
            name='is_active',
            field=models.BooleanField(default=True),
        ),
    ]
