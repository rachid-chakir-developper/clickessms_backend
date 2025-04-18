# Generated by Django 3.2.22 on 2025-01-21 11:30

from decimal import Decimal
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('data_management', '0046_professionalstatus_typeendowment'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('human_ressources', '0067_auto_20250117_1243'),
    ]

    operations = [
        migrations.CreateModel(
            name='BeneficiaryEndowmentEntry',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('initial_balance', models.DecimalField(decimal_places=2, default=Decimal('0.00'), max_digits=10)),
                ('starting_date', models.DateTimeField(null=True)),
                ('ending_date', models.DateTimeField(null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated_at', models.DateTimeField(auto_now=True, null=True)),
                ('beneficiary', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='beneficiary_endowment_entries', to='human_ressources.beneficiary')),
                ('creator', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
                ('endowment_type', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='beneficiary_endowment_entries', to='data_management.typeendowment')),
            ],
        ),
    ]
