# Generated by Django 3.2.22 on 2024-11-13 09:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('finance', '0028_auto_20241113_1045'),
    ]

    operations = [
        migrations.AlterField(
            model_name='expense',
            name='status',
            field=models.CharField(choices=[('DRAFT', 'Brouillon'), ('NEW', 'Nouveau'), ('PENDING', 'En Attente'), ('APPROVED', 'Approuvé'), ('REJECTED', 'Rejeté')], default='PENDING', max_length=20),
        ),
    ]
