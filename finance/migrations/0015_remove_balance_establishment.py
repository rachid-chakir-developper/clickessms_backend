# Generated by Django 3.2.22 on 2024-05-22 13:11

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('finance', '0014_balance_establishment'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='balance',
            name='establishment',
        ),
    ]
