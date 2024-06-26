# Generated by Django 3.2.22 on 2024-06-17 08:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('qualities', '0041_auto_20240617_0955'),
    ]

    operations = [
        migrations.AlterField(
            model_name='undesirableevent',
            name='status',
            field=models.CharField(choices=[('NEW', 'Déclaré'), ('IN_PROGRESS', 'En cours'), ('DONE', 'Traité'), ('ACCEPTED', 'Accepté'), ('REFUSED', 'Refusé'), ('COMPLETED', 'Terminée'), ('ON_HOLD', 'En attente'), ('CANCELED', 'Annulée'), ('ARCHIVED', 'Archivée')], default='NEW', max_length=50),
        ),
    ]
