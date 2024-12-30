from django.db import models

# Create your models here.

NOTIF_TYPES_ALL = {
	"SYSTEM" : "SYSTEM",
	"TASK_ADDED": "TASK_ADDED",
	"TASK_UPDATED": "TASK_UPDATED",
	"TASK_PENDING": "TASK_PENDING",
	"TASK_APPROVED": "TASK_APPROVED",
	"TASK_REJECTED": "TASK_REJECTED",
	"ADDED_TO_TASK" : "ADDED_TO_TASK",
	"TASK_TO_DO" : "TASK_TO_DO",
	"GO_TO_TASK" : "GO_TO_TASK",
	"TASK_STARTED" : "TASK_STARTED",
	"TASK_IN_PROGRESS" : "TASK_IN_PROGRESS",
	"TASK_FINISHED" : "TASK_FINISHED",
	"TASK_COMPLETED" : "TASK_COMPLETED",
	"EI_ADDED": "EI_ADDED",
	"EI_UPDATED": "EI_UPDATED",
	"EI_NEW": "EI_NEW",
	"EI_IN_PROGRESS": "EI_IN_PROGRESS",
	"EI_DONE": "EI_DONE",
	"TASK_ACTION_ADDED": "TASK_ACTION_ADDED",
	"MEETING_DECISION_ADDED": "MEETING_DECISION_ADDED",
	"EMPLOYEE_ABSENCE_ADDED": "EMPLOYEE_ABSENCE_ADDED",
	"EMPLOYEE_ABSENCE_UPDATED": "EMPLOYEE_ABSENCE_UPDATED",
	"EMPLOYEE_ABSENCE_PENDING": "EMPLOYEE_ABSENCE_PENDING",
	"EMPLOYEE_ABSENCE_APPROVED": "EMPLOYEE_ABSENCE_APPROVED",
	"EMPLOYEE_ABSENCE_REJECTED": "EMPLOYEE_ABSENCE_REJECTED",
	"EXPENSE_ADDED": "EXPENSE_ADDED",
	"EXPENSE_UPDATED": "EXPENSE_UPDATED",
	"EXPENSE_PENDING": "EXPENSE_PENDING",
	"EXPENSE_APPROVED": "EXPENSE_APPROVED",
	"EXPENSE_REJECTED": "EXPENSE_REJECTED",
	"EXPENSE_PAID": "EXPENSE_PAID",
	"EXPENSE_UNPAID": "EXPENSE_UNPAID",
	"EXPENSE_REPORT_ADDED": "EXPENSE_REPORT_ADDED",
	"EXPENSE_REPORT_UPDATED": "EXPENSE_REPORT_UPDATED",
	"EXPENSE_REPORT_PENDING": "EXPENSE_REPORT_PENDING",
	"EXPENSE_REPORT_APPROVED": "EXPENSE_REPORT_APPROVED",
	"EXPENSE_REPORT_REJECTED": "EXPENSE_REPORT_REJECTED",
	"EXPENSE_REPORT_REIMBURSED": "EXPENSE_REPORT_REIMBURSED",
	"BENEFICIARY_ADMISSION_ADDED": "BENEFICIARY_ADMISSION_ADDED",
	"BENEFICIARY_ADMISSION_UPDATED": "BENEFICIARY_ADMISSION_UPDATED",
	"BENEFICIARY_ADMISSION_PENDING": "BENEFICIARY_ADMISSION_PENDING",
	"BENEFICIARY_ADMISSION_APPROVED": "BENEFICIARY_ADMISSION_APPROVED",
	"BENEFICIARY_ADMISSION_REJECTED": "BENEFICIARY_ADMISSION_REJECTED",
	"BENEFICIARY_ADMISSION_CANCELED": "BENEFICIARY_ADMISSION_CANCELED",
}
class Notification(models.Model):
	NOTIF_TYPES = [
		("SYSTEM", "Système"),
		("TASK_ADDED", "Nouvelle intervention ajoutée"),
		("TASK_UPDATED", "Intervention mise à jour"),
		("TASK_PENDING", "Intervention en attente de décision"),
		("TASK_APPROVED", "Intervention approuvée"),
		("TASK_REJECTED", "Intervention rejetée"),
		("ADDED_TO_TASK", "Affecté à une intérvention"),
		("TASK_TO_DO", "Affecté à une intérvention"),
		("GO_TO_TASK", "Départ vers l'intérvention"),
		("TASK_STARTED", "L'intérvention commencée"),
		("TASK_IN_PROGRESS", "L'intérvention commencée"),
		("TASK_FINISHED", "L'intérvention terminée"),
		("TASK_COMPLETED", "L'intérvention terminée"),
		("EI_ADDED", "Événement indésirable déclaré"),
		("EI_UPDATED", "Événement indésirable mise à jour"),
		("EI_NEW", "Événement indésirable remis comme déclaré"),
		("EI_IN_PROGRESS", "Événement indésirable en cours de traitement"),
		("EI_DONE", "Événement indésirable traité"),
		("TASK_ACTION_ADDED", "Affecté à une action"),
		("MEETING_DECISION_ADDED", "Affecté à une décision"),
		("EMPLOYEE_ABSENCE_ADDED", "Nouvelle demande de congé ajoutée"),
		("EMPLOYEE_ABSENCE_UPDATED", "Demande de congé mise à jour"),
		("EMPLOYEE_ABSENCE_PENDING", "Demande de congé en attente de décision"),
		("EMPLOYEE_ABSENCE_APPROVED", "Demande de congé approuvée"),
		("EMPLOYEE_ABSENCE_REJECTED", "Demande de congé rejetée"),
		("EXPENSE_ADDED", "Nouvelle demande de dépense ajoutée"),
		("EXPENSE_UPDATED", "Demande de dépense mise à jour"),
		("EXPENSE_PENDING", "Demande de dépense en attente d'approbation"),
		("EXPENSE_APPROVED", "Demande de dépense approuvée"),
		("EXPENSE_REJECTED", "Demande de dépense rejetée"),
		("EXPENSE_PAID", "Dépense payée."),
		("EXPENSE_UNPAID", "Dépense non payée."),
		("EXPENSE_REPORT_ADDED", "Nouvelle demande de remboursement de note de frais ajoutée"),
		("EXPENSE_REPORT_UPDATED", "Demande de remboursement de note de frais mise à jour"),
		("EXPENSE_REPORT_PENDING", "Demande de remboursement de note de frais en attente d'approbation"),
		("EXPENSE_REPORT_APPROVED", "Demande de remboursement de note de frais approuvée"),
		("EXPENSE_REPORT_REJECTED", "Demande de remboursement de note de frais rejetée"),
		("EXPENSE_REPORT_REIMBURSED", "Note de frais remboursée."),
		("BENEFICIARY_ADMISSION_ADDED", "Nouvelle demande d'admission ajoutée"),
		("BENEFICIARY_ADMISSION_UPDATED", "Demande d'admission mise à jour"),
		("BENEFICIARY_ADMISSION_PENDING", "Demande d'admission en attente"),
		("BENEFICIARY_ADMISSION_APPROVED", "Demande d'admission approuvée"),
		("BENEFICIARY_ADMISSION_REJECTED", "Demande d'admission rejetée"),
		("BENEFICIARY_ADMISSION_CANCELED", "Demande d'admission annulée"),

	]
	sender = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, related_name='notification_sender', null=True)
	recipient = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, related_name='notification_recipient', null=True)
	notification_type = models.CharField(max_length=50, choices=NOTIF_TYPES, default= "SYSTEM")
	title = models.CharField(max_length=255, null=True)
	message = models.TextField(null=True)
	is_read = models.BooleanField(default=False, null=True)
	is_seen = models.BooleanField(default=False, null=True)
	task = models.ForeignKey('works.Task', on_delete=models.SET_NULL, null=True)
	undesirable_event = models.ForeignKey('qualities.UndesirableEvent', on_delete=models.SET_NULL, null=True, related_name='notifications')
	task_action = models.ForeignKey('works.TaskAction', on_delete=models.SET_NULL, null=True, related_name='notifications')
	meeting_decision = models.ForeignKey('administratives.MeetingDecision', on_delete=models.SET_NULL, null=True, related_name='notifications')
	employee_absence = models.ForeignKey('planning.EmployeeAbsence', on_delete=models.SET_NULL, null=True, related_name='notifications')
	expense = models.ForeignKey('purchases.Expense', on_delete=models.SET_NULL, null=True, related_name='notifications')
	expense_report = models.ForeignKey('purchases.ExpenseReport', on_delete=models.SET_NULL, null=True, related_name='notifications')
	beneficiary_admission = models.ForeignKey('human_ressources.BeneficiaryAdmission', on_delete=models.SET_NULL, null=True, related_name='notifications')
	company = models.ForeignKey('companies.Company', on_delete=models.SET_NULL, related_name='company_notifications', null=True)
	created_at = models.DateTimeField(auto_now_add=True, null=True)
	updated_at = models.DateTimeField(auto_now=True, null=True)

	class Meta:
		ordering = ['-created_at']
		
	def __str__(self):
		return self.message

