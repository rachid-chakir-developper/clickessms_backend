# Generated by Django 3.2.22 on 2024-02-01 09:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('medias', '0009_auto_20240130_1417'),
    ]

    operations = [
        migrations.AlterField(
            model_name='file',
            name='number',
            field=models.CharField(editable=False, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='folder',
            name='number',
            field=models.CharField(editable=False, max_length=255, null=True),
        ),
    ]
