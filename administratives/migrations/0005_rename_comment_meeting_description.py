# Generated by Django 3.2.22 on 2024-03-28 10:54

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('administratives', '0004_beneficiarymeetingitem_meeting'),
    ]

    operations = [
        migrations.RenameField(
            model_name='meeting',
            old_name='comment',
            new_name='description',
        ),
    ]