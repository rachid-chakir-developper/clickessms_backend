# Generated by Django 3.2.22 on 2024-05-30 10:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vehicles', '0009_auto_20240530_1211'),
    ]

    operations = [
        migrations.AddField(
            model_name='vehicle',
            name='crit_air_vignette',
            field=models.CharField(choices=[('0', '0'), ('1', '1'), ('2', '2'), ('3', '3'), ('4', '4'), ('5', '5')], max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='vehicle',
            name='state',
            field=models.CharField(choices=[('NEW', 'Neuf'), ('GOOD', 'Correct'), ('BAD', 'Mauvais')], default='GOOD', max_length=50, null=True),
        ),
    ]
