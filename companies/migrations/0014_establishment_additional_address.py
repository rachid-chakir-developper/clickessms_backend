# Generated by Django 3.2.22 on 2024-04-05 13:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('companies', '0013_alter_establishment_establishment_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='establishment',
            name='additional_address',
            field=models.TextField(default='', null=True),
        ),
    ]