# Generated by Django 3.2.22 on 2024-05-30 13:15

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('companies', '0025_activityauthorization_temporary_capacity'),
    ]

    operations = [
        migrations.AlterField(
            model_name='activityauthorization',
            name='establishment',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='activity_authorizations', to='companies.establishment'),
        ),
        migrations.AlterField(
            model_name='establishmentmanager',
            name='establishment',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='managers', to='companies.establishment'),
        ),
    ]