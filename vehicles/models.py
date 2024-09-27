from django.db import models
from datetime import datetime
import random

# Create your models here.
class Vehicle(models.Model):
	VEHICLE_STATE = [
		('NEW', 'Neuf'),
		('GOOD', 'En bon état'),
		('BAD', 'Mauvais'),
		('TO_REVIEW', 'À réviser'),
		('IN_REPAIR', 'En réparation'),
		('OUT_OF_SERVICE', 'Hors service'),
	]
	CRIT_AIR_CHOICES = [
		('', 'NONE'),
		('ZERO', '0'),
		('ONE', '1'),
		('TWO', '2'),
		('THREE', '3'),
		('FOUR', '4'),
		('FIVE', '5')
	]
	number = models.CharField(max_length=255, editable=False, null=True)
	name = models.CharField(max_length=255)
	image = models.ForeignKey('medias.File', on_delete=models.SET_NULL, related_name='vehicle_image', null=True)
	registration_number = models.CharField(max_length=255)
	vehicle_brand = models.ForeignKey('data_management.VehicleBrand', on_delete=models.SET_NULL, related_name='brand_vehicles', null=True)
	vehicle_model = models.ForeignKey('data_management.VehicleModel', on_delete=models.SET_NULL, related_name='model_vehicles', null=True)
	state = models.CharField(max_length=50, choices=VEHICLE_STATE, default= "GOOD", null=True)
	crit_air_vignette = models.CharField(max_length=50, choices=CRIT_AIR_CHOICES, null=True, blank=True)
	description = models.TextField(default='', null=True)
	observation = models.TextField(default='', null=True)
	is_active = models.BooleanField(default=True, null=True)
	folder = models.ForeignKey('medias.Folder', on_delete=models.SET_NULL, null=True)
	company = models.ForeignKey('companies.Company', on_delete=models.SET_NULL, related_name='company_vehicles', null=True)
	creator = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True)
	is_deleted = models.BooleanField(default=False, null=True)
	created_at = models.DateTimeField(auto_now_add=True, null=True)
	updated_at = models.DateTimeField(auto_now=True, null=True)
	
	def save(self, *args, **kwargs):
		# Générer le numéro unique lors de la sauvegarde si ce n'est pas déjà défini
		if not self.number:
			self.number = self.generate_unique_number()

		super(Vehicle, self).save(*args, **kwargs)

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
		while Vehicle.objects.filter(number=number).exists():
			number_suffix = current_time.strftime("%Y%m%d%H%M%S")
			number = f'{number_prefix}{number_suffix}'

		return number

	@property
	def current_vehicle_inspection(self):
		return self.vehicle_inspections.order_by('-inspection_date_time').first()
		
	def __str__(self):
		return self.name

# Create your models here.
class VehicleEstablishment(models.Model):
	vehicle = models.ForeignKey(Vehicle, on_delete=models.SET_NULL, null=True, related_name='vehicle_establishments')
	establishments = models.ManyToManyField('companies.Establishment')
	starting_date = models.DateTimeField(null=True)
	ending_date = models.DateTimeField(null=True)
	creator = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True)
	created_at = models.DateTimeField(auto_now_add=True, null=True)
	updated_at = models.DateTimeField(auto_now=True, null=True)

# Create your models here.
class VehicleEmployee(models.Model):
	vehicle = models.ForeignKey(Vehicle, on_delete=models.SET_NULL, null=True, related_name='vehicle_employees')
	employees = models.ManyToManyField('human_ressources.Employee')
	starting_date = models.DateTimeField(null=True)
	ending_date = models.DateTimeField(null=True)
	creator = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True)
	created_at = models.DateTimeField(auto_now_add=True, null=True)
	updated_at = models.DateTimeField(auto_now=True, null=True)

class VehicleOwnership(models.Model):
	OWNERSHIP_TYPE_CHOICES = [
		("LEASE", "Location Longue Durée"),
		("LEASE_PURCHASE_OPTION", "Location avec option d'achat"),
		("PURCHASE", "Achat"),
		("LOAN", "Prêt"),
		("SALE", "Vendu"),
	]
	vehicle = models.ForeignKey(Vehicle, on_delete=models.SET_NULL, null=True, related_name='vehicle_ownerships')
	ownership_type = models.CharField(max_length=30, choices=OWNERSHIP_TYPE_CHOICES, default= "LEASE", null=True)
	purchase_date = models.DateTimeField(null=True, blank=True)
	purchase_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
	sale_date = models.DateTimeField(null=True, blank=True)
	sale_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
	rental_starting_date = models.DateTimeField(null=True, blank=True)
	rental_ending_date = models.DateTimeField(null=True, blank=True)
	rental_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
	rent_purchase_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
	expected_mileage = models.FloatField(null=True, blank=True)
	loan_details = models.TextField(default='', null=True, blank=True)
	creator = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True)
	created_at = models.DateTimeField(auto_now_add=True, null=True)
	updated_at = models.DateTimeField(auto_now=True, null=True)

