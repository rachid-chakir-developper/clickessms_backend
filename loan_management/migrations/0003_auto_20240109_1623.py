# Generated by Django 3.2.22 on 2024-01-09 15:23

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('sales', '0001_initial'),
        ('loan_management', '0002_alter_objectrecovery_the_object'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='objectrecovery',
            name='client',
        ),
        migrations.AddField(
            model_name='theobject',
            name='client',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='the_object_client', to='sales.client'),
        ),
    ]
