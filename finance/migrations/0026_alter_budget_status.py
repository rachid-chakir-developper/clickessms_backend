# Generated by Django 3.2.22 on 2024-11-12 13:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('finance', '0025_budget_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='budget',
            name='status',
            field=models.CharField(choices=[('DRAFT', 'Brouillon'), ('PENDING', 'En attente de validation'), ('APPROVED', 'Validé'), ('REJECTED', 'Rejeté'), ('IN_PROGRESS', 'En cours'), ('PARTIALLY_USED', 'Partiellement utilisé'), ('COMPLETED', 'Complété'), ('OVERSPENT', 'Dépassement'), ('ON_HOLD', 'En attente'), ('CANCELLED', 'Annulé'), ('CLOSED', 'Clôturé')], default='PENDING', max_length=20),
        ),
    ]
