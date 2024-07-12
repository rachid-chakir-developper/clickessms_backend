# Generated by Django 3.2.22 on 2024-07-12 09:53

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('medias', '0011_file_company'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('companies', '0026_auto_20240530_1515'),
        ('human_ressources', '0047_employee_social_security_number'),
        ('works', '0033_auto_20240627_1107'),
    ]

    operations = [
        migrations.CreateModel(
            name='EfcReport',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('number', models.CharField(editable=False, max_length=255, null=True)),
                ('title', models.CharField(max_length=255, null=True)),
                ('description', models.TextField(default='', null=True)),
                ('efc_date', models.DateTimeField(null=True)),
                ('declaration_date', models.DateTimeField(null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated_at', models.DateTimeField(auto_now=True, null=True)),
                ('company', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='efc_reports', to='companies.company')),
                ('creator', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='efc_reports', to=settings.AUTH_USER_MODEL)),
                ('document', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='efc_reports', to='medias.file')),
                ('employees', models.ManyToManyField(related_name='efc_reports', to='human_ressources.Employee')),
                ('ticket', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='efc_reports', to='works.ticket')),
            ],
        ),
    ]
