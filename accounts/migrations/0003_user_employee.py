# Generated by Django 3.2.22 on 2023-10-24 09:17

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('human_ressources', '0002_auto_20231024_1117'),
        ('accounts', '0002_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='employee',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='employee_user', to='human_ressources.employee'),
        ),
    ]
