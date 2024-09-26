# Generated by Django 3.2.22 on 2024-09-26 13:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('medias', '0011_file_company'),
        ('blog', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='files',
            field=models.ManyToManyField(related_name='file_posts', to='medias.File'),
        ),
    ]
