# Generated by Django 3.2.22 on 2023-12-13 10:25

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('medias', '0005_auto_20231213_1125'),
        ('human_ressources', '0007_auto_20231208_1047'),
    ]

    operations = [
        migrations.AddField(
            model_name='employee',
            name='folder',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='medias.folder'),
        ),
    ]
