# Generated by Django 3.2.22 on 2024-03-18 12:31

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('human_ressources', '0020_remove_employeegroup_employees'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('qualities', '0005_undesirableevent_undesirable_event_type'),
    ]

    operations = [
        migrations.CreateModel(
            name='UndesirableEventEmployee',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated_at', models.DateTimeField(auto_now=True, null=True)),
                ('creator', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='undesirable_event_employee_former', to=settings.AUTH_USER_MODEL)),
                ('employee', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='undesirable_event_employee', to='human_ressources.employee')),
                ('undesirable_event', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='qualities.undesirableevent')),
            ],
        ),
    ]
