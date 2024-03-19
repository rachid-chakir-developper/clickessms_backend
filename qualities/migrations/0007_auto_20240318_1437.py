# Generated by Django 3.2.22 on 2024-03-18 13:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('data_management', '0005_auto_20240318_1409'),
        ('qualities', '0006_undesirableeventemployee'),
    ]

    operations = [
        migrations.AddField(
            model_name='undesirableevent',
            name='undesirable_event_normal_type',
            field=models.ManyToManyField(related_name='undesirable_event_normal_type_events', to='data_management.UndesirableEventNormalType'),
        ),
        migrations.AddField(
            model_name='undesirableevent',
            name='undesirable_event_serious_type',
            field=models.ManyToManyField(related_name='undesirable_event_serious_type_events', to='data_management.UndesirableEventSeriousType'),
        ),
    ]
