# Generated by Django 3.2.22 on 2024-03-18 13:58

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('data_management', '0006_undesirableeventfrequency'),
        ('qualities', '0009_auto_20240318_1456'),
    ]

    operations = [
        migrations.AddField(
            model_name='undesirableevent',
            name='frequency',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='frequency_undesirable_events', to='data_management.undesirableeventfrequency'),
        ),
    ]