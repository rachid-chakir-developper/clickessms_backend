from django.db import models
from datetime import datetime
import random

STEP_TYPES_LABELS = ["BEFORE", "IN_PROGRESS", "AFTER"]
STEP_TYPES_ALL = {
    "BEFORE" : "BEFORE",
    "IN_PROGRESS" : "IN_PROGRESS",
    "AFTER" : "AFTER",
}
STATUS_All = []
# Create your models here.
class Task(models.Model):
	LEVELS = [
        ("EASY", "Facile"),#
        ("MEDIUM", "Moyen"),#
        ("HARD", "Difficile")#
    ]
	PRIORITIES = [
        ("LOW", "Faible"),#
        ("MEDIUM", "Moyenne"),#
        ("HIGH", "Haute")#
    ]
	STATUS = [
	    ("NEW", "À faire"),
	    ("PENDING", "En attente"),
	    ("APPROVED", "Approuvé"),
	    ("REJECTED", "Rejeté"),
	    ("TO_DO", "À fair"),
	    ("IN_PROGRESS", "En attente"),
	    ("COMPLETED", "Terminée"),
	    ("CANCELED", "Annulée"),
	    ("ARCHIVED", "Archivée")
	]
	number = models.CharField(max_length=255, editable=False, null=True)
	name = models.CharField(max_length=255, null=True)
	starting_date_time = models.DateTimeField(null=True)
	ending_date_time = models.DateTimeField(null=True)
	started_at = models.DateTimeField(null=True)
	finished_at = models.DateTimeField(null=True)
	latitude = models.CharField(max_length=255, null=True)
	longitude = models.CharField(max_length=255, null=True)
	city = models.CharField(max_length=255, null=True)
	country = models.CharField(max_length=255, null=True)
	zip_code = models.CharField(max_length=255, null=True)
	address = models.TextField(default='', null=True)
	additional_address = models.TextField(default='', null=True)
	# receiver infos start
	receiver_name = models.CharField(max_length=255, null=True)
	receiver_tel = models.CharField(max_length=255, null=True)
	receiver_email = models.EmailField(max_length=254, null=True)
	# ****************************
	# Intérvenant Véhicules matérails infos start
	workers_infos = models.TextField(default='', null=True)
	vehicles_infos = models.TextField(default='', null=True)
	materials_infos = models.TextField(default='', null=True)
	# ****************************
	comment = models.TextField(default='', null=True)
	description = models.TextField(default='', null=True)
	observation = models.TextField(default='', null=True)
	is_active = models.BooleanField(default=True, null=True)
	priority = models.CharField(max_length=50, choices=PRIORITIES, default= "LOW")
	work_level = models.CharField(max_length=50, choices=LEVELS, default= "MEDIUM")
	status = models.CharField(max_length=50, choices=STATUS, default= "NEW")
	employee = models.ForeignKey('human_ressources.Employee', on_delete=models.SET_NULL, related_name='employee_tasks', null=True)
	folder = models.ForeignKey('medias.Folder', on_delete=models.SET_NULL, null=True)
	company = models.ForeignKey('companies.Company', on_delete=models.SET_NULL, related_name='tasks', null=True)
	creator = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True)
	is_deleted = models.BooleanField(default=False, null=True)
	created_at = models.DateTimeField(auto_now_add=True, null=True)
	updated_at = models.DateTimeField(auto_now=True, null=True)
	
	def save(self, *args, **kwargs):
		# Générer le numéro unique lors de la sauvegarde si ce n'est pas déjà défini
		if not self.number:
			self.number = self.generate_unique_number()

		super(Task, self).save(*args, **kwargs)

	def generate_unique_number(self):
		# Implémentez la logique de génération du numéro unique ici
		# Vous pouvez utiliser des combinaisons de date, heure, etc.
		# par exemple, en utilisant la fonction strftime de l'objet datetime
		# pour générer une chaîne basée sur la date et l'heure actuelles.

		# Exemple : Utilisation de la date et de l'heure actuelles
		current_time = datetime.now()
		number_suffix = current_time.strftime("%Y%m%d%H%M%S")
		# number_prefix = ''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ', k=2))  # Ajoutez 3 lettres au début
		number_prefix = 'IN' # Ajoutez 3 lettres au début
		number = f'{number_prefix}{number_suffix}'

		# Vérifier s'il est unique dans la base de données
		while Task.objects.filter(number=number).exists():
			number_suffix = current_time.strftime("%Y%m%d%H%M%S")
			number = f'{number_prefix}{number_suffix}'

		return number

	def __str__(self):
		return self.name

