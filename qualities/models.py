from django.db import models
from datetime import datetime
import random

# Create your models here.
class UndesirableEvent(models.Model):
	STATUS = [
	    ("NEW", "Nouveau"),
	    ("ACCEPTED", "Accepté"),
	    ("REFUSED", "Refusé"),
	    ("IN_PROGRESS", "En cours"),
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
	other_notified_persons = models.CharField(max_length=255, null=True)
	folder = models.ForeignKey('medias.Folder', on_delete=models.SET_NULL, null=True)
	status = models.CharField(max_length=50, choices=STATUS, default= "NEW")
	normal_types = models.ManyToManyField('data_management.UndesirableEventNormalType', related_name='normal_type_undesirable_events')
	serious_types = models.ManyToManyField('data_management.UndesirableEventSeriousType', related_name='serious_type_undesirable_events')
	frequency = models.ForeignKey('data_management.UndesirableEventFrequency', on_delete=models.SET_NULL, related_name='frequency_undesirable_events', null=True)
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
		total_objectives = self.objectives.count()
		if total_objectives == 0:
			return 0
		total_completion = sum(obj.completion_percentage for obj in self.objectives.all())
		return round(total_completion / total_objectives, 2)
	    
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

class ActionPlanObjective(models.Model):
	STATUS = [
	    ("NEW", "Nouveau"),
	    ("ACCEPTED", "Accepté"),
	    ("REFUSED", "Refusé"),
	    ("IN_PROGRESS", "En cours"),
	    ("COMPLETED", "Terminée"),
	    ("ON_HOLD", "En attente"),
	    ("CANCELED", "Annulée"),
	    ("ARCHIVED", "Archivée")
	]
	PRIORITIES = [
	    ("LOW", "Faible"),#
	    ("MEDIUM", "Moyenne"),#
	    ("HIGH", "Haute")#
	]
	number = models.CharField(max_length=255, editable=False, null=True)
	title = models.CharField(max_length=255, null=True)
	description = models.TextField(default='', null=True)
	establishments = models.ManyToManyField('companies.Establishment', related_name='action_plan_objectives')
	priority = models.CharField(max_length=50, choices=PRIORITIES, default= "LOW")
	status = models.CharField(max_length=50, choices=STATUS, default= "NEW")
	employee = models.ForeignKey('human_ressources.Employee', on_delete=models.SET_NULL, related_name='action_plan_objectives', null=True)
	is_active = models.BooleanField(default=False, null=True)
	undesirable_event = models.ForeignKey(UndesirableEvent, on_delete=models.SET_NULL, null=True, related_name='objectives')
	folder = models.ForeignKey('medias.Folder', on_delete=models.SET_NULL, null=True)
	company = models.ForeignKey('companies.Company', on_delete=models.SET_NULL, related_name='action_plan_objectives', null=True)
	creator = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, related_name='action_plan_objectives', null=True)
	is_deleted = models.BooleanField(default=False, null=True)
	created_at = models.DateTimeField(auto_now_add=True, null=True)
	updated_at = models.DateTimeField(auto_now=True, null=True)
    
	def save(self, *args, **kwargs):
	    # Générer le numéro unique lors de la sauvegarde si ce n'est pas déjà défini
	    if not self.number:
	        self.number = self.generate_unique_number()

	    super(ActionPlanObjective, self).save(*args, **kwargs)

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
	    while ActionPlanObjective.objects.filter(number=number).exists():
	        number_suffix = current_time.strftime("%Y%m%d%H%M%S")
	        number = f'{number_prefix}{number_suffix}'

	    return number

	@property
	def completion_percentage(self):
		total_actions = self.actions.count()
		if total_actions == 0:
			return 0
		completed_actions = self.actions.filter(status="DONE").count()
		percentage = (completed_actions / total_actions) * 100
		return round(percentage, 2)
	    
	def __str__(self):
		return self.title

class ActionPlanAction(models.Model):
	STATUS = [
	    ("TO_DO", "À traiter"),
	    ("IN_PROGRESS", "En cours"),
	    ("DONE", "Traité")
	]
	PRIORITIES = [
	    ("LOW", "Faible"),#
	    ("MEDIUM", "Moyenne"),#
	    ("HIGH", "Haute")#
	]
	number = models.CharField(max_length=255, editable=False, null=True)
	action_plan_objective = models.ForeignKey(ActionPlanObjective, on_delete=models.SET_NULL, null=True, related_name='actions')
	action = models.TextField(default='', null=True)
	document = models.ForeignKey("medias.File",on_delete=models.SET_NULL,related_name="action_plan_actions", null=True)
	due_date = models.DateTimeField(null=True)
	employees = models.ManyToManyField('human_ressources.Employee', related_name='action_plan_actions')
	status = models.CharField(max_length=50, choices=STATUS, default= "TO_DO")
	folder = models.ForeignKey('medias.Folder', on_delete=models.SET_NULL, null=True)
	company = models.ForeignKey('companies.Company', on_delete=models.SET_NULL, related_name='action_plan_actions', null=True)
	creator = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, related_name='action_plan_actions', null=True)
	created_at = models.DateTimeField(auto_now_add=True, null=True)
	updated_at = models.DateTimeField(auto_now=True, null=True)
    
	def save(self, *args, **kwargs):
	    # Générer le numéro unique lors de la sauvegarde si ce n'est pas déjà défini
	    if not self.number:
	        self.number = self.generate_unique_number()

	    super(ActionPlanAction, self).save(*args, **kwargs)

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
	    while ActionPlanAction.objects.filter(number=number).exists():
	        number_suffix = current_time.strftime("%Y%m%d%H%M%S")
	        number = f'{number_prefix}{number_suffix}'

	    return number

	def __str__(self):
		return str(self.action)