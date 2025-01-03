# Generated by Django 3.2.22 on 2025-01-03 14:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('data_management', '0043_alter_customfield_field_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='absencereason',
            name='is_considered',
            field=models.BooleanField(default=True, null=True),
        ),
        migrations.AddField(
            model_name='accountingnature',
            name='is_considered',
            field=models.BooleanField(default=True, null=True),
        ),
        migrations.AddField(
            model_name='admissiondocumenttype',
            name='is_considered',
            field=models.BooleanField(default=True, null=True),
        ),
        migrations.AddField(
            model_name='beneficiarystatus',
            name='is_considered',
            field=models.BooleanField(default=True, null=True),
        ),
        migrations.AddField(
            model_name='documenttype',
            name='is_considered',
            field=models.BooleanField(default=True, null=True),
        ),
        migrations.AddField(
            model_name='employeemission',
            name='is_considered',
            field=models.BooleanField(default=True, null=True),
        ),
        migrations.AddField(
            model_name='establishmentcategory',
            name='is_considered',
            field=models.BooleanField(default=True, null=True),
        ),
        migrations.AddField(
            model_name='establishmenttype',
            name='is_considered',
            field=models.BooleanField(default=True, null=True),
        ),
        migrations.AddField(
            model_name='humangender',
            name='is_considered',
            field=models.BooleanField(default=True, null=True),
        ),
        migrations.AddField(
            model_name='meetingreason',
            name='is_considered',
            field=models.BooleanField(default=True, null=True),
        ),
        migrations.AddField(
            model_name='typemeeting',
            name='is_considered',
            field=models.BooleanField(default=True, null=True),
        ),
        migrations.AddField(
            model_name='undesirableeventfrequency',
            name='is_considered',
            field=models.BooleanField(default=True, null=True),
        ),
        migrations.AddField(
            model_name='undesirableeventnormaltype',
            name='is_considered',
            field=models.BooleanField(default=True, null=True),
        ),
        migrations.AddField(
            model_name='undesirableeventserioustype',
            name='is_considered',
            field=models.BooleanField(default=True, null=True),
        ),
        migrations.AddField(
            model_name='vehiclebrand',
            name='is_considered',
            field=models.BooleanField(default=True, null=True),
        ),
        migrations.AddField(
            model_name='vehiclemodel',
            name='is_considered',
            field=models.BooleanField(default=True, null=True),
        ),
    ]
