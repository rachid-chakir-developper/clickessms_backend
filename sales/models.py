from django.db import models
from django.conf import settings
from datetime import datetime
import random
from decimal import Decimal, ROUND_DOWN
import base64
from num2words import num2words

PAYMENT_METHOD = [
	("CASH", "Espèces"),
	("CREDIT_CARD", "Carte de crédit"),
	("BANK_TRANSFER", "Virement bancaire"),
	("DIRECT_DEBIT", "Prélèvement"),
	("PAYPAL", "PayPal"),
	("CHECK", "Chèque"),
	("BILL_OF_EXCHANGE", "Lettre de change relevé"),
	("LIBEO_TRANSFER", "Virement par Libeo"),
	("MOBILE_PAYMENT", "Paiement mobile"),
	("CRYPTOCURRENCY", "Cryptomonnaie"),
	("DEBIT_CARD", "Carte de débit"),
	("APPLE_PAY", "Apple Pay"),
	("GOOGLE_PAY", "Google Pay"),
]

# Create your models here.
class Client(models.Model):
	CLIENT_TYPES = [
		("BUSINESS", "Entreprise"),
		("INDIVIDUAL", "Particulier"),
	]
	number = models.CharField(max_length=255, editable=False, null=True)
	external_number = models.CharField(default='', max_length=255, null=True)
	name = models.CharField(max_length=255)
	email = models.EmailField(blank=False, max_length=255, verbose_name="email")
	photo = models.ForeignKey('medias.File', on_delete=models.SET_NULL, related_name='client_photo', null=True)
	cover_image = models.ForeignKey('medias.File', on_delete=models.SET_NULL, related_name='client_cover_image', null=True)
	client_type = models.CharField(max_length=50, choices=CLIENT_TYPES, default= "INDIVIDUAL", null=True)
	manager_name = models.CharField(max_length=255, null=True)
	latitude = models.CharField(max_length=255, null=True)
	longitude = models.CharField(max_length=255, null=True)
	city = models.CharField(max_length=255, null=True)
	country = models.CharField(max_length=255, null=True)
	zip_code = models.CharField(max_length=255, null=True)
	address = models.TextField(default='', null=True)
	additional_address = models.TextField(default='', null=True)
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
	company = models.ForeignKey('companies.Company', on_delete=models.SET_NULL, related_name='company_clients', null=True)
	creator = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, related_name='client_former', null=True)
	is_deleted = models.BooleanField(default=False, null=True)
	created_at = models.DateTimeField(auto_now_add=True, null=True)
	updated_at = models.DateTimeField(auto_now=True, null=True)
	
	def save(self, *args, **kwargs):
		# Générer le numéro unique lors de la sauvegarde si ce n'est pas déjà défini
		if not self.number:
			self.number = self.generate_unique_number()

		super(Client, self).save(*args, **kwargs)

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
		while Client.objects.filter(number=number).exists():
			number_suffix = current_time.strftime("%Y%m%d%H%M%S")
			number = f'{number_prefix}{number_suffix}'

		return number
		
	def __str__(self):
		return self.email