class MessageNotification(models.Model):
	MSG_NOTIF_TYPES = [
		('SYSTEM', 'Système'),
		('REMINDER', 'Rappel'),
		('MESSAGE', 'Message'),
		('TASK', 'Tâche'),
		('SCE', 'Cse'),
		('EVENT', 'Événement'),
		('NEWS', 'Actualités'),
		('WARNING', 'Avertissement'),
		('PROMOTION', 'Promotion'),
		('UPDATE', 'Mise à jour'),
		('FEEDBACK', 'Commentaires'),
		('ERROR', 'Erreur'),
	]
	message_notification_type = models.CharField(max_length=50, choices=MSG_NOTIF_TYPES, default= "SYSTEM")
	title = models.CharField(max_length=255, null=True)
	image = models.ForeignKey('medias.File', on_delete=models.SET_NULL, related_name='message_notifications', null=True)
	message = models.TextField(null=True)
	is_active = models.BooleanField(default=True, null=True)
	company = models.ForeignKey('companies.Company', on_delete=models.SET_NULL, related_name='message_notifications', null=True)
	creator = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, related_name='message_notifications', null=True)
	created_at = models.DateTimeField(auto_now_add=True, null=True)
	updated_at = models.DateTimeField(auto_now=True, null=True)

	class Meta:
		ordering = ['-created_at']

	@property
	def primary_color(self):
		colors = {
			'SYSTEM': '#808080',  # Gray 
			'REMINDER': '#0000FF',  # Blue 
			'MESSAGE': '#008000',  # Green 
			'TASK': '#FFA500',  # Orange 
			'SCE': '#800080',  # Purple 
			'EVENT': '#FFFF00',  # Yellow 
			'NEWS': '#00008B',  # DarkBlue 
			'WARNING': '#FF0000',  # Red 
			'PROMOTION': '#FFC0CB',  # Pink 
			'UPDATE': '#ADD8E6',  # LightBlue 
			'FEEDBACK': '#90EE90',  # LightGreen 
			'ERROR': '#8B0000',  # DarkRed
		}
		return colors.get(self.message_notification_type, '#808080')  # Default to gray
		
	def __str__(self):
		return self.title

class MessageNotificationEstablishment(models.Model):
	message_notification = models.ForeignKey(MessageNotification, on_delete=models.SET_NULL, null=True, related_name='establishments')
	establishment = models.ForeignKey('companies.Establishment', on_delete=models.SET_NULL, related_name='message_notification_establishments', null=True)
	creator = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, related_name='message_notification_establishments', null=True)
	created_at = models.DateTimeField(auto_now_add=True, null=True)
	updated_at = models.DateTimeField(auto_now=True, null=True)

class MessageNotificationUserStatus(models.Model):
	message_notification = models.ForeignKey(MessageNotification, on_delete=models.SET_NULL, null=True, related_name='message_notification_statuses')
	user = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, related_name='message_notification_statuses', null=True)
	is_read = models.BooleanField(default=False)
	read_at = models.DateTimeField(auto_now_add=True, null=True)
	created_at = models.DateTimeField(auto_now_add=True, null=True)
	updated_at = models.DateTimeField(auto_now=True, null=True)
	class Meta:
		unique_together = ('message_notification', 'user')