# Generated by Django 3.2.22 on 2024-05-20 14:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0012_remove_usercompany_is_deleted'),
    ]

    operations = [
        migrations.AddField(
            model_name='device',
            name='is_deleted',
            field=models.BooleanField(default=False, null=True),
        ),
    ]
