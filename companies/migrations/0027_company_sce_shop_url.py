# Generated by Django 3.2.22 on 2024-09-20 15:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('companies', '0026_auto_20240530_1515'),
    ]

    operations = [
        migrations.AddField(
            model_name='company',
            name='sce_shop_url',
            field=models.URLField(max_length=255, null=True),
        ),
    ]