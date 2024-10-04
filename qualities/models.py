from django.db import models
from datetime import datetime
import random

# Create your models here.
class UndesirableEvent(models.Model):
	STATUS = [
	    ("DRAFT", "Brouillon"),
	    ("NEW", "Déclaré"),
	    ("IN_PROGRESS", "En cours"),
	    ("DONE", "Traité"),
	    ("ACCEPTED", "Accepté"),
	    ("REFUSED", "Refusé"),
	    ("COMPLETED", "Terminée"),
	    ("ON_HOLD", "En attente"),
	    ("CANCELED", "Annulée"),
	    ("ARCHIVED", "Archivée")
	]
	UDESIRABLE_EVENT_TYPES = [
        ("NORMAL", "EVENEMENT INDESIRABLE (EI) - Normal"),
        ("SERIOUS", "EVENEMENT INDESIRABLE GRAVE (EIG) - Grave"),
    ]
	UDESIRABLE_EVENT_SEVERITY = [
        ("LOW", "Faible"),
        ("MEDIUM", "Moyenne"),
        ("SEVERE", "Grave"),
        ("VERY_SERIOUS", "Très grave"),
    ]
	number = models.CharField(max_length=255, editable=False, null=True)
	title = models.CharField(max_length=255, null=True)
	undesirable_event_type = models.CharField(max_length=50, choices=UDESIRABLE_EVENT_TYPES, default= "NORMAL", null=True)
	severity = models.CharField(max_length=50, choices=UDESIRABLE_EVENT_SEVERITY, default= "MEDIUM", null=True)
	image = models.ForeignKey('medias.File', on_delete=models.SET_NULL, related_name='undesirable_event_image', null=True)
	starting_date_time = models.DateTimeField(null=True)
	ending_date_time = models.DateTimeField(null=True)
	actions_taken_text = models.TextField(default='', null=True)
	course_facts_date_time = models.DateTimeField(null=True)
	course_facts_place = models.CharField(max_length=255, null=True)
	circumstance_event_text = models.TextField(default='', null=True)
	description = models.TextField(default='', null=True)
	observation = models.TextField(default='', null=True)
	is_active = models.BooleanField(default=True, null=True)
	other_notified_persons = models.TextField(default='', null=True)
	concerned_families = models.TextField(default='', null=True)
	files = models.ManyToManyField('medias.File', related_name='file_undesirable_events')
	folder = models.ForeignKey('medias.Folder', on_delete=models.SET_NULL, null=True)
	status = models.CharField(max_length=50, choices=STATUS, default= "DRAFT")
	other_types = models.TextField(default='', null=True)
	normal_types = models.ManyToManyField('data_management.UndesirableEventNormalType', related_name='normal_type_undesirable_events')
	serious_types = models.ManyToManyField('data_management.UndesirableEventSeriousType', related_name='serious_type_undesirable_events')
	frequency = models.ForeignKey('data_management.UndesirableEventFrequency', on_delete=models.SET_NULL, related_name='frequency_undesirable_events', null=True)
	call = models.ForeignKey('administratives.Call', on_delete=models.SET_NULL, null=True, related_name='undesirable_events')
	employee = models.ForeignKey('human_ressources.Employee', on_delete=models.SET_NULL, related_name='employee_undesirable_events', null=True)
	company = models.ForeignKey('companies.Company', on_delete=models.SET_NULL, related_name='company_undesirable_events', null=True)
	creator = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True)
	is_deleted = models.BooleanField(default=False, null=True)
	created_at = models.DateTimeField(auto_now_add=True, null=True)
	updated_at = models.DateTimeField(auto_now=True, null=True)
    
	def save(self, *args, **kwargs):
	    # Générer le numéro unique lors de la sauvegarde si ce n'est pas déjà défini
	    if not self.number:
	        self.number = self.generate_unique_number()

	    super(UndesirableEvent, self).save(*args, **kwargs)

	def generate_unique_number(self):
	    # Implémentez la logique de génération du numéro unique ici
	    # Vous pouvez utiliser des combinaisons de date, heure, etc.
	    # par exemple, en utilisant la fonction strftime de l'objet datetime
	    # pour générer une chaîne basée sur la date et l'heure actuelles.

	    # Exemple : Utilisation de la date et de l'heure actuelles
	    current_time = datetime.now()
	    number_suffix = current_time.strftime("%Y%m%d%H%M%S")
	    number_prefix = ''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ', k=2))  # Ajoutez 3 lettres au début
	    number = f'{number_prefix}{number_suffix}'

	    # Vérifier s'il est unique dans la base de données
	    while UndesirableEvent.objects.filter(number=number).exists():
	        number_suffix = current_time.strftime("%Y%m%d%H%M%S")
	        number = f'{number_prefix}{number_suffix}'

	    return number

	@property
	def completion_percentage(self):
		total_tickets = self.tickets.count()
		if total_tickets == 0:
			return 0
		total_completion = sum(obj.completion_percentage for obj in self.tickets.all())
		return round(total_completion / total_tickets, 2)
	    
	def __str__(self):
		return self.title

# Create your models here.
class UndesirableEventEstablishment(models.Model):
	undesirable_event = models.ForeignKey(UndesirableEvent, on_delete=models.SET_NULL, null=True, related_name='establishments')
	establishment = models.ForeignKey('companies.Establishment', on_delete=models.SET_NULL, related_name='undesirable_event_establishments', null=True)
	creator = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, related_name='undesirable_event_establishments', null=True)
	created_at = models.DateTimeField(auto_now_add=True, null=True)
	updated_at = models.DateTimeField(auto_now=True, null=True)

	def __str__(self):
		return str(self.id)

# Create your models here.
class UndesirableEventEmployee(models.Model):
	undesirable_event = models.ForeignKey(UndesirableEvent, on_delete=models.SET_NULL, null=True, related_name='employees')
	employee = models.ForeignKey('human_ressources.Employee', on_delete=models.SET_NULL, related_name='undesirable_event_employees', null=True)
	creator = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, related_name='undesirable_event_employees', null=True)
	created_at = models.DateTimeField(auto_now_add=True, null=True)
	updated_at = models.DateTimeField(auto_now=True, null=True)

	def __str__(self):
		return str(self.id)

# Create your models here.
class UndesirableEventBeneficiary(models.Model):
	undesirable_event = models.ForeignKey(UndesirableEvent, on_delete=models.SET_NULL, null=True, related_name='beneficiaries')
	beneficiary = models.ForeignKey('human_ressources.Beneficiary', on_delete=models.SET_NULL, related_name='undesirable_event_beneficiaries', null=True)
	creator = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, related_name='undesirable_event_beneficiaries', null=True)
	created_at = models.DateTimeField(auto_now_add=True, null=True)
	updated_at = models.DateTimeField(auto_now=True, null=True)

	def __str__(self):
		return str(self.id)

# Create your models here.
class UndesirableEventNotifiedPerson(models.Model):
	undesirable_event = models.ForeignKey(UndesirableEvent, on_delete=models.SET_NULL, null=True, related_name='notified_persons')
	employee = models.ForeignKey('human_ressources.Employee', on_delete=models.SET_NULL, related_name='undesirable_event_notified_persons', null=True)
	creator = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, related_name='undesirable_event_notified_persons', null=True)
	created_at = models.DateTimeField(auto_now_add=True, null=True)
	updated_at = models.DateTimeField(auto_now=True, null=True)

	def __str__(self):
		return str(self.id)