class VehicleInspection(models.Model):
	number = models.CharField(max_length=255, editable=False, null=True)
	vehicle = models.ForeignKey(Vehicle, on_delete=models.SET_NULL, null=True, related_name='vehicle_inspections')
	inspection_date_time = models.DateTimeField(null=True, blank=True)
	next_inspection_date = models.DateTimeField(null=True, blank=True)
	next_technical_inspection_date = models.DateTimeField(null=True, blank=True)
	controller_employees = models.ManyToManyField('human_ressources.Employee')
	controller_partner = models.ForeignKey('partnerships.Partner', on_delete=models.SET_NULL, null=True, blank=True, related_name='inspected_vehicles')
	mileage = models.FloatField(null=True, blank=True)
	is_registration_card_here = models.BooleanField(default=False, null=True)
	is_insurance_certificate_here = models.BooleanField(default=False, null=True)
	is_insurance_attestation_here = models.BooleanField(default=False, null=True)
	is_technical_control_here = models.BooleanField(default=False, null=True)
	is_oil_level_checked = models.BooleanField(default=False, null=True)
	is_windshield_washer_level_checked = models.BooleanField(default=False, null=True)
	is_brake_fluid_level_checked = models.BooleanField(default=False, null=True)
	is_coolant_level_checked = models.BooleanField(default=False, null=True)
	is_tire_pressure_checked = models.BooleanField(default=False, null=True)
	is_lights_condition_checked = models.BooleanField(default=False, null=True)
	is_body_condition_checked = models.BooleanField(default=False, null=True)
	remarks = models.TextField(default='', null=True, blank=True)
	images = models.ManyToManyField('medias.File', related_name='image_vehicle_inspections')
	videos = models.ManyToManyField('medias.File', related_name='video_vehicle_inspections')
	folder = models.ForeignKey('medias.Folder', on_delete=models.SET_NULL, null=True)
	company = models.ForeignKey('companies.Company', on_delete=models.SET_NULL, related_name='company_inspected_vehicles', null=True)
	creator = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True)
	is_deleted = models.BooleanField(default=False, null=True)
	created_at = models.DateTimeField(auto_now_add=True, null=True)
	updated_at = models.DateTimeField(auto_now=True, null=True)
	
	def save(self, *args, **kwargs):
		# Générer le numéro unique lors de la sauvegarde si ce n'est pas déjà défini
		if not self.number:
			self.number = self.generate_unique_number()

		super(VehicleInspection, self).save(*args, **kwargs)

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
		while VehicleInspection.objects.filter(number=number).exists():
			number_suffix = current_time.strftime("%Y%m%d%H%M%S")
			number = f'{number_prefix}{number_suffix}'

		return number
		
	def __str__(self):
		return self.number



class VehicleTechnicalInspection(models.Model):
	TECH_INSPECTION_STATES = [
		('FAVORABLE', 'Favorable'),
		('NOT_FAVORABLE', 'Non favorable'),
	]
	number = models.CharField(max_length=255, editable=False, null=True)
	vehicle = models.ForeignKey(Vehicle, on_delete=models.SET_NULL, null=True, related_name='vehicle_technical_inspections')
	inspection_date_time = models.DateTimeField(null=True, blank=True)
	next_inspection_date = models.DateTimeField(null=True, blank=True)
	document = models.ForeignKey('medias.File', on_delete=models.SET_NULL, related_name='vehicle_technical_inspections', null=True)
	observation = models.TextField(default='', null=True, blank=True)
	state = models.CharField(max_length=50, choices=TECH_INSPECTION_STATES, default= "FAVORABLE", null=True)
	folder = models.ForeignKey('medias.Folder', on_delete=models.SET_NULL, null=True)
	company = models.ForeignKey('companies.Company', on_delete=models.SET_NULL, related_name='vehicle_technical_inspections', null=True)
	creator = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True)
	is_deleted = models.BooleanField(default=False, null=True)
	created_at = models.DateTimeField(auto_now_add=True, null=True)
	updated_at = models.DateTimeField(auto_now=True, null=True)
	
	def save(self, *args, **kwargs):
		# Générer le numéro unique lors de la sauvegarde si ce n'est pas déjà défini
		if not self.number:
			self.number = self.generate_unique_number()

		super(VehicleTechnicalInspection, self).save(*args, **kwargs)

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
		while VehicleTechnicalInspection.objects.filter(number=number).exists():
			number_suffix = current_time.strftime("%Y%m%d%H%M%S")
			number = f'{number_prefix}{number_suffix}'

		return number
		
	def __str__(self):
		return self.number

