from django.db import models
from datetime import datetime
from decimal import Decimal
import random


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
