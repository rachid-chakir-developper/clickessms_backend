# Generated by Django 3.2.22 on 2024-05-20 08:43

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('companies', '0020_establishment_company'),
        ('qualities', '0024_undesirableevent_is_deleted'),
    ]

    operations = [
        migrations.AddField(
            model_name='undesirableevent',
            name='company',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='company_undesirable_events', to='companies.company'),
        ),
    ]
