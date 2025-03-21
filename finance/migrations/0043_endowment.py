# Generated by Django 3.2.22 on 2025-01-20 14:37

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('data_management', '0046_professionalstatus_typeendowment'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('companies', '0035_companymedia_blog_url'),
        ('finance', '0042_alter_decisiondocumentitem_establishment'),
    ]

    operations = [
        migrations.CreateModel(
            name='Endowment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('number', models.CharField(editable=False, max_length=255, null=True)),
                ('name', models.CharField(max_length=255, null=True)),
                ('description', models.TextField(blank=True, default='', null=True)),
                ('observation', models.TextField(blank=True, default='', null=True)),
                ('amount_allocated', models.DecimalField(decimal_places=2, max_digits=10)),
                ('starting_date_time', models.DateTimeField(null=True)),
                ('ending_date_time', models.DateTimeField(null=True)),
                ('age_min', models.IntegerField(blank=True, null=True, verbose_name='Âge minimum')),
                ('age_max', models.IntegerField(blank=True, null=True, verbose_name='Âge maximum')),
                ('is_active', models.BooleanField(default=True, null=True)),
                ('is_deleted', models.BooleanField(default=False, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated_at', models.DateTimeField(auto_now=True, null=True)),
                ('accounting_nature', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='endowments', to='data_management.accountingnature')),
                ('company', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='company_endowments', to='companies.company')),
                ('creator', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
                ('endowment_type', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='endowments', to='data_management.typeendowment')),
                ('establishment', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='endowments', to='companies.establishment')),
                ('gender', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='data_management.humangender')),
                ('professional_status', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='endowments', to='data_management.professionalstatus')),
            ],
        ),
    ]
