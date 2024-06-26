# Generated by Django 3.2.22 on 2024-05-20 07:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('human_ressources', '0027_employeecontract_document'),
    ]

    operations = [
        migrations.AddField(
            model_name='beneficiary',
            name='is_deleted',
            field=models.BooleanField(default=False, null=True),
        ),
        migrations.AddField(
            model_name='employee',
            name='is_deleted',
            field=models.BooleanField(default=False, null=True),
        ),
        migrations.AddField(
            model_name='employeecontract',
            name='is_deleted',
            field=models.BooleanField(default=False, null=True),
        ),
    ]
