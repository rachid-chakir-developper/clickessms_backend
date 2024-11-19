from django.db import models
from django.db.models import Sum
from datetime import datetime
from decimal import Decimal
import random
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

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
    number = models.CharField(max_length=255, editable=False, null=True)
    label = models.CharField(max_length=255, null=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))  # Montant total
    expense_date_time = models.DateTimeField(null=True, blank=True)  # Date de la dépense
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="PENDING")
    description = models.TextField(default="", null=True, blank=True)
    observation = models.TextField(default="", null=True, blank=True)
    is_active = models.BooleanField(default=True, null=True)
    files = models.ManyToManyField('medias.File', related_name='file_expenses')
    folder = models.ForeignKey('medias.Folder', on_delete=models.SET_NULL, null=True)
    employee = models.ForeignKey('human_ressources.Employee', on_delete=models.SET_NULL, related_name='employee_expenses', null=True)
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

# Create your models here.
class ExpenseEstablishment(models.Model):
	expense = models.ForeignKey(Expense, on_delete=models.SET_NULL, null=True, related_name='establishments')
	establishment = models.ForeignKey('companies.Establishment', on_delete=models.SET_NULL, related_name='expense_establishments', null=True)
	creator = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, related_name='expense_establishments', null=True)
	created_at = models.DateTimeField(auto_now_add=True, null=True)
	updated_at = models.DateTimeField(auto_now=True, null=True)

	def __str__(self):
		return str(self.id)

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
    establishment = models.ForeignKey(
        "companies.Establishment",
        on_delete=models.SET_NULL,
        related_name="expense_items",
        null=True,
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))  # Montant
    expense_date_time = models.DateTimeField(null=True, blank=True)  # Date de la dépense
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
    expense = instance.expense
    expense.total_amount = expense.calculate_total_amount()
    expense.save()