# Generated by Django 3.2.22 on 2024-06-18 15:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('planning', '0005_auto_20240618_1638'),
    ]

    operations = [
        migrations.AlterField(
            model_name='employeeabsence',
            name='absence_type',
            field=models.CharField(choices=[('ABSENCE', 'Absence'), ('LEAVE', 'Congé')], default='ABSENCE', max_length=50),
        ),
    ]
