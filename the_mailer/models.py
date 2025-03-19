from django.db import models

# Create your models here.

class SentEmail(models.Model):
	STATUS_CHOICES = [
		('PENDING', 'En attente'),
		('SENT', 'Envoyé'),
		('FAILED', 'Échec'),
	]

	recipient = models.EmailField()  # Destinataire de l'email
	sender = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, related_name='sent_emails', null=True)
	subject = models.CharField(max_length=255)  # Objet de l'email
	body = models.TextField()  # Contenu de l'email
	status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')  # Statut de l'envoi
	error_message = models.TextField(null=True, blank=True)  # Message d'erreur en cas d'échec
	employee = models.ForeignKey('human_ressources.Employee', on_delete=models.SET_NULL, related_name='sent_emails', null=True)
	company = models.ForeignKey('companies.Company', on_delete=models.SET_NULL, related_name='company_sent_emails', null=True)
	creator = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, related_name='creator_sent_emails', null=True)
	is_deleted = models.BooleanField(default=False, null=True)
	created_at = models.DateTimeField(auto_now_add=True, null=True)
	updated_at = models.DateTimeField(auto_now=True, null=True)

	def __str__(self):
		return f"{self.subject} - {self.recipient}"