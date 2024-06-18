# Generated by Django 3.2.22 on 2024-06-18 14:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('planning', '0004_rename_absence_typo_employeeabsence_absence_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='employeeabsence',
            name='absence_type',
            field=models.CharField(choices=[('ANNUAL', 'Congé Annuel'), ('SICK', 'Congé Maladie'), ('MATERNITY', 'Congé Maternité'), ('PATERNITY', 'Congé Paternité'), ('UNPAID', 'Congé Sans Solde'), ('PARENTAL', 'Congé Parental'), ('BEREAVEMENT', 'Congé de Décès'), ('MARRIAGE', 'Congé de Mariage'), ('STUDY', 'Congé de Formation'), ('ADOPTION', "Congé d'Adoption"), ('ABSENCE', 'Absence')], default='ABSENCE', max_length=50),
        ),
        migrations.AlterField(
            model_name='employeeabsence',
            name='leave_type',
            field=models.CharField(choices=[('ANNUAL', 'Congé Annuel'), ('SICK', 'Congé Maladie'), ('MATERNITY', 'Congé Maternité'), ('PATERNITY', 'Congé Paternité'), ('UNPAID', 'Congé Sans Solde'), ('PARENTAL', 'Congé Parental'), ('BEREAVEMENT', 'Congé de Décès'), ('MARRIAGE', 'Congé de Mariage'), ('STUDY', 'Congé de Formation'), ('ADOPTION', "Congé d'Adoption"), ('ABSENCE', 'Absence')], default='ABSENCE', max_length=50),
        ),
    ]