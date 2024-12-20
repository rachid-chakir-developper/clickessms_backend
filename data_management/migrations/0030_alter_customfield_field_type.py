# Generated by Django 3.2.22 on 2024-10-21 10:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('data_management', '0029_alter_customfield_form_model'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customfield',
            name='field_type',
            field=models.CharField(choices=[('TEXT', 'Text'), ('NUMBER', 'Number'), ('DATETIME', 'Date'), ('DATETIME', 'Date et heure'), ('BOOLEAN', 'Boolean'), ('RADIO', 'Radio Button'), ('SELECT', 'Select'), ('CHECKBOX', 'Checkbox')], default='TEXT', max_length=50),
        ),
    ]
