# Generated by Django 3.2.22 on 2024-01-10 10:32

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('partnerships', '0001_initial'),
        ('loan_management', '0003_auto_20240109_1623'),
    ]

    operations = [
        migrations.AddField(
            model_name='theobject',
            name='partner',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='the_object_partner', to='partnerships.partner'),
        ),
    ]
