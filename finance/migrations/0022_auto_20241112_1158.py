# Generated by Django 3.2.22 on 2024-11-12 10:58

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('finance', '0021_budget'),
    ]

    operations = [
        migrations.RenameField(
            model_name='budget',
            old_name='end_date',
            new_name='ending_date',
        ),
        migrations.RenameField(
            model_name='budget',
            old_name='start_date',
            new_name='starting_date',
        ),
    ]
