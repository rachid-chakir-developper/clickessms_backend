# Generated by Django 3.2.22 on 2024-06-07 10:27

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('qualities', '0027_auto_20240607_1220'),
    ]

    operations = [
        migrations.AlterField(
            model_name='undesirableeventbeneficiary',
            name='undesirable_event',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='beneficiaries', to='qualities.undesirableevent'),
        ),
        migrations.AlterField(
            model_name='undesirableeventemployee',
            name='undesirable_event',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='employees', to='qualities.undesirableevent'),
        ),
        migrations.AlterField(
            model_name='undesirableeventestablishment',
            name='undesirable_event',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='establishments', to='qualities.undesirableevent'),
        ),
        migrations.AlterField(
            model_name='undesirableeventnotifiedperson',
            name='undesirable_event',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='notified_persons', to='qualities.undesirableevent'),
        ),
    ]
