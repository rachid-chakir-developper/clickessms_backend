# Generated by Django 3.2.22 on 2024-05-25 12:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('companies', '0024_activityauthorization_document'),
    ]

    operations = [
        migrations.AddField(
            model_name='activityauthorization',
            name='temporary_capacity',
            field=models.FloatField(null=True),
        ),
    ]