# Generated by Django 3.2.22 on 2024-09-23 08:16

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('companies', '0027_company_sce_shop_url'),
        ('medias', '0011_file_company'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('sce', '0004_scemember_role'),
    ]

    operations = [
        migrations.CreateModel(
            name='SceBenefit',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('number', models.CharField(editable=False, max_length=255, null=True)),
                ('title', models.CharField(blank=True, max_length=255, null=True)),
                ('description', models.TextField(default='', null=True)),
                ('observation', models.TextField(default='', null=True)),
                ('is_active', models.BooleanField(default=True, null=True)),
                ('is_deleted', models.BooleanField(default=False, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated_at', models.DateTimeField(auto_now=True, null=True)),
                ('company', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='company_sce_benefits', to='companies.company')),
                ('creator', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='sce_benefit_former', to=settings.AUTH_USER_MODEL)),
                ('folder', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='medias.folder')),
            ],
        ),
    ]
