# Generated by Django 3.2.22 on 2024-11-13 15:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('purchases', '0009_expense_expenseitem'),
    ]

    operations = [
        migrations.AlterField(
            model_name='expense',
            name='status',
            field=models.CharField(choices=[('DRAFT', 'Brouillon'), ('NEW', 'Nouveau'), ('PENDING', 'En Attente'), ('APPROVED', 'Approuvé'), ('REJECTED', 'Rejeté'), ('PAID', 'Payé'), ('UNPAID', 'Non payé')], default='PENDING', max_length=20),
        ),
        migrations.AlterField(
            model_name='expenseitem',
            name='status',
            field=models.CharField(choices=[('PENDING', 'En Attente'), ('APPROVED', 'Approuvé'), ('REJECTED', 'Rejeté'), ('PAID', 'Payé'), ('UNPAID', 'Non payé')], default='PENDING', max_length=20),
        ),
    ]
