# Generated by Django 3.2.22 on 2024-04-05 08:42

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('companies', '0010_auto_20240405_0959'),
    ]

    operations = [
        migrations.AddField(
            model_name='establishmentservice',
            name='establishment_service_parent',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='establishment_service_childs', to='companies.establishmentservice'),
        ),
        migrations.AddField(
            model_name='establishmentservice',
            name='establishment_service_type',
            field=models.CharField(choices=[('PRIMARY', 'Primaire'), ('SECONDARY', 'Sécondaire')], default='PRIMARY', max_length=50, null=True),
        ),
    ]