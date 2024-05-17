# Generated by Django 3.2.22 on 2024-05-17 09:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('qualities', '0022_delete_undesirableeventestablishmentservice'),
    ]

    operations = [
        migrations.AlterField(
            model_name='undesirableevent',
            name='status',
            field=models.CharField(choices=[('NEW', 'À traiter'), ('ACCEPTED', 'Accepté'), ('REFUSED', 'Refusé'), ('STARTED', 'En cours'), ('FINISHED', 'Terminée'), ('PENDING', 'En attente'), ('CANCELED', 'Annulée'), ('ARCHIVED', 'Archivée')], default='NEW', max_length=50),
        ),
    ]