class Invoice(models.Model):
	INVOICE_TYPES = [
		("STANDARD", "Facture Standard"),
		("DEPOSIT", "Facture d'Acompte"),
	]
	STATUS = [
		("DRAFT", "Brouillon"),
		("VALIDATED", "Validée"),
		("PARTIALLY_PAID", "Semi Réglée"),
		("PAID", "Réglée"),
		("CANCELED", "Annulée"),
	]
	number = models.CharField(max_length=255)
	invoice_type = models.CharField(max_length=50, choices=INVOICE_TYPES, default= "STANDARD")
	title = models.TextField(default='', null=True)
	description = models.TextField(default='', null=True)
	#********establishment*****************************************************
	establishment_logo_base64_encoded = models.TextField(null=True)
	establishment_infos = models.CharField(max_length=255, null=True)
	establishment_number = models.CharField(max_length=255, null=True)
	establishment_name = models.CharField(max_length=255, null=True)
	establishment_siret = models.CharField(max_length=255, null=True)
	establishment_finess = models.CharField(max_length=255, null=True)
	establishment_ape_code = models.CharField(max_length=255, null=True)
	establishment_tva_number = models.CharField(max_length=255, null=True)
	establishment_capacity = models.FloatField(null=True)
	establishment_unit_price = models.DecimalField(decimal_places=2, max_digits=11, null=True, default=Decimal(0))
	establishment_address = models.TextField(default='', null=True)
	establishment_city = models.CharField(max_length=255, null=True)
	establishment_country = models.CharField(max_length=255, null=True)
	establishment_zip_code = models.CharField(max_length=255, null=True)
	establishment_mobile = models.CharField(max_length=255, null=True)
	establishment_fix = models.CharField(max_length=255, null=True)
	establishment_email = models.EmailField(max_length=254, null=True)
	establishment_iban = models.CharField(max_length=255, null=True)
	establishment_bic = models.CharField(max_length=255, null=True)
	establishment_bank_name = models.CharField(max_length=255, null=True)
	#**************************************************************************
	#********financier************************************************************
	financier_logo_base64_encoded = models.TextField(null=True)
	financier_infos = models.CharField(max_length=255, null=True)
	financier_number = models.CharField(max_length=255, null=True)
	financier_name = models.CharField(max_length=255, null=True)
	financier_tva_number = models.CharField(max_length=255, null=True)
	financier_address = models.TextField(default='', null=True)
	financier_city = models.CharField(max_length=255, null=True)
	financier_country = models.CharField(max_length=255, null=True)
	financier_zip_code = models.CharField(max_length=255, null=True)
	financier_mobile = models.CharField(max_length=255, null=True)
	financier_fix = models.CharField(max_length=255, null=True)
	financier_email = models.EmailField(max_length=254, null=True)
	financier_iban = models.CharField(max_length=255, null=True)
	financier_bic = models.CharField(max_length=255, null=True)
	financier_bank_name = models.CharField(max_length=255, null=True)
	#**************************************************************************
	#********company*****************************************************
	company_logo_base64_encoded = models.TextField(null=True)
	company_infos = models.CharField(max_length=255, null=True)
	company_number = models.CharField(max_length=255, null=True)
	company_name = models.CharField(max_length=255, null=True)
	company_siret = models.CharField(max_length=255, null=True)
	company_finess = models.CharField(max_length=255, null=True)
	company_ape_code = models.CharField(max_length=255, null=True)
	company_approval_number = models.CharField(max_length=255, null=True)
	company_tva_number = models.CharField(max_length=255, null=True)
	company_address = models.TextField(default='', null=True)
	company_city = models.CharField(max_length=255, null=True)
	company_country = models.CharField(max_length=255, null=True)
	company_zip_code = models.CharField(max_length=255, null=True)
	company_mobile = models.CharField(max_length=255, null=True)
	company_fix = models.CharField(max_length=255, null=True)
	company_email = models.EmailField(max_length=254, null=True)
	company_bank_code = models.CharField("Bank Code", max_length=5, null=True)
	company_branch_code = models.CharField("Branch Code", max_length=5, null=True)
	company_account_number = models.CharField("Account Number", max_length=11, null=True)
	company_rib_key = models.CharField("RIB Key", max_length=2, null=True)
	company_iban = models.CharField(max_length=255, null=True)
	company_bic = models.CharField(max_length=255, null=True)
	company_bank_name = models.CharField(max_length=255, null=True)
	#**************************************************************************
	year = models.CharField(max_length=255, null=True)
	month = models.CharField(max_length=255, null=True)
	emission_date = models.DateTimeField(null=True)
	due_date = models.DateTimeField(null=True)
	payment_date = models.DateTimeField(null=True)
	comment = models.TextField(default='', null=True)
	total_ht = models.DecimalField(decimal_places=2, max_digits=11, null=True, default=Decimal(0))
	tva = models.DecimalField(decimal_places=2, max_digits=11, null=True, default=Decimal(0))
	discount = models.DecimalField(decimal_places=2, max_digits=11, null=True, default=Decimal(0))
	total_ttc = models.DecimalField(decimal_places=2, max_digits=11, null=True, default=Decimal(0))
	payment_method = models.CharField(max_length=50, choices=PAYMENT_METHOD, default= "BANK_TRANSFER")
	financier = models.ForeignKey('partnerships.Financier', on_delete=models.SET_NULL, null=True)
	establishment = models.ForeignKey("companies.Establishment", on_delete=models.SET_NULL, related_name="invoices", null=True)
	managers = models.ManyToManyField('human_ressources.Employee', related_name='manager_invoices')
	signatures = models.ManyToManyField('feedbacks.Signature', related_name='invoices')
	status = models.CharField(max_length=50, choices=STATUS, default= "DRAFT")
	employee = models.ForeignKey('human_ressources.Employee', on_delete=models.SET_NULL, related_name='invoices', null=True)
	company = models.ForeignKey('companies.Company', on_delete=models.SET_NULL, related_name='invoices', null=True)
	creator = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, related_name='invoices', null=True)
	is_deleted = models.BooleanField(default=False, null=True)
	created_at = models.DateTimeField(auto_now_add=True, null=True)
	updated_at = models.DateTimeField(auto_now=True, null=True)

	@property
	def month_text(self):
		if self.month:
			try:
				return settings.MONTHS[int(self.month) - 1]
			except (IndexError, ValueError):
				return ""
		return ""

	@property
	def total_ttc_text(self):
		try:
			value = float(self.total_ttc)
			euros = int(value)
			centimes = int(round((value - euros) * 100))

			euros_text = num2words(euros, lang='fr')
			if centimes > 0:
				centimes_text = num2words(centimes, lang='fr')
				return f"{euros_text} euros et {centimes_text} centimes".capitalize()
			else:
				return f"{euros_text} euros".capitalize()
		except Exception:
			return str(self.total_ttc)

	def update_totals(self):
		# Recalculer le total HT et TTC
		total_ht = sum(Decimal(item.amount_ht) for item in self.invoice_items.all())
		self.total_ht = Decimal(total_ht).quantize(Decimal('0.01'), rounding=ROUND_DOWN)
		total_ttc = sum(Decimal(item.amount_ttc) for item in self.invoice_items.all())
		self.total_ttc = Decimal(total_ttc).quantize(Decimal('0.01'), rounding=ROUND_DOWN)

		# Recalculer la TVA totale si nécessaire
		if self.total_ht > 0:
			self.tva = ((self.total_ttc - self.total_ht) / self.total_ht * Decimal(100)).quantize(Decimal('0.01'), rounding=ROUND_DOWN)
		elif self.tva >= 0:
			self.total_ht = (self.total_ttc / (1 + (self.tva / Decimal(100)))).quantize(Decimal('0.01'), rounding=ROUND_DOWN) 
		else:
			self.tva = Decimal(0)
		
		self.save()

	def update_company_logo_base64(self):
		"""
		Update the company_logo_base64_encoded field with the base64 representation of the company's logo.
		"""
		if self.company and self.company.logo and self.company.logo.image:
			try:
				# Open the logo file
				with self.company.logo.image.open('rb') as logo_file:
					# Read the content of the file
					logo_data = logo_file.read()
					# Encode it to base64
					self.company_logo_base64_encoded = f"data:image/png;base64,{base64.b64encode(logo_data).decode('utf-8')}"
			except Exception as e:
				raise ValueError(f"Erreur lors de l'encodage base64 du logo : {str(e)}")
		"""
		Update the establishment_logo_base64_encoded field with the base64 representation of the establishment's logo.
		"""
		if self.establishment and self.establishment.logo and self.establishment.logo.image:
			logo_data=None,
			try:
				# Open the logo file
				with self.establishment.logo.image.open('rb') as logo_file:
					# Read the content of the file
					logo_data = logo_file.read()
					# Encode it to base64
					self.establishment_logo_base64_encoded = f"data:image/png;base64,{base64.b64encode(logo_data).decode('utf-8')}"
			except Exception as e:
				raise ValueError(f"Erreur lors de l'encodage base64 du logo : {str(e)}")
		"""
		Update the client_logo_base64_encoded field with the base64 representation of the financier's logo.
		"""
		if self.financier and self.financier.photo and self.financier.photo.image:
			logo_data=None,
			try:
				# Open the logo file
				with self.financier.photo.image.open('rb') as logo_file:
					# Read the content of the file
					logo_data = logo_file.read()
					# Encode it to base64
					self.client_logo_base64_encoded = f"data:image/png;base64,{base64.b64encode(logo_data).decode('utf-8')}"
			except Exception as e:
				raise ValueError(f"Erreur lors de l'encodage base64 du logo : {str(e)}")
	
	def save(self, *args, **kwargs):
		# Si le numéro n'est pas défini, générer un numéro en fonction du statut
		if not self.number:
			if self.status == 'DRAFT':  # Supposons que 'draft' soit le statut pour les brouillons
				self.number = self.generate_unique_number(prefix='BR')
			elif self.status == 'VALIDATED':  # Supposons que 'validated' soit le statut pour les factures validées
				self.number = self.generate_unique_number(prefix='FAC')
		elif self.status != 'DRAFT' and not self.number.startswith('FAC'):  # Supposons que 'validated' soit le statut pour les factures validées
				self.number = self.generate_unique_number(prefix='FAC')
		self.update_company_logo_base64()
		super().save(*args, **kwargs)

	def generate_unique_number(self, prefix='BR'):
		# Ajouter l'année courante au préfixe
		current_year = datetime.now().year
		prefix_with_year = f'{prefix}{current_year}'

		# Chercher la dernière facture avec ce préfixe et l'année courante
		last_invoice = Invoice.objects.filter(number__startswith=prefix_with_year).order_by('number').last()
		
		if last_invoice and last_invoice.number:
			# Extraire la partie numérique après l'année et incrémenter
			last_number = int(last_invoice.number.replace(prefix_with_year, ''))
			new_number = last_number + 1
		else:
			# Si aucun numéro n'existe, commencer à 1
			new_number = 1

		# Formater le nouveau numéro avec des zéros devant
		formatted_number = f'{prefix_with_year}{new_number:05d}'
		
		return formatted_number

	def set_signatures(self, employees=[], creator=None):
		"""
		Définit les signatures des employés pour cette facture.
		Pour chaque employé, sa signature est associée à la facture.

		Args:
			employees (QuerySet): Une liste ou un QuerySet d'objets `Employee`.
		
		Raises:
			ValueError: Si un employé n'a pas de signature associée.
		"""
		from feedbacks.models import Signature  # Import du modèle Signature si nécessaire

		# Effacer les signatures actuelles
		self.signatures.all().delete()

		for employee in employees:
			signature = Signature.objects.create(
				author=employee,
				author_name=f"{employee.first_name} {employee.preferred_name or ''} {employee.last_name}".strip(),
				author_position=employee.current_contract.position if employee.current_contract else employee.position,
				author_number=employee.number,
				author_email=employee.email,
				image=employee.signature,
				creator=creator if creator else self.creator  # Le créateur de la facture
			)
			# Associer la signature de l'employé à la facture
			self.signatures.add(signature)

		# Sauvegarder la facture après modification
		self.save()

	def __str__(self):
		return self.number


