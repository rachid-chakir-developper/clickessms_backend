# Generated by Django 3.2.22 on 2024-05-20 08:43

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('companies', '0020_establishment_company'),
        ('activities', '0014_auto_20240520_0954'),
    ]

    operations = [
        migrations.AddField(
            model_name='beneficiaryabsence',
            name='company',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='company_beneficiary_absences', to='companies.company'),
        ),
        migrations.AddField(
            model_name='event',
            name='company',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='company_events', to='companies.company'),
        ),
    ]