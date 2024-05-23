# Generated by Django 3.2.22 on 2024-05-20 07:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('partnerships', '0006_financier'),
    ]

    operations = [
        migrations.AddField(
            model_name='financier',
            name='is_deleted',
            field=models.BooleanField(default=False, null=True),
        ),
        migrations.AddField(
            model_name='partner',
            name='is_deleted',
            field=models.BooleanField(default=False, null=True),
        ),
    ]