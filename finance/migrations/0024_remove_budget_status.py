# Generated by Django 3.2.22 on 2024-11-12 11:49

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('finance', '0023_alter_budget_status'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='budget',
            name='status',
        ),
    ]
