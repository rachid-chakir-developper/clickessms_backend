# Generated by Django 3.2.22 on 2024-03-11 14:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('companies', '0008_auto_20240311_1540'),
    ]

    operations = [
        migrations.AddField(
            model_name='establishment',
            name='establishment_type',
            field=models.CharField(choices=[('PRIMARY', 'Primaire'), ('SECONDARY', 'Sécondaire')], default='PRIMARY', max_length=50, null=True),
        ),
    ]
