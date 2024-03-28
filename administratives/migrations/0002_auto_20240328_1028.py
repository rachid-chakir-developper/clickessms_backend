# Generated by Django 3.2.22 on 2024-03-28 09:28

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('human_ressources', '0020_remove_employeegroup_employees'),
        ('administratives', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='call',
            name='employee',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='employee_calls', to='human_ressources.employee'),
        ),
        migrations.DeleteModel(
            name='CallBeneficiaryAbsence',
        ),
    ]
