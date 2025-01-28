from django.db import models
from datetime import datetime
import random
from decimal import Decimal

# Create your models here.
class TransmissionEvent(models.Model):
	number = models.CharField(max_length=255, editable=False, null=True)
	title = models.CharField(max_length=255)
	image = models.ForeignKey('medias.File', on_delete=models.SET_NULL, related_name='transmission_event_image', null=True)
	starting_date_time = models.DateTimeField(null=True)
	ending_date_time = models.DateTimeField(null=True)
	description = models.TextField(default='', null=True)
	observation = models.TextField(default='', null=True)
	is_active = models.BooleanField(default=True, null=True)
	folder = models.ForeignKey('medias.Folder', on_delete=models.SET_NULL, null=True)
	employee = models.ForeignKey('human_ressources.Employee', on_delete=models.SET_NULL, related_name='employee_transmission_events', null=True)
	company = models.ForeignKey('companies.Company', on_delete=models.SET_NULL, related_name='company_transmission_events', null=True)
	creator = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True)
	is_deleted = models.BooleanField(default=False, null=True)
	created_at = models.DateTimeField(auto_now_add=True, null=True)
	updated_at = models.DateTimeField(auto_now=True, null=True)
	
	def save(self, *args, **kwargs):
		# Générer le numéro unique lors de la sauvegarde si ce n'est pas déjà défini
		if not self.number:
			self.number = self.generate_unique_number()

		super(TransmissionEvent, self).save(*args, **kwargs)

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
		while TransmissionEvent.objects.filter(number=number).exists():
			number_suffix = current_time.strftime("%Y%m%d%H%M%S")
			number = f'{number_prefix}{number_suffix}'

		return number
		
	def __str__(self):
		return self.title

# Create your models here.
class TransmissionEventBeneficiary(models.Model):
	transmission_event = models.ForeignKey(TransmissionEvent, on_delete=models.SET_NULL, null=True, related_name='beneficiaries')
	beneficiary = models.ForeignKey('human_ressources.Beneficiary', on_delete=models.SET_NULL, related_name='transmission_event_beneficiary', null=True)
	creator = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, related_name='transmission_event_beneficiary_former', null=True)
	created_at = models.DateTimeField(auto_now_add=True, null=True)
	updated_at = models.DateTimeField(auto_now=True, null=True)

	def __str__(self):
		return str(self.id)

# Create your models here.
class BeneficiaryAbsence(models.Model):
	number = models.CharField(max_length=255, editable=False, null=True)
	title = models.CharField(max_length=255)
	transmission_event = models.ForeignKey(TransmissionEvent, on_delete=models.SET_NULL, null=True)
	starting_date_time = models.DateTimeField(null=True)
	ending_date_time = models.DateTimeField(null=True)
	reasons = models.ManyToManyField('data_management.AbsenceReason', related_name='reason_beneficiary_absences')
	other_reasons = models.CharField(max_length=255, null=True)
	is_considered = models.BooleanField(default=False, null=True)
	comment = models.TextField(default='', null=True)
	observation = models.TextField(default='', null=True)
	folder = models.ForeignKey('medias.Folder', on_delete=models.SET_NULL, null=True)
	employee = models.ForeignKey('human_ressources.Employee', on_delete=models.SET_NULL, related_name='employee_beneficiary_absences', null=True)
	company = models.ForeignKey('companies.Company', on_delete=models.SET_NULL, related_name='company_beneficiary_absences', null=True)
	creator = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, related_name='beneficiary_absence_former', null=True)
	is_deleted = models.BooleanField(default=False, null=True)
	created_at = models.DateTimeField(auto_now_add=True, null=True)
	updated_at = models.DateTimeField(auto_now=True, null=True)

	def __str__(self):
		return str(self.id)

# Create your models here.
class BeneficiaryAbsenceItem(models.Model):
	beneficiary_absence = models.ForeignKey(BeneficiaryAbsence, on_delete=models.SET_NULL, null=True, related_name='beneficiaries')
	beneficiary = models.ForeignKey('human_ressources.Beneficiary', on_delete=models.SET_NULL, related_name='beneficiary_absence_items', null=True)
	creator = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, related_name='beneficiary_absence_item_former', null=True)
	created_at = models.DateTimeField(auto_now_add=True, null=True)
	updated_at = models.DateTimeField(auto_now=True, null=True)

	def __str__(self):
		return str(self.id)

