# Generated by Django 3.2.22 on 2024-10-08 14:02

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('medias', '0013_contracttemplate_image'),
        ('human_ressources', '0052_auto_20241007_1022'),
    ]

    operations = [
        migrations.AlterField(
            model_name='employeecontract',
            name='document',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='employee_contract_doucument', to='medias.file'),
        ),
    ]