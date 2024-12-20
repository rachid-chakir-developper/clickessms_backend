from django.db import models
from datetime import datetime
from decimal import Decimal
import random
from collections import defaultdict
from django.db.models import Count, Sum, Q
from django.db.models.functions import ExtractMonth

# Create your models here.
class DecisionDocument(models.Model):
    number = models.CharField(max_length=255, editable=False, null=True)
    name = models.CharField(max_length=255, null=True)
    document = models.ForeignKey(
        "medias.File",
        on_delete=models.SET_NULL,
        related_name="decision_document_file",
        null=True,
    )
    decision_date = models.DateTimeField(null=True)
    reception_date_time = models.DateTimeField(null=True)
    description = models.TextField(default="", null=True)
    observation = models.TextField(default="", null=True)
    is_active = models.BooleanField(default=True, null=True)
    financier = models.ForeignKey(
        "partnerships.Financier", on_delete=models.SET_NULL, null=True
    )
    folder = models.ForeignKey("medias.Folder", on_delete=models.SET_NULL, null=True)
    company = models.ForeignKey(
        "companies.Company",
        on_delete=models.SET_NULL,
        related_name="company_decision_documents",
        null=True,
    )
    creator = models.ForeignKey("accounts.User", on_delete=models.SET_NULL, null=True)
    is_deleted = models.BooleanField(default=False, null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    def save(self, *args, **kwargs):
        # Générer le numéro unique lors de la sauvegarde si ce n'est pas déjà défini
        if not self.number:
            self.number = self.generate_unique_number()

        super(DecisionDocument, self).save(*args, **kwargs)

    def generate_unique_number(self):
        # Implémentez la logique de génération du numéro unique ici
        # Vous pouvez utiliser des combinaisons de date, heure, etc.
        # par exemple, en utilisant la fonction strftime de l'objet datetime
        # pour générer une chaîne basée sur la date et l'heure actuelles.

        # Exemple : Utilisation de la date et de l'heure actuelles
        current_time = datetime.now()
        number_suffix = current_time.strftime("%Y%m%d%H%M%S")
        number_prefix = "".join(
            random.choices("ABCDEFGHIJKLMNOPQRSTUVWXYZ", k=2)
        )  # Ajoutez 3 lettres au début
        number = f"{number_prefix}{number_suffix}"

        # Vérifier s'il est unique dans la base de données
        while DecisionDocument.objects.filter(number=number).exists():
            number_suffix = current_time.strftime("%Y%m%d%H%M%S")
            number = f"{number_prefix}{number_suffix}"

        return number

    def __str__(self):
        return self.name


# Create your models here.
class DecisionDocumentItem(models.Model):
    decision_document = models.ForeignKey(
        DecisionDocument, on_delete=models.SET_NULL, null=True,
        related_name="decision_document_items",
    )
    establishment = models.ForeignKey(
        "companies.Establishment",
        on_delete=models.SET_NULL,
        related_name="establishment_decision_document_items",
        null=True,
    )
    starting_date_time = models.DateTimeField(null=True)
    ending_date_time = models.DateTimeField(null=True)
    price = models.DecimalField(decimal_places=2, max_digits=11, null=True)
    endowment = models.DecimalField(decimal_places=2, max_digits=11, null=True)
    occupancy_rate = models.FloatField(null=True)
    theoretical_number_unit_work = models.FloatField(null=True)
    creator = models.ForeignKey(
        "accounts.User",
        on_delete=models.SET_NULL,
        related_name="decision_document_item_former",
        null=True,
    )
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)
    
    @classmethod
    def monthly_statistics(cls, year, establishments=None, company=None):
        # Base queryset
        queryset = cls.objects.filter(decision_document__company=company)

        # Filtrer par établissements si fourni
        if establishments:
            queryset = queryset.filter(establishment__in=establishments)

        # Annoter et grouper les données par mois et établissement
        data = (
            queryset
            .values('establishment__id')  # Utiliser l'ID de l'établissement
            .annotate(
                month=ExtractMonth('starting_date_time'),
                total_price=Sum('price', filter=Q(starting_date_time__year=year)),
                total_endowment=Sum('endowment', filter=Q(starting_date_time__year=year)),
                average_occupancy_rate=Sum('occupancy_rate', filter=Q(starting_date_time__year=year)),
                total_theoretical_number_unit_work=Sum('theoretical_number_unit_work', filter=Q(starting_date_time__year=year)),
            )
            .order_by('establishment__id', 'month')
        )

        # Structurer les données avec des mois manquants initialisés à 0
        stats = defaultdict(lambda: {month: {
            "total_price": 0,
            "total_endowment": 0,
            "average_occupancy_rate": 0,
            "total_theoretical_number_unit_work": 0
        } for month in range(1, 13)})

        for item in data:
            establishment_id = item['establishment__id']
            month = item['month']
            stats[establishment_id][month] = {
                "total_price": item['total_price'] or 0,
                "total_endowment": item['total_endowment'] or 0,
                "average_occupancy_rate": item['average_occupancy_rate'] or 0,
                "total_theoretical_number_unit_work": item['total_theoretical_number_unit_work'] or 0,
            }

        # Si aucun établissement n'est fourni, retourner les totaux globaux
        if establishments is None:
            totals = {month: {
                "total_price": 0,
                "total_endowment": 0,
                "average_occupancy_rate": 0,
                "total_theoretical_number_unit_work": 0
            } for month in range(1, 13)}

            for establishment_data in stats.values():
                for month, values in establishment_data.items():
                    totals[month]["total_price"] += values["total_price"]
                    totals[month]["total_endowment"] += values["total_endowment"]
                    totals[month]["average_occupancy_rate"] += values["average_occupancy_rate"]
                    totals[month]["total_theoretical_number_unit_work"] += values["total_theoretical_number_unit_work"]

            return {"global_totals": totals}

        return dict(stats)

    def __str__(self):
        return str(self.id)


