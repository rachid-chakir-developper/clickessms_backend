# Generated by Django 3.2.22 on 2024-03-14 12:10

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('human_ressources', '0018_auto_20240313_1637'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='beneficiarygroup',
            name='beneficiaries',
        ),
    ]
