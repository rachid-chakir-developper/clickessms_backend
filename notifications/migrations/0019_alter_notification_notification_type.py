# Generated by Django 3.2.22 on 2024-07-18 09:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('notifications', '0018_messagenotificationuserstatus'),
    ]

    operations = [
        migrations.AlterField(
            model_name='notification',
            name='notification_type',
            field=models.CharField(choices=[('SYSTEM', 'Système'), ('TASK_ADDED', 'Nouvelle intervention ajoutée'), ('TASK_UPDATED', 'Intervention mise à jour'), ('TASK_PENDING', 'Intervention en attente de décision'), ('TASK_APPROVED', 'Intervention approuvée'), ('TASK_REJECTED', 'Intervention rejetée'), ('ADDED_TO_TASK', 'Affecté à une intérvention'), ('TASK_TO_DO', 'Affecté à une intérvention'), ('GO_TO_TASK', "Départ vers l'intérvention"), ('TASK_STARTED', "L'intérvention commencée"), ('TASK_FINISHED', "L'intérvention terminée"), ('EI_ADDED', 'Événement indésirable déclaré'), ('EI_UPDATED', 'Événement indésirable mise à jour'), ('EI_NEW', 'Événement indésirable remis comme déclaré'), ('EI_IN_PROGRESS', 'Événement indésirable en cours de traitement'), ('EI_DONE', 'Événement indésirable traité'), ('TASK_ACTION_ADDED', 'Affecté à une action'), ('MEETING_DECISION_ADDED', 'Affecté à une décision'), ('EMPLOYEE_ABSENCE_ADDED', 'Nouvelle demande de congé ajoutée'), ('EMPLOYEE_ABSENCE_UPDATED', 'Demande de congé mise à jour'), ('EMPLOYEE_ABSENCE_PENDING', 'Demande de congé en attente de décision'), ('EMPLOYEE_ABSENCE_APPROVED', 'Demande de congé approuvée'), ('EMPLOYEE_ABSENCE_REJECTED', 'Demande de congé rejetée')], default='SYSTEM', max_length=50),
        ),
    ]
