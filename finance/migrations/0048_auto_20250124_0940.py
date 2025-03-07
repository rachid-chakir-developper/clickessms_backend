# Generated by Django 3.2.22 on 2025-01-24 08:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('finance', '0047_auto_20250123_0940'),
    ]

    operations = [
        migrations.AddField(
            model_name='endowment',
            name='is_recurring',
            field=models.BooleanField(default=False, null=True),
        ),
        migrations.AddField(
            model_name='endowment',
            name='recurrence_days',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='endowment',
            name='recurrence_end_date',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='endowment',
            name='recurrence_frequency',
            field=models.CharField(blank=True, choices=[('DAILY', 'Tous les jours'), ('WEEKLY', 'Toutes les semaines'), ('MONTHLY', 'Tous les mois'), ('YEARLY', 'Tous les ans')], max_length=20, null=True),
        ),
        migrations.AddField(
            model_name='endowment',
            name='recurrence_rule',
            field=models.TextField(blank=True, null=True),
        ),
    ]