class InvoiceEstablishment(models.Model):
	invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, null=True, related_name='invoice_establishments')
	establishment = models.ForeignKey("companies.Establishment", on_delete=models.SET_NULL, related_name="invoice_establishments", null=True)
	#********establishment*****************************************************
	establishment_logo_base64_encoded = models.TextField(null=True)
	establishment_infos = models.CharField(max_length=255, null=True)
	establishment_number = models.CharField(max_length=255, null=True)
	establishment_name = models.CharField(max_length=255, null=True)
	establishment_siret = models.CharField(max_length=255, null=True)
	establishment_finess = models.CharField(max_length=255, null=True)
	establishment_ape_code = models.CharField(max_length=255, null=True)
	establishment_tva_number = models.CharField(max_length=255, null=True)
	establishment_capacity = models.FloatField(null=True)
	establishment_unit_price = models.DecimalField(decimal_places=2, max_digits=11, null=True, default=Decimal(0))
	establishment_address = models.TextField(default='', null=True)
	establishment_city = models.CharField(max_length=255, null=True)
	establishment_country = models.CharField(max_length=255, null=True)
	establishment_zip_code = models.CharField(max_length=255, null=True)
	establishment_mobile = models.CharField(max_length=255, null=True)
	establishment_fix = models.CharField(max_length=255, null=True)
	establishment_email = models.EmailField(max_length=254, null=True)
	establishment_iban = models.CharField(max_length=255, null=True)
	establishment_bic = models.CharField(max_length=255, null=True)
	establishment_bank_name = models.CharField(max_length=255, null=True)
	#**************************************************************************
	comment = models.TextField(default='', null=True)
	total_ht = models.DecimalField(decimal_places=2, max_digits=11, null=True, default=Decimal(0))
	tva = models.DecimalField(decimal_places=2, max_digits=11, null=True, default=Decimal(0))
	discount = models.DecimalField(decimal_places=2, max_digits=11, null=True, default=Decimal(0))
	total_ttc = models.DecimalField(decimal_places=2, max_digits=11, null=True, default=Decimal(0))
	payment_method = models.CharField(max_length=50, choices=PAYMENT_METHOD, default= "BANK_TRANSFER")
	creator = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True)
	created_at = models.DateTimeField(auto_now_add=True, null=True)
	updated_at = models.DateTimeField(auto_now=True, null=True)

	def update_totals(self):
		# Recalculer le total HT et TTC
		total_ht = sum(Decimal(item.amount_ht) for item in self.invoice_items.all())
		self.total_ht = Decimal(total_ht).quantize(Decimal('0.01'), rounding=ROUND_DOWN)
		total_ttc = sum(Decimal(item.amount_ttc) for item in self.invoice_items.all())
		self.total_ttc = Decimal(total_ttc).quantize(Decimal('0.01'), rounding=ROUND_DOWN)

		# Recalculer la TVA totale si nécessaire
		if self.total_ht > 0:
			self.tva = ((self.total_ttc - self.total_ht) / self.total_ht * Decimal(100)).quantize(Decimal('0.01'), rounding=ROUND_DOWN)
		elif self.tva >= 0:
			self.total_ht = (self.total_ttc / (1 + (self.tva / Decimal(100)))).quantize(Decimal('0.01'), rounding=ROUND_DOWN) 
		else:
			self.tva = Decimal(0)
		
		self.save()

	def update_company_logo_base64(self):
		"""
		Update the establishment_logo_base64_encoded field with the base64 representation of the establishment's logo.
		"""
		if self.establishment and self.establishment.logo and self.establishment.logo.image:
			logo_data=None,
			try:
				# Open the logo file
				with self.establishment.logo.image.open('rb') as logo_file:
					# Read the content of the file
					logo_data = logo_file.read()
					# Encode it to base64
					self.establishment_logo_base64_encoded = f"data:image/png;base64,{base64.b64encode(logo_data).decode('utf-8')}"
			except Exception as e:
				raise ValueError(f"Erreur lors de l'encodage base64 du logo : {str(e)}")
	
	def save(self, *args, **kwargs):
		self.update_company_logo_base64()
		super().save(*args, **kwargs)
	

	def __str__(self):
		return self.label

