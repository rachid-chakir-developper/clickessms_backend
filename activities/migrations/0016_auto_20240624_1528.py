# Generated by Django 3.2.22 on 2024-06-24 13:28

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('companies', '0026_auto_20240530_1515'),
        ('human_ressources', '0040_employeecontractestablishment'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('medias', '0011_file_company'),
        ('activities', '0015_auto_20240520_1043'),
    ]

    operations = [
        migrations.CreateModel(
            name='TransmissionEvent',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('number', models.CharField(editable=False, max_length=255, null=True)),
                ('title', models.CharField(max_length=255)),
                ('starting_date_time', models.DateTimeField(null=True)),
                ('ending_date_time', models.DateTimeField(null=True)),
                ('description', models.TextField(default='', null=True)),
                ('observation', models.TextField(default='', null=True)),
                ('is_active', models.BooleanField(default=True, null=True)),
                ('is_deleted', models.BooleanField(default=False, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated_at', models.DateTimeField(auto_now=True, null=True)),
                ('company', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='company_transmission_events', to='companies.company')),
                ('creator', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
                ('employee', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='employee_transmission_events', to='human_ressources.employee')),
                ('folder', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='medias.folder')),
                ('image', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='transmission_event_image', to='medias.file')),
            ],
        ),
        migrations.CreateModel(
            name='TransmissionEventBeneficiary',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated_at', models.DateTimeField(auto_now=True, null=True)),
                ('beneficiary', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='transmission_event_beneficiary', to='human_ressources.beneficiary')),
                ('creator', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='transmission_event_beneficiary_former', to=settings.AUTH_USER_MODEL)),
                ('transmission_event', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='beneficiaries', to='activities.transmissionevent')),
            ],
        ),
        migrations.RemoveField(
            model_name='eventbeneficiary',
            name='beneficiary',
        ),
        migrations.RemoveField(
            model_name='eventbeneficiary',
            name='creator',
        ),
        migrations.RemoveField(
            model_name='eventbeneficiary',
            name='event',
        ),
        migrations.RemoveField(
            model_name='beneficiaryabsence',
            name='event',
        ),
        migrations.AlterField(
            model_name='beneficiaryabsenceitem',
            name='beneficiary_absence',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='beneficiaries', to='activities.beneficiaryabsence'),
        ),
        migrations.DeleteModel(
            name='Event',
        ),
        migrations.DeleteModel(
            name='EventBeneficiary',
        ),
        migrations.AddField(
            model_name='beneficiaryabsence',
            name='transmission_event',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='activities.transmissionevent'),
        ),
    ]
