# Generated by Django 3.2.22 on 2024-02-20 13:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sales', '0004_client_folder'),
    ]

    operations = [
        migrations.AddField(
            model_name='client',
            name='external_number',
            field=models.CharField(default='', max_length=255, null=True),
        ),
    ]