from django.db import models
from django.db.models import Sum
from datetime import datetime
import random
from decimal import Decimal
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

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

# Create your models here.
class Supplier(models.Model):
	SUPPLIER_TYPES = [
		("BUSINESS", "Entreprise"),
		("INDIVIDUAL", "Particulier"),
	]
	number = models.CharField(max_length=255, editable=False, null=True)
	external_number = models.CharField(default='', max_length=255, null=True)
	name = models.CharField(max_length=255)
	email = models.EmailField(blank=False, max_length=255, verbose_name="email")
	photo = models.ForeignKey('medias.File', on_delete=models.SET_NULL, related_name='supplier_photo', null=True)
	cover_image = models.ForeignKey('medias.File', on_delete=models.SET_NULL, related_name='supplier_cover_image', null=True)
	supplier_type = models.CharField(max_length=50, choices=SUPPLIER_TYPES, default= "INDIVIDUAL", null=True)
	manager_name = models.CharField(max_length=255, null=True)
	latitude = models.CharField(max_length=255, null=True)
	longitude = models.CharField(max_length=255, null=True)
	city = models.CharField(max_length=255, null=True)
	country = models.CharField(max_length=255, null=True)
	zip_code = models.CharField(max_length=255, null=True)
	address = models.TextField(default='', null=True)
	mobile = models.CharField(max_length=255, null=True)
	fix = models.CharField(max_length=255, null=True)
	fax = models.CharField(max_length=255, null=True)
	email = models.EmailField(max_length=254, null=True)
	web_site = models.URLField(max_length=255, null=True)
	other_contacts = models.CharField(max_length=255, null=True)
	iban = models.CharField(max_length=255, null=True)
	bic = models.CharField(max_length=255, null=True)
	bank_name = models.CharField(max_length=255, null=True)
	description = models.TextField(default='', null=True)
	observation = models.TextField(default='', null=True)
	is_active = models.BooleanField(default=True, null=True)
	folder = models.ForeignKey('medias.Folder', on_delete=models.SET_NULL, null=True)
	company = models.ForeignKey('companies.Company', on_delete=models.SET_NULL, related_name='company_suppliers', null=True)
	creator = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, related_name='supplier_former', null=True)
	is_deleted = models.BooleanField(default=False, null=True)
	created_at = models.DateTimeField(auto_now_add=True, null=True)
	updated_at = models.DateTimeField(auto_now=True, null=True)
	
	def save(self, *args, **kwargs):
		# Générer le numéro unique lors de la sauvegarde si ce n'est pas déjà défini
		if not self.number:
			self.number = self.generate_unique_number()

		super(Supplier, self).save(*args, **kwargs)

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
		while Supplier.objects.filter(number=number).exists():
			number_suffix = current_time.strftime("%Y%m%d%H%M%S")
			number = f'{number_prefix}{number_suffix}'

		return number
		
	def __str__(self):
		return self.email



