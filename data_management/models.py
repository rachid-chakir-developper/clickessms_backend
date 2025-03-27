from django.db import models
from accounts.models import User


class CustomField(models.Model):
	FIELD_TYPES = [
		('TEXT', 'Text'),
		('TEXTAREA', 'Zone du text'),
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
		('Beneficiary', 'Personne accompagnée'),
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
	beneficiary = models.ForeignKey('human_ressources.Beneficiary', on_delete=models.SET_NULL, related_name='custom_field_values', null=True)
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
	is_deleted = models.BooleanField(default=False, null=True)
	created_at = models.DateTimeField(auto_now_add=True, null=True)
	updated_at = models.DateTimeField(auto_now=True, null=True)

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
	is_deleted = models.BooleanField(default=False, null=True)
	created_at = models.DateTimeField(auto_now_add=True, null=True)
	updated_at = models.DateTimeField(auto_now=True, null=True)

	def __str__(self):
		return str(self.address)
		
# Create your models here.
class AddressBookEntry(models.Model):
    number = models.CharField(max_length=255, editable=False, null=True)
    beneficiary = models.ForeignKey('human_ressources.Beneficiary', on_delete=models.SET_NULL, related_name='address_book_entries', null=True)
    title = models.CharField(max_length=255, blank=False, null=True)
    first_name = models.CharField(max_length=255, blank=False, null=True)
    last_name = models.CharField(max_length=255, blank=False, null=True)
    email = models.EmailField(blank=False, max_length=255, verbose_name="email", null=True)
    full_address = models.TextField(default='', null=True)
    address = models.TextField(default='', null=True)
    additional_address = models.TextField(default='', null=True)
    latitude = models.CharField(max_length=255, null=True)
    longitude = models.CharField(max_length=255, null=True)
    city = models.CharField(max_length=255, null=True)
    country = models.CharField(max_length=255, null=True)
    zip_code = models.CharField(max_length=255, null=True)
    mobile = models.CharField(max_length=255, null=True)
    fix = models.CharField(max_length=255, null=True)
    fax = models.CharField(max_length=255, null=True)
    web_site = models.URLField(max_length=255, null=True)
    description = models.TextField(default='', null=True)
    other_contacts = models.CharField(max_length=255, null=True)
    company = models.ForeignKey('companies.Company', on_delete=models.SET_NULL, related_name='address_book_entries', null=True)
    creator = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, related_name='former_address_book_entries', null=True)
    is_deleted = models.BooleanField(default=False, null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)


# Create your models here.
class DataModel(models.Model):
	id = models.AutoField(primary_key=True)
	number = models.CharField(max_length=255, null=True)
	code = models.CharField(max_length=255, null=True)
	name = models.CharField(max_length=255)
	description = models.TextField(default='', null=True)
	parent = models.ForeignKey('self', on_delete=models.SET_NULL, related_name='children', null=True, blank=True)
	is_considered = models.BooleanField(default=False, null=True)
	is_active = models.BooleanField(default=True, null=True)
	company = models.ForeignKey('companies.Company', on_delete=models.SET_NULL, null=True)
	creator = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
	is_deleted = models.BooleanField(default=False, null=True)
	created_at = models.DateTimeField(auto_now_add=True, null=True)
	updated_at = models.DateTimeField(auto_now=True, null=True)

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

class BeneficiaryStatus(DataModel):
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

class BeneficiaryDocumentType(DataModel):
	def __str__(self):
		return str(self.id)
		
class JobCandidateDocumentType(DataModel):
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

class TypeEndowment(DataModel):
	def __str__(self):
		return str(self.id)

class ProfessionalStatus(DataModel):
	def __str__(self):
		return str(self.id)

class JobPlatform(DataModel):
	def __str__(self):
		return str(self.id)

class AccountingNature(DataModel):
	starting_date = models.DateField(null=True)
	ending_date = models.DateField(null=True)
	replaced_accounting_nature = models.ForeignKey('self', on_delete=models.SET_NULL, related_name='replaced_by_accounting_natures', null=True, blank=True)
	def __str__(self):
		return str(self.id)
	class Meta:
		ordering = ['code']

	def save(self, *args, **kwargs):
		# Vérifier si cette nature remplace une autre nature
		if self.replaced_accounting_nature:
			# Mettre à jour l'ending_date de la nature remplacée avec le starting_date de la nouvelle nature
			self.replaced_accounting_nature.ending_date = self.starting_date
			self.replaced_accounting_nature.save()  # Enregistrer la nature remplacée après modification

		# Appeler la méthode save() du parent pour enregistrer l'objet actuel
		super().save(*args, **kwargs)