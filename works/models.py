from django.db import models
from datetime import datetime
import random

STEP_TYPES_LABELS = ["BEFORE", "IN_PROGRESS", "AFTER"]
STEP_TYPES_ALL = {
    "BEFORE" : "BEFORE",
    "IN_PROGRESS" : "IN_PROGRESS",
    "AFTER" : "AFTER",
}
STATUS = [
    ("NEW", "À faire"),
    ("STARTED", "En cours"),
    ("FINISHED", "Terminée"),
    ("PENDING", "En attente"),
    ("CANCELED", "Annulée"),
    ("ARCHIVED", "Archivée")
]
STATUS_All = {
    "NEW" : "NEW",
    "STARTED" : "STARTED",
    "FINISHED" : "FINISHED",
    "PENDING" : "PENDING",
    "CANCELED" : "CANCELED",
    "ARCHIVED" : "ARCHIVED"
}
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
	number = models.CharField(max_length=255, editable=False, null=True)
	name = models.CharField(max_length=255, null=True)
	image = models.ForeignKey('medias.File', on_delete=models.SET_NULL, related_name='task_image', null=True)
	starting_date_time = models.DateTimeField(null=True)
	ending_date_time = models.DateTimeField(null=True)
	started_at = models.DateTimeField(null=True)
	finished_at = models.DateTimeField(null=True)
	estimated_budget = models.FloatField(null=True)
	google_calendar_event_id = models.CharField(max_length=255, null=True)
	latitude = models.CharField(max_length=255, null=True)
	longitude = models.CharField(max_length=255, null=True)
	city = models.CharField(max_length=255, null=True)
	country = models.CharField(max_length=255, null=True)
	zip_code = models.CharField(max_length=255, null=True)
	address = models.TextField(default='', null=True)
	# client infos start
	client_name = models.CharField(max_length=255, null=True)
	client_task_number = models.CharField(max_length=255, null=True)
	billing_address = models.TextField(default='', null=True)
	mobile = models.CharField(max_length=255, null=True)
	fix = models.CharField(max_length=255, null=True)
	email = models.EmailField(max_length=254, null=True)
	site_owner_name = models.CharField(max_length=255, null=True)
	site_tenant_name = models.CharField(max_length=255, null=True)
	# ****************************
	# contractor infos start
	contractor_name = models.CharField(max_length=255, null=True)
	contractor_tel = models.CharField(max_length=255, null=True)
	contractor_email = models.EmailField(max_length=254, null=True)
	# ****************************
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
	state = models.CharField(max_length=255, null=True)
	total_price_ht = models.FloatField(default=0, null=True)
	tva = models.FloatField(default=0, null=True)
	discount = models.FloatField(default=0, null=True)
	total_price_ttc = models.FloatField(default=0, null=True)
	is_display_price = models.BooleanField(default=False, null=True)
	is_from_quote = models.BooleanField(default=False, null=True)
	is_active = models.BooleanField(default=True, null=True)
	priority = models.CharField(max_length=50, choices=PRIORITIES, default= "LOW")
	work_level = models.CharField(max_length=50, choices=LEVELS, default= "MEDIUM")
	status = models.CharField(max_length=50, choices=STATUS, default= "NEW")
	client = models.ForeignKey('sales.Client', on_delete=models.CASCADE, null=True)
	client_signature = models.ForeignKey('feedbacks.Signature', on_delete=models.CASCADE, related_name='task_client_signature', null=True)
	employee_signature = models.ForeignKey('feedbacks.Signature', on_delete=models.CASCADE, related_name='task_employee_signature', null=True)
	folder = models.ForeignKey('medias.Folder', on_delete=models.SET_NULL, null=True)
	company = models.ForeignKey('companies.Company', on_delete=models.SET_NULL, related_name='company_tasks', null=True)
	creator = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True)
	is_deleted = models.BooleanField(default=False, null=True)
	created_at = models.DateTimeField(auto_now_add=True, null=True)
	updated_at = models.DateTimeField(auto_now=True, null=True)

	def calculer_total_ttc(self):
		ttc_avant_remise = self.total_price_ht + (self.total_price_ht * self.tva / 100)
		ttc_apres_remise = ttc_avant_remise * (1 - self.discount / 100)
		self.total_price_ttc = ttc_apres_remise
	
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
class TaskWorker(models.Model):
	task = models.ForeignKey(Task, on_delete=models.SET_NULL, null=True)
	employee = models.ForeignKey('human_ressources.Employee', on_delete=models.SET_NULL, related_name='task_employee', null=True)
	creator = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, related_name='task_worker_former', null=True)
	created_at = models.DateTimeField(auto_now_add=True, null=True)
	updated_at = models.DateTimeField(auto_now=True, null=True)

	def __str__(self):
		return str(self.id)

# Create your models here.
class TaskMaterial(models.Model):
	task = models.ForeignKey(Task, on_delete=models.SET_NULL, null=True)
	material = models.ForeignKey('stocks.Material', on_delete=models.SET_NULL, null=True)
	quantity = models.IntegerField(null=True)
	creator = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True)
	created_at = models.DateTimeField(auto_now_add=True, null=True)
	updated_at = models.DateTimeField(auto_now=True, null=True)

	def __str__(self):
		return str(self.id)

# Create your models here.
class TaskVehicle(models.Model):
	task = models.ForeignKey(Task, on_delete=models.SET_NULL, null=True)
	vehicle = models.ForeignKey('vehicles.Vehicle', on_delete=models.SET_NULL, null=True)
	creator = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True)
	created_at = models.DateTimeField(auto_now_add=True, null=True)
	updated_at = models.DateTimeField(auto_now=True, null=True)

	def __str__(self):
		return str(self.id)

# Create your models here.
class TaskChecklistItem(models.Model):
	number = models.CharField(max_length=255, null=True)
	name = models.CharField(max_length=255, null=True)
	localisation = models.CharField(max_length=255, null=True)
	comment = models.TextField(default='', null=True)
	description = models.TextField(default='', null=True)
	observation = models.TextField(default='', null=True)
	task = models.ForeignKey(Task, on_delete=models.SET_NULL, null=True)
	status = models.CharField(max_length=50, choices=STATUS, default= "NEW")
	is_active = models.BooleanField(default=True, null=True)
	creator = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True)
	created_at = models.DateTimeField(auto_now_add=True, null=True)
	updated_at = models.DateTimeField(auto_now=True, null=True)

	def __str__(self):
		return self.name

# Create your models here.
class TaskStep(models.Model):
	STEP_TYPES = [
        ("BEFORE", "Avant"),
        ("IN_PROGRESS", "En cours"),
        ("AFTER", "Après")
    ]
	name = models.CharField(max_length=255, null=True)
	task = models.ForeignKey(Task, on_delete=models.SET_NULL, null=True)
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
	    
	def __str__(self):
		return self.title

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