class Expense(models.Model):
	STATUS_CHOICES = [
		("DRAFT", "Brouillon"),
		("NEW", "Nouveau"),
		('PENDING', 'En Attente'),
		('APPROVED', 'Approuvé'),
		('REJECTED', 'Rejeté'),
		('PAID', 'Payé'),
		('UNPAID', 'Non payé')
	]
	EXPENSE_TYPE_CHOICES = [
		("INVESTMENT", "Investissement"),
		("PURCHASE", "Achat"),
	]
	number = models.CharField(max_length=255, editable=False, null=True)
	label = models.CharField(max_length=255, null=True)
	total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))  # Montant total
	expense_date_time = models.DateTimeField(null=True, blank=True)  # Date de la dépense
	payment_method = models.CharField(max_length=50, choices=PAYMENT_METHOD, default= "CREDIT_CARD")
	expense_type = models.CharField(max_length=50, choices=EXPENSE_TYPE_CHOICES, default= "PURCHASE")
	status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="PENDING")
	description = models.TextField(default="", null=True, blank=True)
	comment = models.TextField(default="", null=True, blank=True)
	observation = models.TextField(default="", null=True, blank=True)
	is_amount_accurate = models.BooleanField(default=True, null=True)
	is_planned_in_budget = models.BooleanField(default=False, null=True)
	is_active = models.BooleanField(default=True, null=True)
	cash_register = models.ForeignKey('finance.CashRegister', on_delete=models.SET_NULL, null=True, related_name='cash_register_expenses')
	files = models.ManyToManyField('medias.File', related_name='file_expenses')
	folder = models.ForeignKey('medias.Folder', on_delete=models.SET_NULL, null=True)
	supplier = models.ForeignKey('purchases.Supplier', on_delete=models.SET_NULL, related_name='supplier_expenses', null=True)
	employee = models.ForeignKey('human_ressources.Employee', on_delete=models.SET_NULL, related_name='employee_expenses', null=True)
	establishment = models.ForeignKey(
		"companies.Establishment",
		on_delete=models.SET_NULL,
		related_name="establishment_expenses",
		null=True,
	)
	company = models.ForeignKey(
		"companies.Company",
		on_delete=models.SET_NULL,
		related_name="company_expenses",
		null=True,
	)
	creator = models.ForeignKey("accounts.User", on_delete=models.SET_NULL, null=True)
	is_deleted = models.BooleanField(default=False, null=True)
	created_at = models.DateTimeField(auto_now_add=True, null=True)
	updated_at = models.DateTimeField(auto_now=True, null=True)
	
	def __str__(self):
		return f"{self.name} - {self.number}"

	def calculate_total_amount(self):
		"""Calcule le total_amount en fonction des ExpenseItem associés."""
		total = self.expense_items.aggregate(Sum('amount'))['amount__sum'] or Decimal('0.00')
		return total

	def save(self, *args, **kwargs):
		# Générer le numéro unique lors de la sauvegarde si ce n'est pas déjà défini
		if not self.number:
			self.number = self.generate_unique_number()
		super(Expense, self).save(*args, **kwargs)
	
	def generate_unique_number(self, prefix='DE'):
		# Ajouter l'année courante au préfixe
		current_year = datetime.now().year
		prefix_with_year = f'{prefix}{current_year}'

		# Trouver le dernier devis avec ce préfixe et l'année courante
		last_expense = Expense.objects.filter(number__startswith=prefix_with_year).order_by('number').last()
		
		if last_expense and last_expense.number:
			# Extraire la partie numérique après l'année
			last_number = int(last_expense.number.replace(prefix_with_year, ''))
			new_number = last_number + 1
		else:
			new_number = 1

		# Formater le nouveau numéro avec l'année courante
		formatted_number = f'{prefix_with_year}-{new_number:04d}'
		
		return formatted_number


class ExpenseItem(models.Model):
	STATUS_CHOICES = [
		('PENDING', 'En Attente'),
		('APPROVED', 'Approuvé'),
		('REJECTED', 'Rejeté'),
		('PAID', 'Payé'),
		('UNPAID', 'Non payé')
	]
	expense = models.ForeignKey(Expense, on_delete=models.CASCADE, related_name="expense_items")
	accounting_nature = models.ForeignKey('data_management.AccountingNature', on_delete=models.SET_NULL, related_name='expense_items', null=True)
	amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))  # Montant
	quantity = models.FloatField(null=True, default=1)
	expense_date_time = models.DateTimeField(null=True, blank=True)  # Date de la dépense
	comment = models.TextField(default="", null=True, blank=True)
	description = models.TextField(default="", null=True, blank=True)
	status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="PENDING")
	creator = models.ForeignKey("accounts.User", on_delete=models.SET_NULL, null=True)
	created_at = models.DateTimeField(auto_now_add=True, null=True)
	updated_at = models.DateTimeField(auto_now=True, null=True)
	
	def __str__(self):
		return f"{self.amount} - {self.amount}"

@receiver(post_save, sender=ExpenseItem)
@receiver(post_delete, sender=ExpenseItem)
def update_total_amount(sender, instance, **kwargs):
	"""Met à jour le total_amount d'une Expense lorsque ses ExpenseItems changent."""
	if instance.expense:
		expense = instance.expense
		expense.total_amount = expense.calculate_total_amount()
		expense.save()