class InvoiceItem(models.Model):
	MEASUREMENT_UNITS = [
		("HOUR", "Heure"),#
		("DAY", "Jour"),#
		("WEEK", "Semaine"),#
		("MONTH", "Mois")#
	]
	invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='invoice_items', null=True)
	invoice_establishment = models.ForeignKey(InvoiceEstablishment, on_delete=models.CASCADE, related_name="invoice_items", null=True)
	label = models.TextField(default='', null=True)
	preferred_name = models.CharField(max_length=255, null=True)
	first_name = models.CharField(max_length=255, null=True)
	last_name = models.CharField(max_length=255, null=True)
	birth_date = models.DateTimeField(null=True)
	entry_date = models.DateTimeField(null=True)
	release_date = models.DateTimeField(null=True)
	description = models.TextField(default='', null=True)
	measurement_unit = models.CharField(max_length=50, choices=MEASUREMENT_UNITS, default= "DAY")
	unit_price = models.DecimalField(decimal_places=2, max_digits=11, null=True, default=Decimal(0))
	quantity = models.FloatField(null=True, default=1)
	tva = models.DecimalField(decimal_places=2, max_digits=11, null=True, default=Decimal(0))
	discount = models.DecimalField(decimal_places=2, max_digits=11, null=True, default=Decimal(0))
	amount_ht = models.DecimalField(decimal_places=2, max_digits=11, null=True, default=Decimal(0))
	amount_ttc = models.DecimalField(decimal_places=2, max_digits=11, null=True, default=Decimal(0))
	beneficiary = models.ForeignKey('human_ressources.Beneficiary', on_delete=models.SET_NULL, null=True, related_name='invoice_items')
	creator = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True)
	created_at = models.DateTimeField(auto_now_add=True, null=True)
	updated_at = models.DateTimeField(auto_now=True, null=True)

	def update_totals(self):
		self.save()

	def save(self, *args, **kwargs):
		# Convertir les valeurs en Decimal pour éviter l'erreur
		unit_price_decimal = Decimal(self.unit_price)
		quantity_decimal = Decimal(self.quantity)
		discount_decimal = Decimal(self.discount) / Decimal(100)
		# Recalculer le prix HT
		self.amount_ht = unit_price_decimal * quantity_decimal * (Decimal(1) - discount_decimal)

		# Recalculer le prix TTC
		tva_decimal = Decimal(self.tva) / Decimal(100)
		self.amount_ttc = self.amount_ht * (Decimal(1) + tva_decimal)

		super(InvoiceItem, self).save(*args, **kwargs)
		
		# Mettre à jour le total de la Invoice après chaque modification d'un InvoiceItem
		self.invoice_establishment.update_totals()
		self.invoice.update_totals()

	def __str__(self):
		return self.label