# Generated by Django 3.2.22 on 2024-06-13 11:40

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('medias', '0011_file_company'),
        ('companies', '0026_auto_20240530_1515'),
        ('qualities', '0035_auto_20240613_1203'),
    ]

    operations = [
        migrations.AddField(
            model_name='actionplanaction',
            name='company',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='action_plan_actions', to='companies.company'),
        ),
        migrations.AddField(
            model_name='actionplanaction',
            name='folder',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='medias.folder'),
        ),
    ]
