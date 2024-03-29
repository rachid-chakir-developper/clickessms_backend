# Generated by Django 3.2.22 on 2024-01-25 14:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('companies', '0002_company_folder'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='company',
            name='authorized_domains',
        ),
        migrations.AddField(
            model_name='company',
            name='bank_name',
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='company',
            name='bic',
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='company',
            name='iban',
            field=models.CharField(max_length=255, null=True),
        ),
    ]