# Create your models here.
class BankAccount(models.Model):
    ACCOUNT_TYPES = [
        ("CURRENT", "Courant"),  #
        ("SAVINGS", "Placement"),  #
        ("FIXED_TERM", "Compte à terme"),  #
    ]
    number = models.CharField(max_length=255, editable=False, null=True)
    name = models.CharField(max_length=255, null=True)
    image = models.ForeignKey(
        "medias.File",
        on_delete=models.SET_NULL,
        related_name="bank_account_image",
        null=True,
    )
    account_number = models.CharField(max_length=255, null=True)
    account_type = models.CharField(
        max_length=50, choices=ACCOUNT_TYPES, default="CURRENT"
    )
    bank_name = models.CharField(max_length=255, null=True)
    iban = models.CharField(max_length=255, null=True)
    bic = models.CharField(max_length=255, null=True)
    opening_date = models.DateTimeField(null=True)
    closing_date = models.DateTimeField(null=True)
    description = models.TextField(default="", null=True)
    observation = models.TextField(default="", null=True)
    is_active = models.BooleanField(default=True, null=True)
    folder = models.ForeignKey("medias.Folder", on_delete=models.SET_NULL, null=True)
    establishment = models.ForeignKey(
        "companies.Establishment",
        on_delete=models.SET_NULL,
        related_name="establishment_bank_accounts",
        null=True,
    )
    company = models.ForeignKey(
        "companies.Company",
        on_delete=models.SET_NULL,
        related_name="company_bank_accounts",
        null=True,
    )
    creator = models.ForeignKey("accounts.User", on_delete=models.SET_NULL, null=True)
    is_deleted = models.BooleanField(default=False, null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    @property
    def current_balance(self):
        balance = self.bank_account_balances.order_by("-date").first()
        return balance.amount if balance is not None else Decimal(0)

    def save(self, *args, **kwargs):
        # Générer le numéro unique lors de la sauvegarde si ce n'est pas déjà défini
        if not self.number:
            self.number = self.generate_unique_number()

        super(BankAccount, self).save(*args, **kwargs)

    def generate_unique_number(self):
        # Implémentez la logique de génération du numéro unique ici
        # Vous pouvez utiliser des combinaisons de date, heure, etc.
        # par exemple, en utilisant la fonction strftime de l'objet datetime
        # pour générer une chaîne basée sur la date et l'heure actuelles.

        # Exemple : Utilisation de la date et de l'heure actuelles
        current_time = datetime.now()
        number_suffix = current_time.strftime("%Y%m%d%H%M%S")
        number_prefix = "".join(
            random.choices("ABCDEFGHIJKLMNOPQRSTUVWXYZ", k=2)
        )  # Ajoutez 3 lettres au début
        number = f"{number_prefix}{number_suffix}"

        # Vérifier s'il est unique dans la base de données
        while BankAccount.objects.filter(number=number).exists():
            number_suffix = current_time.strftime("%Y%m%d%H%M%S")
            number = f"{number_prefix}{number_suffix}"

        return number

    def __str__(self):
        return self.iban


class Balance(models.Model):
    number = models.CharField(max_length=255, editable=False, null=True)
    name = models.CharField(max_length=255, null=True)
    document = models.ForeignKey(
        "medias.File",
        on_delete=models.SET_NULL,
        related_name="balance_document",
        null=True,
    )
    date = models.DateTimeField(null=True)
    amount = models.DecimalField(decimal_places=2, max_digits=11, null=True)
    bank_account = models.ForeignKey(
        BankAccount,
        on_delete=models.SET_NULL,
        related_name="bank_account_balances",
        null=True,
    )
    creator = models.ForeignKey("accounts.User", on_delete=models.SET_NULL, null=True)
    is_deleted = models.BooleanField(default=False, null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    def save(self, *args, **kwargs):
        # Générer le numéro unique lors de la sauvegarde si ce n'est pas déjà défini
        if not self.number:
            self.number = self.generate_unique_number()

        super(Balance, self).save(*args, **kwargs)

    def generate_unique_number(self):
        # Implémentez la logique de génération du numéro unique ici
        # Vous pouvez utiliser des combinaisons de date, heure, etc.
        # par exemple, en utilisant la fonction strftime de l'objet datetime
        # pour générer une chaîne basée sur la date et l'heure actuelles.

        # Exemple : Utilisation de la date et de l'heure actuelles
        current_time = datetime.now()
        number_suffix = current_time.strftime("%Y%m%d%H%M%S")
        number_prefix = "".join(
            random.choices("ABCDEFGHIJKLMNOPQRSTUVWXYZ", k=2)
        )  # Ajoutez 3 lettres au début
        number = f"{number_prefix}{number_suffix}"

        # Vérifier s'il est unique dans la base de données
        while Balance.objects.filter(number=number).exists():
            number_suffix = current_time.strftime("%Y%m%d%H%M%S")
            number = f"{number_prefix}{number_suffix}"

        return number

    def __str__(self):
        return self.amount


class CashRegister(models.Model):
    number = models.CharField(max_length=255, editable=False, null=True)
    name = models.CharField(max_length=255, null=True)
    description = models.TextField(default="", null=True, blank=True)
    observation = models.TextField(default="", null=True, blank=True)
    opening_date = models.DateTimeField(null=True)
    closing_date = models.DateTimeField(null=True)
    is_active = models.BooleanField(default=True, null=True)
    folder = models.ForeignKey('medias.Folder', on_delete=models.SET_NULL, null=True)
    company = models.ForeignKey(
        "companies.Company",
        on_delete=models.SET_NULL,
        related_name="company_cash_registers",
        null=True,
    )
    creator = models.ForeignKey("accounts.User", on_delete=models.SET_NULL, null=True)
    is_deleted = models.BooleanField(default=False, null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    @property
    def current_balance(self):
        transactions = self.transactions.all()
        total_credit = transactions.filter(transaction_type='CREDIT').aggregate(total=models.Sum('amount'))['total'] or 0
        total_debit = transactions.filter(transaction_type='DEBIT').aggregate(total=models.Sum('amount'))['total'] or 0
        return Decimal(total_credit - total_debit)
    
    def __str__(self):
        return f"{self.name} - {self.number}"

# Create your models here.
class CashRegisterEstablishment(models.Model):
    cash_register = models.ForeignKey(CashRegister, on_delete=models.SET_NULL, null=True, related_name='establishments')
    establishment = models.ForeignKey('companies.Establishment', on_delete=models.SET_NULL, related_name='cash_register_establishments', null=True)
    creator = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, related_name='cash_register_establishments', null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

# Create your models here.
class CashRegisterManager(models.Model):
    cash_register = models.ForeignKey(CashRegister, on_delete=models.SET_NULL, null=True, related_name='managers')
    employee = models.ForeignKey('human_ressources.Employee', on_delete=models.SET_NULL, related_name='cash_register_employees', null=True)
    creator = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, related_name='cash_register_managers', null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return str(self.id)

# Create your models here.
class CashRegisterTransaction(models.Model):
    TRANSACTION_TYPES = [
        ('CREDIT', 'Encaissement'), # Credit
        ('DEBIT', 'Décaissement'), # Debit
    ]
    number = models.CharField(max_length=255, editable=False, null=True)
    label = models.CharField(max_length=255, null=True)
    document = models.ForeignKey(
        "medias.File",
        on_delete=models.SET_NULL,
        related_name="transaction_document",
        null=True,
    )
    description = models.TextField(default="", null=True, blank=True)
    comment = models.TextField(default="", null=True, blank=True)
    cash_register = models.ForeignKey(CashRegister, on_delete=models.SET_NULL, null=True, related_name='transactions')
    expense = models.ForeignKey('purchases.Expense', on_delete=models.SET_NULL, null=True, related_name='cash_register_transactions')
    date = models.DateTimeField(null=True)
    amount = models.DecimalField(decimal_places=2, max_digits=11, null=True)
    transaction_type = models.CharField(max_length=50, choices=TRANSACTION_TYPES, default="CREDIT")
    creator = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, related_name='cash_register_transactions', null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return str(self.id)

class Budget(models.Model):
    STATUS_CHOICES = [
        ("DRAFT", "Brouillon"),                           # Budget en cours de préparation, pas encore soumis
        ("NEW", "Nouveau"),
        ("PENDING", "En attente de validation"), # En attente d'approbation
        ("APPROVED", "Validé"),                           # Budget approuvé pour utilisation
        ("REJECTED", "Rejeté"),                           # Budget rejeté lors de l'approbation
        ("IN_PROGRESS", "En cours"),                      # Budget en cours d'utilisation
        ("PARTIALLY_USED", "Partiellement utilisé"),      # Budget partiellement utilisé mais encore actif
        ("COMPLETED", "Complété"),                        # Budget entièrement consommé selon le montant alloué
        ("OVERSPENT", "Dépassement"),                     # Budget dépassé au-delà du montant alloué
        ("ON_HOLD", "En attente"),                        # Budget mis en pause temporairement
        ("CANCELLED", "Annulé"),                          # Budget annulé, inutilisable
        ("CLOSED", "Clôturé")                             # Budget clôturé pour toute transaction future
    ]
 
    number = models.CharField(max_length=255, editable=False, null=True)
    name = models.CharField(max_length=255, null=True)
    amount_allocated = models.DecimalField(max_digits=10, decimal_places=2)  # Montant prévu
    amount_spent = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))  # Montant dépensé
    starting_date = models.DateTimeField(null=True)
    ending_date = models.DateTimeField(null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="PENDING")
    description = models.TextField(default="", null=True, blank=True)
    observation = models.TextField(default="", null=True, blank=True)
    is_active = models.BooleanField(default=True, null=True)
    folder = models.ForeignKey("medias.Folder", on_delete=models.SET_NULL, null=True)
    establishment = models.ForeignKey(
        "companies.Establishment",
        on_delete=models.SET_NULL,
        related_name="establishment_budgets",
        null=True,
    )
    company = models.ForeignKey(
        "companies.Company",
        on_delete=models.SET_NULL,
        related_name="company_budgets",
        null=True,
    )
    creator = models.ForeignKey("accounts.User", on_delete=models.SET_NULL, null=True)
    is_deleted = models.BooleanField(default=False, null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)
    
    def __str__(self):
        return f"{self.name} - {self.number}"

    def save(self, *args, **kwargs):
        # Générer le numéro unique lors de la sauvegarde si ce n'est pas déjà défini
        if not self.number:
            self.number = self.generate_unique_number()
        
        super(Budget, self).save(*args, **kwargs)
    
    def generate_unique_number(self):
        """Génère un numéro unique pour le budget."""
        current_time = datetime.now()
        number_suffix = current_time.strftime("%Y%m%d%H%M%S")
        number_prefix = "".join(random.choices("ABCDEFGHIJKLMNOPQRSTUVWXYZ", k=2))
        number = f"{number_prefix}{number_suffix}"

        while Budget.objects.filter(number=number).exists():
            number_suffix = current_time.strftime("%Y%m%d%H%M%S")
            number = f"{number_prefix}{number_suffix}"
        
        return number

# Create your models here.
class BudgetAccountingNature(models.Model):
    budget = models.ForeignKey(Budget, on_delete=models.SET_NULL, null=True, related_name='budget_accounting_natures')
    accounting_nature = models.ForeignKey('data_management.AccountingNature', on_delete=models.SET_NULL, related_name='budget_accounting_natures', null=True)
    amount_allocated = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)  # Montant prévu
    managers = models.ManyToManyField('human_ressources.Employee', related_name='budget_accounting_natures')
    creator = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, related_name='budget_accounting_natures', null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return str(self.id)