# Generated by Django 3.2.22 on 2024-02-21 16:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('feedbacks', '0005_auto_20240221_1708'),
    ]

    operations = [
        migrations.AlterField(
            model_name='signature',
            name='satisfaction',
            field=models.CharField(blank=True, choices=[('ANGRY', 'ANGRY'), ('CONFUSED', 'CONFUSED'), ('SMILE', 'SMILE'), ('KISS', 'KISS')], max_length=50, null=True),
        ),
    ]
