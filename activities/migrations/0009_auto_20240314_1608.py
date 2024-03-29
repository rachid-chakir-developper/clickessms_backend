# Generated by Django 3.2.22 on 2024-03-14 15:08

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('human_ressources', '0020_remove_employeegroup_employees'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('activities', '0008_rename_eventbeneficiaryabsence_beneficiaryabsence'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='beneficiaryabsence',
            name='beneficiary',
        ),
        migrations.AddField(
            model_name='beneficiaryabsence',
            name='employee',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='employee_beneficiary_absences', to='human_ressources.employee'),
        ),
        migrations.AlterField(
            model_name='beneficiaryabsence',
            name='creator',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='beneficiary_absence_former', to=settings.AUTH_USER_MODEL),
        ),
        migrations.CreateModel(
            name='BeneficiaryAbsenceItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated_at', models.DateTimeField(auto_now=True, null=True)),
                ('beneficiary', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='beneficiary_absence_items', to='human_ressources.beneficiary')),
                ('beneficiary_absence', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='activities.beneficiaryabsence')),
                ('creator', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='beneficiary_absence_item_former', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
