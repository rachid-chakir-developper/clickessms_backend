# Generated by Django 3.2.22 on 2024-06-10 14:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('qualities', '0030_auto_20240610_1217'),
    ]

    operations = [
        migrations.AddField(
            model_name='actionplanobjective',
            name='number',
            field=models.CharField(editable=False, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='actionplanobjective',
            name='title',
            field=models.CharField(max_length=255, null=True),
        ),
    ]