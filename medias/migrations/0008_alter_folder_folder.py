# Generated by Django 3.2.22 on 2023-12-13 16:27

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('medias', '0007_auto_20231213_1711'),
    ]

    operations = [
        migrations.AlterField(
            model_name='folder',
            name='folder',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='children_folders', to='medias.folder'),
        ),
    ]
