# Generated by Django 3.2.22 on 2024-12-30 10:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('human_ressources', '0063_alter_beneficiaryadmission_files'),
    ]

    operations = [
        migrations.AddField(
            model_name='beneficiaryadmission',
            name='status_reason',
            field=models.TextField(default='', null=True),
        ),
    ]
