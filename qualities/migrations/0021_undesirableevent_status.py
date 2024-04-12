# Generated by Django 3.2.22 on 2024-04-05 14:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('qualities', '0020_undesirableeventestablishmentservice'),
    ]

    operations = [
        migrations.AddField(
            model_name='undesirableevent',
            name='status',
            field=models.CharField(choices=[('NEW', 'À faire'), ('STARTED', 'En cours'), ('FINISHED', 'Terminée'), ('PENDING', 'En attente'), ('CANCELED', 'Annulée'), ('ARCHIVED', 'Archivée')], default='NEW', max_length=50),
        ),
    ]