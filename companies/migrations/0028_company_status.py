# Generated by Django 3.2.22 on 2024-10-28 14:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('companies', '0027_company_sce_shop_url'),
    ]

    operations = [
        migrations.AddField(
            model_name='company',
            name='status',
            field=models.CharField(choices=[('ACTIVE', 'Active'), ('INACTIVE', 'Inactive'), ('PENDING', 'En attente de vérification'), ('SUSPENDED', 'Suspendue'), ('CLOSED', 'Fermée')], default='ACTIVE', max_length=20),
        ),
    ]