# Create your models here.
class TaskEstablishment(models.Model):
	task = models.ForeignKey(Task, on_delete=models.SET_NULL, null=True, related_name='establishments')
	establishment = models.ForeignKey('companies.Establishment', on_delete=models.SET_NULL, related_name='task_establishments', null=True)
	creator = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, related_name='task_establishments', null=True)
	created_at = models.DateTimeField(auto_now_add=True, null=True)
	updated_at = models.DateTimeField(auto_now=True, null=True)

# Create your models here.
class TaskWorker(models.Model):
	task = models.ForeignKey(Task, on_delete=models.SET_NULL, null=True, related_name='workers')
	employee = models.ForeignKey('human_ressources.Employee', on_delete=models.SET_NULL, related_name='task_employee', null=True)
	creator = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, related_name='task_worker_former', null=True)
	created_at = models.DateTimeField(auto_now_add=True, null=True)
	updated_at = models.DateTimeField(auto_now=True, null=True)

	def __str__(self):
		return str(self.id)

# Create your models here.
class TaskMaterial(models.Model):
	task = models.ForeignKey(Task, on_delete=models.SET_NULL, null=True, related_name='materials')
	material = models.ForeignKey('stocks.Material', on_delete=models.SET_NULL, null=True)
	quantity = models.IntegerField(null=True)
	creator = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True)
	created_at = models.DateTimeField(auto_now_add=True, null=True)
	updated_at = models.DateTimeField(auto_now=True, null=True)

	def __str__(self):
		return str(self.id)

# Create your models here.
class TaskVehicle(models.Model):
	task = models.ForeignKey(Task, on_delete=models.SET_NULL, null=True, related_name='vehicles')
	vehicle = models.ForeignKey('vehicles.Vehicle', on_delete=models.SET_NULL, null=True)
	creator = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True)
	created_at = models.DateTimeField(auto_now_add=True, null=True)
	updated_at = models.DateTimeField(auto_now=True, null=True)

	def __str__(self):
		return str(self.id)

# Create your models here.
class TaskChecklistItem(models.Model):
	STATUS = [
	    ("NEW", "À faire"),
	    ("STARTED", "En cours"),
	    ("FINISHED", "Terminée"),
	    ("PENDING", "En attente"),
	    ("CANCELED", "Annulée"),
	    ("ARCHIVED", "Archivée")
	]
	number = models.CharField(max_length=255, null=True)
	name = models.CharField(max_length=255, null=True)
	localisation = models.CharField(max_length=255, null=True)
	comment = models.TextField(default='', null=True)
	description = models.TextField(default='', null=True)
	observation = models.TextField(default='', null=True)
	task = models.ForeignKey(Task, on_delete=models.SET_NULL, null=True, related_name='task_checklist')
	status = models.CharField(max_length=50, choices=STATUS, default= "NEW")
	is_active = models.BooleanField(default=True, null=True)
	creator = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True)
	created_at = models.DateTimeField(auto_now_add=True, null=True)
	updated_at = models.DateTimeField(auto_now=True, null=True)

	def __str__(self):
		return self.name

# Create your models here.
class TaskStep(models.Model):
	STATUS = [
	    ("NEW", "À faire"),
	    ("STARTED", "En cours"),
	    ("FINISHED", "Terminée"),
	    ("PENDING", "En attente"),
	    ("CANCELED", "Annulée"),
	    ("ARCHIVED", "Archivée")
	]
	STEP_TYPES = [
        ("BEFORE", "Avant"),
        ("IN_PROGRESS", "En cours"),
        ("AFTER", "Après")
    ]
	name = models.CharField(max_length=255, null=True)
	task = models.ForeignKey(Task, on_delete=models.SET_NULL, null=True, related_name='task_steps')
	step_type = models.CharField(max_length=50, choices=STEP_TYPES, default= "BEFORE")
	status = models.CharField(max_length=50, choices=STATUS, default= "PENDING")
	images = models.ManyToManyField('medias.File', related_name='task_step_images')
	videos = models.ManyToManyField('medias.File', related_name='task_step_videos')
	comments = models.ManyToManyField('feedbacks.Comment', related_name='task_step')
	creator = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True)
	created_at = models.DateTimeField(auto_now_add=True, null=True)
	updated_at = models.DateTimeField(auto_now=True, null=True)

	def __str__(self):
		return self.name