# Create your models here.
class PersonalizedProject(models.Model):
	number = models.CharField(max_length=255, editable=False, null=True)
	title = models.CharField(max_length=255)
	starting_date_time = models.DateTimeField(null=True)
	ending_date_time = models.DateTimeField(null=True)
	beneficiary = models.ForeignKey('human_ressources.Beneficiary', on_delete=models.SET_NULL, related_name='personalized_projects', null=True)
	description = models.TextField(default='', null=True)
	observation = models.TextField(default='', null=True)
	folder = models.ForeignKey('medias.Folder', on_delete=models.SET_NULL, null=True)
	employee = models.ForeignKey('human_ressources.Employee', on_delete=models.SET_NULL, related_name='personalized_projects', null=True)
	company = models.ForeignKey('companies.Company', on_delete=models.SET_NULL, related_name='personalized_projects', null=True)
	creator = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True)
	is_deleted = models.BooleanField(default=False, null=True)
	created_at = models.DateTimeField(auto_now_add=True, null=True)
	updated_at = models.DateTimeField(auto_now=True, null=True)
		
	def __str__(self):
		return self.title
		
# Create your models here.
class BeneficiaryExpense(models.Model):
	STATUS_CHOICES = [
		('PENDING', 'En Attente'),
		('APPROVED', 'Approuvé'),
		('REJECTED', 'Rejeté'),
		('PAID', 'Payé'),
		('UNPAID', 'Non payé')
	]
	PAYMENT_METHOD = [
		("CASH", "Espèces"),
		("CREDIT_CARD", "Carte de crédit"),
		("BANK_TRANSFER", "Virement bancaire"),
		("DIRECT_DEBIT", "Prélèvement"),
		("PURCHASE_ORDER", "Bon de commande"),
		("CHECK", "Chèque"),
		("PAYPAL", "PayPal"),
		("BILL_OF_EXCHANGE", "Lettre de change relevé"),
		("LIBEO_TRANSFER", "Virement par Libeo"),
		("MOBILE_PAYMENT", "Paiement mobile"),
		("CRYPTOCURRENCY", "Cryptomonnaie"),
		("DEBIT_CARD", "Carte de débit"),
		("APPLE_PAY", "Apple Pay"),
		("GOOGLE_PAY", "Google Pay"),
	]
	number = models.CharField(max_length=255, editable=False, null=True)
	label = models.CharField(max_length=255, null=True)
	beneficiary = models.ForeignKey('human_ressources.Beneficiary', on_delete=models.SET_NULL, related_name='beneficiary_expenses', null=True)
	endowment_type = models.ForeignKey('data_management.TypeEndowment', on_delete=models.SET_NULL, related_name='beneficiary_expenses', null=True)
	amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))  # Montant total
	expense_date_time = models.DateTimeField(null=True, blank=True)  # Date de la dépense
	payment_method = models.CharField(max_length=50, choices=PAYMENT_METHOD, default= "CASH")
	bank_card = models.ForeignKey('finance.BankCard', on_delete=models.SET_NULL, null=True, related_name='beneficiary_expenses')
	cash_register = models.ForeignKey('finance.CashRegister', on_delete=models.SET_NULL, null=True, related_name='beneficiary_expenses')
	check_number = models.CharField(max_length=255, blank=True, null=True)
	bank_name = models.CharField(max_length=255, blank=True, null=True)
	status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="PENDING")
	description = models.TextField(default="", null=True, blank=True)
	comment = models.TextField(default="", null=True, blank=True)
	observation = models.TextField(default="", null=True, blank=True)
	is_active = models.BooleanField(default=True, null=True)
	files = models.ManyToManyField('medias.File', related_name='file_beneficiary_expenses')
	folder = models.ForeignKey('medias.Folder', on_delete=models.SET_NULL, null=True)
	employee = models.ForeignKey('human_ressources.Employee', on_delete=models.SET_NULL, related_name='employee_beneficiary_expenses', null=True)
	company = models.ForeignKey(
		"companies.Company",
		on_delete=models.SET_NULL,
		related_name="company_beneficiary_expenses",
		null=True,
	)
	creator = models.ForeignKey("accounts.User", on_delete=models.SET_NULL, null=True)
	is_deleted = models.BooleanField(default=False, null=True)
	created_at = models.DateTimeField(auto_now_add=True, null=True)
	updated_at = models.DateTimeField(auto_now=True, null=True)
		
	def __str__(self):
		return self.label
