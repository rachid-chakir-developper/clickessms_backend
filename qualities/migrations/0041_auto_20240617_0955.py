# Generated by Django 3.2.22 on 2024-06-17 07:55

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('qualities', '0040_auto_20240617_0934'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='ticket',
            name='company',
        ),
        migrations.RemoveField(
            model_name='ticket',
            name='creator',
        ),
        migrations.RemoveField(
            model_name='ticket',
            name='employee',
        ),
        migrations.RemoveField(
            model_name='ticket',
            name='establishments',
        ),
        migrations.RemoveField(
            model_name='ticket',
            name='folder',
        ),
        migrations.RemoveField(
            model_name='ticket',
            name='undesirable_event',
        ),
        migrations.DeleteModel(
            name='TaskAction',
        ),
        migrations.DeleteModel(
            name='Ticket',
        ),
    ]