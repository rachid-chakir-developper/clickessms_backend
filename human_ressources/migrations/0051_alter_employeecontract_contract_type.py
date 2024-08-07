# Generated by Django 3.2.22 on 2024-07-15 11:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('human_ressources', '0050_alter_employeecontract_contract_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='employeecontract',
            name='contract_type',
            field=models.CharField(choices=[('CDI', 'CDI'), ('CDD', 'CDD'), ('APPRENTICESHIP_CONTRACT', "Contrat d'apprentissage"), ('SINGLE_INTEGRATION_CONTRACT', "Contrat Unique d'Insertion (CUI)"), ('PROFESSIONALIZATION_CONTRACT', 'Contrat de professionnalisation'), ('SEASONAL_CONTRACT', 'Contrat saisonnier'), ('TEMPORARY_CONTRACT', 'Contrat intérimaire'), ('PART_TIME_CONTRACT', 'Contrat à temps partiel'), ('FULL_TIME_CONTRACT', 'Contrat à temps plein'), ('INTERNSHIP_CONTRACT', 'Contrat de stage')], default='CDI', max_length=50),
        ),
    ]
