from django.db import models
from datetime import datetime, date, timedelta
from django.utils.timezone import make_aware, is_naive
from decimal import Decimal
import random
from collections import defaultdict
from django.db.models import Count, Sum, Q, Min, Avg
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
        related_name="decision_document_items",
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
        """
        Retourne les données maximales pour chaque mois et chaque établissement d'une année donnée.
        """
        year = int(year)
        start_of_year = make_aware(datetime(year, 1, 1, 0, 0, 0))
        end_of_year = make_aware(datetime(year, 12, 31, 23, 59, 59))

        # Filtrer les éléments pour l'année donnée
        queryset = cls.objects.filter(Q(ending_date_time__isnull=True) | Q(ending_date_time__gt=end_of_year), starting_date_time__year__lte=year)

        # if company:
        #     queryset = queryset.filter(decision_document__company=company)

        # Filtrer par établissements si fourni
        if establishments:
            queryset = queryset.filter(establishment__in=establishments)

        # Calcul des données mensuelles (max data par mois et par établissement)
        monthly_data = defaultdict(lambda: {month: {
            "price": Decimal(0),
            "endowment": Decimal(0),
            "occupancy_rate": 0,
            "theoretical_number_unit_work": 0,
        } for month in range(1, 13)})
        for item in queryset:
            starting_date = item.starting_date_time if item.starting_date_time else None
            ending_date = item.ending_date_time if item.ending_date_time else None
            start_date = starting_date if starting_date >= start_of_year else start_of_year

            # Ajuster end_date en fonction de release_date
            if ending_date is None:
                end_date = end_of_year
            elif ending_date > end_of_year:
                end_date = end_of_year
            else:
                end_date = ending_date
            
            # Assurez-vous que start_date et end_date sont conscients
            start_date = make_aware(start_date) if is_naive(start_date) else start_date
            end_date = make_aware(end_date) if is_naive(end_date) else end_date

            while start_date <= end_date:
                # Calculer le mois à partir de start_date
                month_key = start_date.month
                establishment_id = item.establishment.id
                price = item.price if item.price else Decimal(0)
                endowment = item.endowment if item.endowment else Decimal(0)
                occupancy_rate = item.occupancy_rate if item.occupancy_rate else 0
                theoretical_number_unit_work = item.theoretical_number_unit_work if item.theoretical_number_unit_work else 0
                # Mettre à jour les données si les valeurs de l'élément sont supérieures à l'existant
                month_data = monthly_data[establishment_id][month_key]
                if price and price > month_data["price"]:
                    month_data["price"] = price
                if endowment and endowment > month_data["endowment"]:
                    month_data["endowment"] = endowment
                if occupancy_rate and occupancy_rate > month_data["occupancy_rate"]:
                    month_data["occupancy_rate"] = occupancy_rate
                if theoretical_number_unit_work and theoretical_number_unit_work > month_data["theoretical_number_unit_work"]:
                    month_data["theoretical_number_unit_work"] = theoretical_number_unit_work

                # Passer au mois suivant
                start_date = start_date.replace(day=1) + timedelta(days=32)
                start_date = start_date.replace(day=1)

        # Étape 3 : S'assurer que tous les établissements incluent les 12 mois
        # On ajoute des entrées pour les mois manquants pour chaque établissement
        establishments_ids = establishments or queryset.values_list('establishment__id', flat=True).distinct()
        for establishment_id in establishments_ids:
            if establishment_id not in monthly_data:
                monthly_data[establishment_id] = {month: {
                    "price": Decimal(0),
                    "endowment": Decimal(0),
                    "occupancy_rate": 0,
                    "theoretical_number_unit_work": 0,
                } for month in range(1, 13)}

        # Conversion des données en dictionnaire standard pour le retour
        return {est_id: dict(months) for est_id, months in monthly_data.items()}

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