# Generated by Django 3.2.22 on 2024-02-21 14:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('companies', '0006_alter_company_number'),
    ]

    operations = [
        migrations.AlterField(
            model_name='company',
            name='address',
            field=models.TextField(default='', null=True),
        ),
    ]
