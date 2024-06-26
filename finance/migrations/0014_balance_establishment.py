# Generated by Django 3.2.22 on 2024-05-22 12:59

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('companies', '0020_establishment_company'),
        ('finance', '0013_balance_folder'),
    ]

    operations = [
        migrations.AddField(
            model_name='balance',
            name='establishment',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='establishment_balances', to='companies.establishment'),
        ),
    ]
