# Generated by Django 3.2.22 on 2024-05-30 10:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vehicles', '0010_auto_20240530_1237'),
    ]

    operations = [
        migrations.AlterField(
            model_name='vehicle',
            name='crit_air_vignette',
            field=models.CharField(blank=True, choices=[('ZERO', '0'), ('ONE', '1'), ('TWO', '2'), ('THREE', '3'), ('FOUR', '4'), ('FIVE', '5')], max_length=50, null=True),
        ),
    ]