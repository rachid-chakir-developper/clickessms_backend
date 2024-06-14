# Generated by Django 3.2.22 on 2024-05-27 13:52

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('medias', '0011_file_company'),
        ('human_ressources', '0037_employeecontract_folder'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('data_management', '0021_rename_meetingtype_typemeeting'),
        ('companies', '0025_activityauthorization_temporary_capacity'),
    ]

    operations = [
        migrations.CreateModel(
            name='EmployeeAbsence',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('number', models.CharField(editable=False, max_length=255, null=True)),
                ('title', models.CharField(max_length=255)),
                ('starting_date_time', models.DateTimeField(null=True)),
                ('ending_date_time', models.DateTimeField(null=True)),
                ('other_reasons', models.CharField(max_length=255, null=True)),
                ('comment', models.TextField(default='', null=True)),
                ('observation', models.TextField(default='', null=True)),
                ('is_deleted', models.BooleanField(default=False, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated_at', models.DateTimeField(auto_now=True, null=True)),
                ('company', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='company_employee_absences', to='companies.company')),
                ('creator', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='employee_absence_former', to=settings.AUTH_USER_MODEL)),
                ('employee', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='employee_employee_absences', to='human_ressources.employee')),
                ('folder', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='medias.folder')),
                ('reasons', models.ManyToManyField(related_name='reason_employee_absences', to='data_management.AbsenceReason')),
            ],
        ),
        migrations.CreateModel(
            name='EmployeeAbsenceItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated_at', models.DateTimeField(auto_now=True, null=True)),
                ('creator', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='employee_absence_item_former', to=settings.AUTH_USER_MODEL)),
                ('employee', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='employee_absence_items', to='human_ressources.employee')),
                ('employee_absence', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='planning.employeeabsence')),
            ],
        ),
    ]