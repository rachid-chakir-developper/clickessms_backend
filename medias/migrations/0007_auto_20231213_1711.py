# Generated by Django 3.2.22 on 2023-12-13 16:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('medias', '0006_rename_descreption_folder_description'),
    ]

    operations = [
        migrations.AddField(
            model_name='file',
            name='description',
            field=models.TextField(default='', null=True),
        ),
        migrations.AddField(
            model_name='file',
            name='observation',
            field=models.TextField(default='', null=True),
        ),
        migrations.AlterField(
            model_name='folder',
            name='description',
            field=models.TextField(default='', null=True),
        ),
        migrations.AlterField(
            model_name='folder',
            name='observation',
            field=models.TextField(default='', null=True),
        ),
    ]
