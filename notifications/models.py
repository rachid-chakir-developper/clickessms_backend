from django.db import models

# Create your models here.

NOTIF_TYPES_ALL = {
    "SYSTEM" : "SYSTEM",
    "ADDED_TO_TASK" : "ADDED_TO_TASK",
    "GO_TO_TASK" : "GO_TO_TASK",
    "TASK_STARTED" : "TASK_STARTED",
    "TASK_FINISHED" : "TASK_FINISHED",
}
class Notification(models.Model):
	NOTIF_TYPES = [
        ("SYSTEM", "Système"),
        ("ADDED_TO_TASK", "Affecté à une intérvention"),
        ("GO_TO_TASK", "Départ vers l'intérvention"),
        ("TASK_STARTED", "L'intérvention commencée"),
        ("TASK_FINISHED", "L'intérvention terminée")
    ]
	sender = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, related_name='notification_sender', null=True)
	recipient = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, related_name='notification_recipient', null=True)
	notification_type = models.CharField(max_length=50, choices=NOTIF_TYPES, default= "SYSTEM")
	title = models.CharField(max_length=255, null=True)
	message = models.TextField(null=True)
	is_read = models.BooleanField(default=False, null=True)
	is_seen = models.BooleanField(default=False, null=True)
	task = models.ForeignKey('works.Task', on_delete=models.SET_NULL, null=True)
	company = models.ForeignKey('companies.Company', on_delete=models.SET_NULL, related_name='company_notifications', null=True)
	created_at = models.DateTimeField(auto_now_add=True, null=True)
	updated_at = models.DateTimeField(auto_now=True, null=True)

	class Meta:
		ordering = ['-created_at']
		
	def __str__(self):
		return self.message