from django.db import models
from accounts.models import User


class CustomField(models.Model):
	FIELD_TYPES = [
		('TEXT', 'Text'),
		('NUMBER', 'Number'),
		('DATE', 'Date'),
		('DATETIME', 'Date et heure'),
		('BOOLEAN', 'Boolean'),
		('RADIO', 'Radio Button'),
		('SELECT', 'Liste'),
		('SELECT_MULTIPLE', 'Liste à choix multiple'),
		('CHECKBOX', 'Checkbox'),
	]
	MODEL_CHOICES = [
		('Employee', 'Employé'),
		('EmployeeContract', 'Contrat Employé'),
		# Ajoutez d'autres modèles si nécessaire
	]
	label = models.CharField(max_length=255)
	key = models.CharField(max_length=255, unique=True)
	field_type = models.CharField(choices=FIELD_TYPES, max_length=50, default= "TEXT")
	form_model = models.CharField(choices=MODEL_CHOICES, max_length=50)
	is_active = models.BooleanField(default=True, null=True)
	company = models.ForeignKey('companies.Company', on_delete=models.SET_NULL, related_name='custom_fields', null=True)
	creator = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, related_name='custom_fields', null=True)
	is_deleted = models.BooleanField(default=False, null=True)
	created_at = models.DateTimeField(auto_now_add=True, null=True)
	updated_at = models.DateTimeField(auto_now=True, null=True)

	def save(self, *args, **kwargs):
		# Sauvegarder l'instance pour générer l'ID si elle n'existe pas encore
		if not self.id:
			super().save(*args, **kwargs)

		# Générer la clé si elle n'est pas déjà définie
		if not self.key and self.company:
			self.key = f"custom_field_{self.company.id}_{self.id}"
			# Sauvegarder à nouveau avec la clé mise à jour
		super().save(*args, **kwargs)

	def __str__(self):
		return self.label

class CustomFieldOption(models.Model):
	custom_field = models.ForeignKey(CustomField, on_delete=models.CASCADE, related_name='options')
	label = models.CharField(max_length=255)  # Label affiché à l'utilisateur
	value = models.CharField(max_length=255, null=True)  # Valeur interne utilisée dans les données ou les requêtes

	def save(self, *args, **kwargs):
		# Sauvegarder l'instance pour générer l'ID si elle n'existe pas encore
		if not self.id:
			super().save(*args, **kwargs)

		# Générer la clé si elle n'est pas déjà définie
		if not self.value and self.custom_field:
			self.value = f"value_{self.custom_field.id}_{self.id}"
			# Sauvegarder à nouveau avec la clé mise à jour
		super().save(*args, **kwargs)

	def __str__(self):
		return f"{self.label} (pour {self.custom_field.label})"

class CustomFieldValue(models.Model):
	employee = models.ForeignKey('human_ressources.Employee', on_delete=models.SET_NULL, related_name='custom_field_values', null=True)
	employee_contract = models.ForeignKey('human_ressources.EmployeeContract', on_delete=models.SET_NULL, related_name='custom_field_values', null=True)
	custom_field = models.ForeignKey(CustomField, on_delete=models.CASCADE)
	value = models.TextField(null=True, blank=True)

	@property
	def key(self):
		return custom_field.key

	def __str__(self):
		return f"{self.custom_field.label}: {self.value}"


# Create your models here.
class PhoneNumber(models.Model):
	id = models.AutoField(primary_key=True)
	name = models.CharField(default='Sans nom', max_length=255, null=True)
	phone = models.CharField(max_length=255)
	description = models.TextField(default='', null=True)
	company = models.ForeignKey('companies.Company', on_delete=models.SET_NULL, related_name='company_phone_numbers', null=True)
	creator = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

	def __str__(self):
		return str(self.number)

# Create your models here.
class HomeAddress(models.Model):
	id = models.AutoField(primary_key=True)
	name = models.CharField(default='Sans nom', max_length=255, null=True)
	address = models.TextField(default='', null=True)
	description = models.TextField(default='', null=True)
	company = models.ForeignKey('companies.Company', on_delete=models.SET_NULL, related_name='company_home_addresses', null=True)
	creator = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

	def __str__(self):
		return str(self.address)

# Create your models here.
class DataModel(models.Model):
	id = models.AutoField(primary_key=True)
	number = models.CharField(max_length=255, null=True)
	code = models.CharField(max_length=255, null=True)
	name = models.CharField(max_length=255)
	description = models.TextField(default='', null=True)
	parent = models.ForeignKey('self', on_delete=models.SET_NULL, related_name='children', null=True, blank=True)
	company = models.ForeignKey('companies.Company', on_delete=models.SET_NULL, null=True)
	creator = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

	def __str__(self):
		return str(self.id)

	class Meta:
		abstract = True

class HumanGender(DataModel):
	def __str__(self):
		return str(self.id)

class AdmissionDocumentType(DataModel):
	def __str__(self):
		return str(self.id)

class EstablishmentCategory(DataModel):
	def __str__(self):
		return str(self.id)

class EstablishmentType(DataModel):
	def __str__(self):
		return str(self.id)
		
class AbsenceReason(DataModel):
	def __str__(self):
		return str(self.id)

class UndesirableEventNormalType(DataModel):
	def __str__(self):
		return str(self.id)

class UndesirableEventSeriousType(DataModel):
	def __str__(self):
		return str(self.id)

class UndesirableEventFrequency(DataModel):
	def __str__(self):
		return str(self.id)

class MeetingReason(DataModel):
	def __str__(self):
		return str(self.id)

class TypeMeeting(DataModel):
	def __str__(self):
		return str(self.id)

class DocumentType(DataModel):
	def __str__(self):
		return str(self.id)

class VehicleBrand(DataModel):
	def __str__(self):
		return str(self.id)

class VehicleModel(DataModel):
	vehicle_brand = models.ManyToManyField('data_management.VehicleBrand', related_name='vehicle_models')
	def __str__(self):
		return str(self.id)

class EmployeeMission(DataModel):
	def __str__(self):
		return str(self.id)

class AccountingNature(DataModel):
	def __str__(self):
		return str(self.id)