# Generated by Django 3.2.22 on 2024-03-13 10:13

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('human_ressources', '0013_beneficiary'),
        ('activities', '0003_eventabsencebeneficiary'),
    ]

    operations = [
        migrations.CreateModel(
            name='EventBeneficiaryAbsence',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('number', models.CharField(editable=False, max_length=255, null=True)),
                ('title', models.CharField(max_length=255)),
                ('starting_date_time', models.DateTimeField(null=True)),
                ('ending_date_time', models.DateTimeField(null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated_at', models.DateTimeField(auto_now=True, null=True)),
                ('beneficiary', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='event_beneficiary_absence', to='human_ressources.beneficiary')),
                ('creator', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='event_beneficiary_absence_former', to=settings.AUTH_USER_MODEL)),
                ('event', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='activities.event')),
            ],
        ),
        migrations.DeleteModel(
            name='EventAbsenceBeneficiary',
        ),
    ]