class Ticket(models.Model):
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
	establishments = models.ManyToManyField('companies.Establishment', related_name='tickets')
	priority = models.CharField(max_length=50, choices=PRIORITIES, default= "LOW")
	status = models.CharField(max_length=50, choices=STATUS, default= "NEW")
	comments = models.ManyToManyField('feedbacks.Comment', related_name='tickets')
	employee = models.ForeignKey('human_ressources.Employee', on_delete=models.SET_NULL, related_name='tickets', null=True)
	is_active = models.BooleanField(default=False, null=True)
	undesirable_event = models.ForeignKey('qualities.UndesirableEvent', on_delete=models.SET_NULL, null=True, related_name='tickets')
	is_have_efc_report = models.BooleanField(default=False, null=False)
	folder = models.ForeignKey('medias.Folder', on_delete=models.SET_NULL, null=True)
	company = models.ForeignKey('companies.Company', on_delete=models.SET_NULL, related_name='tickets', null=True)
	creator = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, related_name='tickets', null=True)
	is_deleted = models.BooleanField(default=False, null=True)
	created_at = models.DateTimeField(auto_now_add=True, null=True)
	updated_at = models.DateTimeField(auto_now=True, null=True)
    
	def save(self, *args, **kwargs):
	    # Générer le numéro unique lors de la sauvegarde si ce n'est pas déjà défini
	    if not self.number:
	        self.number = self.generate_unique_number()

	    super(Ticket, self).save(*args, **kwargs)

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
	    while Ticket.objects.filter(number=number).exists():
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

	@property
	def efc_report(self):
		return self.efc_reports.first()
	    
	def __str__(self):
		return self.title

class EfcReport(models.Model):
	number = models.CharField(max_length=255, editable=False, null=True)
	title = models.CharField(max_length=255, null=True)
	description = models.TextField(default='', null=True)
	document = models.ForeignKey("medias.File",on_delete=models.SET_NULL,related_name="efc_reports", null=True)
	efc_date = models.DateTimeField(null=True)
	declaration_date = models.DateTimeField(null=True)
	employees = models.ManyToManyField('human_ressources.Employee', related_name='efc_reports')
	ticket = models.ForeignKey(Ticket, on_delete=models.SET_NULL, null=True, related_name='efc_reports')
	company = models.ForeignKey('companies.Company', on_delete=models.SET_NULL, related_name='efc_reports', null=True)
	creator = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, related_name='efc_reports', null=True)
	created_at = models.DateTimeField(auto_now_add=True, null=True)
	updated_at = models.DateTimeField(auto_now=True, null=True)

class TaskAction(models.Model):
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
	ticket = models.ForeignKey(Ticket, on_delete=models.SET_NULL, null=True, related_name='actions')
	description = models.TextField(default='', null=True)
	document = models.ForeignKey("medias.File",on_delete=models.SET_NULL,related_name="task_actions", null=True)
	due_date = models.DateTimeField(null=True)
	employees = models.ManyToManyField('human_ressources.Employee', related_name='task_actions')
	status = models.CharField(max_length=50, choices=STATUS, default= "TO_DO")
	folder = models.ForeignKey('medias.Folder', on_delete=models.SET_NULL, null=True)
	company = models.ForeignKey('companies.Company', on_delete=models.SET_NULL, related_name='task_actions', null=True)
	creator = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, related_name='task_actions', null=True)
	created_at = models.DateTimeField(auto_now_add=True, null=True)
	updated_at = models.DateTimeField(auto_now=True, null=True)
    
	def save(self, *args, **kwargs):
	    # Générer le numéro unique lors de la sauvegarde si ce n'est pas déjà défini
	    if not self.number:
	        self.number = self.generate_unique_number()

	    super(TaskAction, self).save(*args, **kwargs)

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
	    while TaskAction.objects.filter(number=number).exists():
	        number_suffix = current_time.strftime("%Y%m%d%H%M%S")
	        number = f'{number_prefix}{number_suffix}'

	    return number

	def __str__(self):
		return str(self.action)