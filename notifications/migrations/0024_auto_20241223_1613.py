# Generated by Django 3.2.22 on 2024-12-23 15:13

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('purchases', '0037_expensereport'),
        ('notifications', '0023_notification_expense'),
    ]

    operations = [
        migrations.AddField(
            model_name='notification',
            name='expense_report',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='notifications', to='purchases.expensereport'),
        ),
        migrations.AlterField(
            model_name='notification',
            name='notification_type',
            field=models.CharField(choices=[('SYSTEM', 'Système'), ('TASK_ADDED', 'Nouvelle intervention ajoutée'), ('TASK_UPDATED', 'Intervention mise à jour'), ('TASK_PENDING', 'Intervention en attente de décision'), ('TASK_APPROVED', 'Intervention approuvée'), ('TASK_REJECTED', 'Intervention rejetée'), ('ADDED_TO_TASK', 'Affecté à une intérvention'), ('TASK_TO_DO', 'Affecté à une intérvention'), ('GO_TO_TASK', "Départ vers l'intérvention"), ('TASK_STARTED', "L'intérvention commencée"), ('TASK_IN_PROGRESS', "L'intérvention commencée"), ('TASK_FINISHED', "L'intérvention terminée"), ('TASK_COMPLETED', "L'intérvention terminée"), ('EI_ADDED', 'Événement indésirable déclaré'), ('EI_UPDATED', 'Événement indésirable mise à jour'), ('EI_NEW', 'Événement indésirable remis comme déclaré'), ('EI_IN_PROGRESS', 'Événement indésirable en cours de traitement'), ('EI_DONE', 'Événement indésirable traité'), ('TASK_ACTION_ADDED', 'Affecté à une action'), ('MEETING_DECISION_ADDED', 'Affecté à une décision'), ('EMPLOYEE_ABSENCE_ADDED', 'Nouvelle demande de congé ajoutée'), ('EMPLOYEE_ABSENCE_UPDATED', 'Demande de congé mise à jour'), ('EMPLOYEE_ABSENCE_PENDING', 'Demande de congé en attente de décision'), ('EMPLOYEE_ABSENCE_APPROVED', 'Demande de congé approuvée'), ('EMPLOYEE_ABSENCE_REJECTED', 'Demande de congé rejetée'), ('EXPENSE_ADDED', 'Nouvelle demande de dépense ajoutée'), ('EXPENSE_UPDATED', 'Demande de dépense mise à jour'), ('EXPENSE_PENDING', "Demande de dépense en attente d'approbation"), ('EXPENSE_APPROVED', 'Demande de dépense approuvée'), ('EXPENSE_REJECTED', 'Demande de dépense rejetée'), ('EXPENSE_PAID', 'Dépense payée.'), ('EXPENSE_UNPAID', 'Dépense non payée.'), ('EXPENSE_REPORT_ADDED', 'Nouvelle demande de remboursement de note de frais ajoutée'), ('EXPENSE_REPORT_UPDATED', 'Demande de remboursement de note de frais mise à jour'), ('EXPENSE_REPORT_PENDING', "Demande de remboursement de note de frais en attente d'approbation"), ('EXPENSE_REPORT_APPROVED', 'Demande de remboursement de note de frais approuvée'), ('EXPENSE_REPORT_REJECTED', 'Demande de remboursement de note de frais rejetée'), ('EXPENSE_REPORT_REIMBURSED', 'note de frais remboursée.')], default='SYSTEM', max_length=50),
        ),
    ]
