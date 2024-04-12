# Generated by Django 3.2.22 on 2023-10-24 10:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('human_ressources', '0004_auto_20231024_1205'),
    ]

    operations = [
        migrations.AddField(
            model_name='employee',
            name='hiring_date',
            field=models.DateTimeField(null=True),
        ),
        migrations.AddField(
            model_name='employee',
            name='probation_end_date',
            field=models.DateTimeField(null=True),
        ),
        migrations.AddField(
            model_name='employee',
            name='starting_salary',
            field=models.FloatField(null=True),
        ),
        migrations.AddField(
            model_name='employee',
            name='work_end_date',
            field=models.DateTimeField(null=True),
        ),
    ]