# Create your models here.
class VehicleInspectionFailure(models.Model):
	INSPECTION_FAILURE_TYPES = [
		('MINOR', 'Défaillance mineur'),
		('MAJOR', 'Défaillance majeur'),
		('CRITICAL', 'Défaillance critique'),
	]
	vehicle_technical_inspection = models.ForeignKey(VehicleTechnicalInspection, on_delete=models.SET_NULL, null=True, related_name='failures')
	failure_type = models.CharField(max_length=50, choices=INSPECTION_FAILURE_TYPES, default= "MINOR", null=True)
	description = models.TextField(default='', null=True)
	creator = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, related_name='technical_inspection_failures', null=True)
	created_at = models.DateTimeField(auto_now_add=True, null=True)
	updated_at = models.DateTimeField(auto_now=True, null=True)

class VehicleRepair(models.Model):
	REPAIR_STATES = [
		('COMPLETED', 'Terminée'),
		('TO_DO', 'À faire'),
	]
	number = models.CharField(max_length=255, editable=False, null=True)
	label = models.CharField(max_length=255, null=True, blank=True)
	vehicle = models.ForeignKey(Vehicle, on_delete=models.SET_NULL, null=True, related_name='vehicle_repairs')
	document = models.ForeignKey('medias.File', on_delete=models.SET_NULL, related_name='vehicle_repairs', null=True)
	repair_date_time = models.DateTimeField(null=True, blank=True)
	garage_partner = models.ForeignKey('partnerships.Partner', on_delete=models.SET_NULL, null=True, blank=True, related_name='vehicle_repairs')
	state = models.CharField(max_length=50, choices=REPAIR_STATES, default= "COMPLETED", null=True)
	description = models.TextField(default='', null=True, blank=True)
	observation = models.TextField(default='', null=True, blank=True)
	report = models.TextField(default='', null=True, blank=True)
	total_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True)
	folder = models.ForeignKey('medias.Folder', on_delete=models.SET_NULL, null=True)
	company = models.ForeignKey('companies.Company', on_delete=models.SET_NULL, related_name='vehicle_repairs', null=True)
	creator = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True)
	is_deleted = models.BooleanField(default=False, null=True)
	created_at = models.DateTimeField(auto_now_add=True, null=True)
	updated_at = models.DateTimeField(auto_now=True, null=True)
	
	def save(self, *args, **kwargs):
		# Générer le numéro unique lors de la sauvegarde si ce n'est pas déjà défini
		if not self.number:
			self.number = self.generate_unique_number()
		if self.vehicle and not self.label:
			self.label = f"Réparation de {self.vehicle.name}"

		super(VehicleRepair, self).save(*args, **kwargs)

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
		while VehicleRepair.objects.filter(number=number).exists():
			number_suffix = current_time.strftime("%Y%m%d%H%M%S")
			number = f'{number_prefix}{number_suffix}'

		return number
		
	def __str__(self):
		return self.number

# Create your models here.
class VehicleTheCarriedOutRepair(models.Model):
	vehicle_repair = models.ForeignKey(VehicleRepair, on_delete=models.SET_NULL, null=True, related_name='repairs')
	description = models.TextField(default='', null=True)
	creator = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, related_name='vehicle_the_carried_out_repairs', null=True)
	created_at = models.DateTimeField(auto_now_add=True, null=True)
	updated_at = models.DateTimeField(auto_now=True, null=True)

# Create your models here.
class VehicleRepairVigilantPoint(models.Model):
	vehicle_repair = models.ForeignKey(VehicleRepair, on_delete=models.SET_NULL, null=True, related_name='vigilant_points')
	description = models.TextField(default='', null=True)
	creator = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, related_name='vehicle_repair_vigilant_points', null=True)
	created_at = models.DateTimeField(auto_now_add=True, null=True)
	updated_at = models.DateTimeField(auto_now=True, null=True)



