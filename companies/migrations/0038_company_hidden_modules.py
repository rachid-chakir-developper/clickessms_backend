# Generated by Django 3.2.22 on 2025-04-09 13:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('companies', '0037_auto_20250324_1229'),
    ]

    operations = [
        migrations.AddField(
            model_name='company',
            name='hidden_modules',
            field=models.TextField(blank=True, null=True),
        ),
    ]
