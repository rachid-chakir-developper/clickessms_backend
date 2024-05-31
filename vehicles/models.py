from django.db import models
from datetime import datetime
import random

# Create your models here.
class Vehicle(models.Model):
	VEHICLE_STATE = [
		('NEW', 'Neuf'),
		('GOOD', 'Correct'),
		('BAD', 'Mauvais'),
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
        ('LEASE', 'Location'),
        ('PURCHASE', 'Achat'),
        ('SALE', 'Vente'),
    ]
    vehicle = models.ForeignKey(Vehicle, on_delete=models.SET_NULL, null=True, related_name='vehicle_ownerships')
    ownership_type = models.CharField(max_length=10, choices=OWNERSHIP_TYPE_CHOICES, default= "LEASE", null=True)
    purchase_date = models.DateField(null=True, blank=True)
    purchase_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    sale_date = models.DateField(null=True, blank=True)
    sale_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    rental_starting_date = models.DateField(null=True, blank=True)
    rental_ending_date = models.DateField(null=True, blank=True)
    rental_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    expected_mileage = models.FloatField(null=True, blank=True)
    creator = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

class VehicleInspection(models.Model):
	number = models.CharField(max_length=255, editable=False, null=True)
	vehicle = models.ForeignKey(Vehicle, on_delete=models.SET_NULL, null=True, related_name='vehicle_inspections')
	inspection_date_time = models.DateField(null=True, blank=True)
	next_inspection_date = models.DateField(null=True, blank=True)
	controller_employees = models.ManyToManyField('human_ressources.Employee')
	controller_partner = models.ForeignKey('partnerships.Partner', on_delete=models.SET_NULL, null=True, blank=True, related_name='inspected_vehicles')
	mileage = models.FloatField(null=True, blank=True)
	is_registration_card_here = models.BooleanField(default=False, null=True)
	is_insurance_certificate_here = models.BooleanField(default=False, null=True)
	is_insurance_attestation_here = models.BooleanField(default=False, null=True)
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
	created_at = models.DateTimeField(auto_now_add=True, null=True)
	updated_at = models.DateTimeField(auto_now=True, null=True)



