# Generated by Django 3.2.22 on 2024-05-02 08:10

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('qualities', '0022_delete_undesirableeventestablishmentservice'),
        ('companies', '0014_establishment_additional_address'),
    ]

    operations = [
        migrations.DeleteModel(
            name='EstablishmentService',
        ),
    ]
