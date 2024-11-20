# Generated by Django 3.2.22 on 2024-11-05 16:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('planning', '0012_employeeshift'),
    ]

    operations = [
        migrations.AddField(
            model_name='employeeshift',
            name='description',
            field=models.TextField(blank=True, default='', null=True),
        ),
        migrations.AddField(
            model_name='employeeshift',
            name='title',
            field=models.CharField(blank=True, default='', max_length=255, null=True),
        ),
    ]