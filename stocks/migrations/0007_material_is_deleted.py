# Generated by Django 3.2.22 on 2024-05-20 07:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stocks', '0006_material_folder'),
    ]

    operations = [
        migrations.AddField(
            model_name='material',
            name='is_deleted',
            field=models.BooleanField(default=False, null=True),
        ),
    ]
