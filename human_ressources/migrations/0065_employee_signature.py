# Generated by Django 3.2.22 on 2025-01-13 08:43

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('medias', '0013_contracttemplate_image'),
        ('human_ressources', '0064_beneficiaryadmission_status_reason'),
    ]

    operations = [
        migrations.AddField(
            model_name='employee',
            name='signature',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='signature_employees', to='medias.file'),
        ),
    ]
