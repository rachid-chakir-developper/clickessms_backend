# Generated by Django 3.2.22 on 2024-01-30 13:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('companies', '0003_auto_20240125_1521'),
    ]

    operations = [
        migrations.AlterField(
            model_name='company',
            name='is_active',
            field=models.BooleanField(default=True, null=True),
        ),
    ]
