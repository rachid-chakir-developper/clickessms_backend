# Generated by Django 3.2.22 on 2024-12-03 15:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('data_management', '0037_auto_20241203_1632'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='accountingnature',
            options={'ordering': ['code']},
        ),
        migrations.AddField(
            model_name='accountingnature',
            name='ending_date',
            field=models.DateField(null=True),
        ),
        migrations.AddField(
            model_name='accountingnature',
            name='starting_date',
            field=models.DateField(null=True),
        ),
    ]