class PurchaseOrder(models.Model):
	STATUS_CHOICES = [
		("DRAFT", "Brouillon"),
		("NEW", "Nouveau"),
		('PENDING', 'En Attente'),
		('APPROVED', 'Approuvé'),
		('REJECTED', 'Rejeté'),
	]
	number = models.CharField(max_length=255, editable=False, null=True)
	label = models.CharField(max_length=255, null=True)
	expense = models.ForeignKey(Expense, on_delete=models.SET_NULL, related_name='purchase_orders', null=True)
	total_ttc = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))  # Montant total
	order_date_time = models.DateTimeField(null=True, blank=True)  # Date de la dépense
	payment_method = models.CharField(max_length=50, choices=PAYMENT_METHOD, default= "CREDIT_CARD")
	status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="PENDING")
	description = models.TextField(default="", null=True, blank=True)
	comment = models.TextField(default="", null=True, blank=True)
	observation = models.TextField(default="", null=True, blank=True)
	supplier = models.ForeignKey('purchases.Supplier', on_delete=models.SET_NULL, related_name='purchase_orders', null=True)
	employee = models.ForeignKey('human_ressources.Employee', on_delete=models.SET_NULL, related_name='purchase_orders', null=True)
	establishment = models.ForeignKey(
		"companies.Establishment",
		on_delete=models.SET_NULL,
		related_name="purchase_orders",
		null=True,
	)

	company = models.ForeignKey(
		"companies.Company",
		on_delete=models.SET_NULL,
		related_name="company_purchase_orders",
		null=True,
	)
	creator = models.ForeignKey("accounts.User", on_delete=models.SET_NULL, null=True)
	is_deleted = models.BooleanField(default=False, null=True)
	created_at = models.DateTimeField(auto_now_add=True, null=True)
	updated_at = models.DateTimeField(auto_now=True, null=True)

	class Meta:
		ordering = ['-created_at']
	
	def __str__(self):
		return f"{self.label} - {self.number}"

	def calculate_total_amount(self):
		"""Calcule le total_amount en fonction des ExpenseItem associés."""
		total = self.purchase_order_items.aggregate(Sum('amount_ttc'))['amount_ttc__sum'] or Decimal('0.00')
		return total

	def save(self, *args, **kwargs):
		# Générer le numéro unique lors de la sauvegarde si ce n'est pas déjà défini
		if not self.number:
			self.number = self.generate_unique_number()
		super(PurchaseOrder, self).save(*args, **kwargs)
	
	def generate_unique_number(self, prefix='BC'):
		# Ajouter l'année courante au préfixe
		current_year = datetime.now().year
		prefix_with_year = f'{prefix}{current_year}'

		# Trouver le dernier devis avec ce préfixe et l'année courante
		last_purchase_order = PurchaseOrder.objects.filter(number__startswith=prefix_with_year).order_by('number').last()
		
		if last_purchase_order and last_purchase_order.number:
			# Extraire la partie numérique après l'année
			last_number = int(last_purchase_order.number.replace(prefix_with_year, ''))
			new_number = last_number + 1
		else:
			new_number = 1

		# Formater le nouveau numéro avec l'année courante
		formatted_number = f'{prefix_with_year}-{new_number:04d}'
		
		return formatted_number

class PurchaseOrderItem(models.Model):
	purchase_order = models.ForeignKey(PurchaseOrder, on_delete=models.CASCADE, related_name="purchase_order_items")
	amount_ttc = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))  # Montant
	quantity = models.FloatField(null=True, default=1)
	comment = models.TextField(default="", null=True, blank=True)
	description = models.TextField(default="", null=True, blank=True)
	creator = models.ForeignKey("accounts.User", on_delete=models.SET_NULL, null=True)
	created_at = models.DateTimeField(auto_now_add=True, null=True)
	updated_at = models.DateTimeField(auto_now=True, null=True)
	
	def __str__(self):
		return f"{self.amount_ttc} - {self.amount_ttc}"

@receiver(post_save, sender=PurchaseOrderItem)
@receiver(post_delete, sender=PurchaseOrderItem)
def update_order_total_amount(sender, instance, **kwargs):
	"""Met à jour le total_amount d'une PurchaseOrder lorsque ses PurchaseOrderItem changent."""
	if instance.purchase_order:
		purchase_order = instance.purchase_order
		purchase_order.total_ttc = purchase_order.calculate_total_amount()
		purchase_order.save()