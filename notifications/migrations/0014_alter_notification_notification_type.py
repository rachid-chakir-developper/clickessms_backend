# Generated by Django 3.2.22 on 2024-07-01 14:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('notifications', '0013_notification_task_action'),
    ]

    operations = [
        migrations.AlterField(
            model_name='notification',
            name='notification_type',
            field=models.CharField(choices=[('SYSTEM', 'Système'), ('ADDED_TO_TASK', 'Affecté à une intérvention'), ('GO_TO_TASK', "Départ vers l'intérvention"), ('TASK_STARTED', "L'intérvention commencée"), ('TASK_FINISHED', "L'intérvention terminée"), ('EI_ADDED', 'Événement indésirable déclaré'), ('TASK_ACTION_ADDED', 'Affecté à une action')], default='SYSTEM', max_length=50),
        ),
    ]
