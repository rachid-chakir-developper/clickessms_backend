from django.db import models
from datetime import datetime
import random

# Create your models here.


class CompanyMedia(models.Model):
    sce_shop_url = models.URLField(max_length=255, null=True)
    blog_url = models.URLField(max_length=255, null=True)
    collective_agreement = models.ForeignKey('medias.File', on_delete=models.SET_NULL, related_name='collective_agreement_company_medias', null=True)
    company_agreement = models.ForeignKey('medias.File', on_delete=models.SET_NULL, related_name='company_agreement_company_medias', null=True)
    labor_law = models.ForeignKey('medias.File', on_delete=models.SET_NULL, related_name='labor_law_company_medias', null=True)
    associations_foundations_code = models.ForeignKey('medias.File', on_delete=models.SET_NULL, related_name='associations_foundations_code_company_medias', null=True)
    safc_code = models.ForeignKey('medias.File', on_delete=models.SET_NULL, related_name='safc_code_company_medias', null=True)
    creator = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, related_name='company_medias', null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return self.id

class Company(models.Model):
    COMPANY_STATUS_CHOICES=[
        ('ACTIVE', 'Active'),
        ('INACTIVE', 'Inactive'),
        ('PENDING', 'En attente de vérification'),
        ('SUSPENDED', 'Suspendue'),
        ('CLOSED', 'Fermée'),
        ('TRIAL', "En période d'essai"),
        ('EXPIRED', 'Expiré'),
        ('RENEWAL_PENDING', 'Renouvellement en attente'),
        ('ARCHIVED', 'Archivée'),
        ('UNDER_REVIEW', 'En révision'),
        ('TERMINATED', 'Résiliée'),
        ('ON_HOLD', 'En attente'),
    ]
    number = models.CharField(max_length=255, editable=False, null=True)
    name = models.CharField(max_length=255, default='Entreprise sans nom')
    logo = models.ForeignKey('medias.File', on_delete=models.SET_NULL, related_name='company_logo', null=True)
    cover_image = models.ForeignKey('medias.File', on_delete=models.SET_NULL, related_name='company_cover_image', null=True)
    primary_color = models.TextField(default='#ffffff', null=True)
    secondary_color = models.TextField(default='#cccccc', null=True)
    text_color = models.TextField(default='#333333', null=True)
    opening_date = models.DateTimeField(null=True)
    closing_date = models.DateTimeField(null=True)
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
    sce_shop_url = models.URLField(max_length=255, null=True)
    web_site = models.URLField(max_length=255, null=True)
    other_contacts = models.CharField(max_length=255, null=True)
    iban = models.CharField(max_length=255, null=True)
    bic = models.CharField(max_length=255, null=True)
    bank_name = models.CharField(max_length=255, null=True)
    description = models.TextField(default='', null=True)
    observation = models.TextField(default='', null=True)
    status = models.CharField(max_length=20, choices=COMPANY_STATUS_CHOICES, default='TRIAL')
    is_active = models.BooleanField(default=True, null=True)
    company_media = models.ForeignKey(CompanyMedia, on_delete=models.SET_NULL, null=True, related_name='companies') 
    folder = models.ForeignKey('medias.Folder', on_delete=models.SET_NULL, null=True)
    creator = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, related_name='company_creator', null=True)
    is_deleted = models.BooleanField(default=False, null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    @property
    def company_admin(self):
        try:
            user_company = self.company_users.filter(roles__name="ADMIN").first()
            return user_company.user if user_company else None
        except Exception as e:
            print(f"company_admin Exception: {e}")
            return None
    
    def save(self, *args, **kwargs):
        # Générer le numéro unique lors de la sauvegarde si ce n'est pas déjà défini
        if not self.number:
            self.number = self.generate_unique_number()

        super(Company, self).save(*args, **kwargs)

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
        while Company.objects.filter(number=number).exists():
            number_suffix = current_time.strftime("%Y%m%d%H%M%S")
            number = f'{number_prefix}{number_suffix}'

        return number

    def __str__(self):
        return self.name


class Establishment(models.Model):
    MEASUREMENT_ACTIVITY_UNITS = [
        ("DAY", "Jour"),#
        ("HOUR", "Heure"),#
        ("MONTH", "Mois")#
    ]
    number = models.CharField(max_length=255, editable=False, null=True)
    name = models.CharField(max_length=255, default='Etablissement sans nom')
    siret = models.CharField(max_length=255, null=True)
    finess = models.CharField(max_length=255, null=True)
    ape_code = models.CharField(max_length=255, null=True)
    logo = models.ForeignKey('medias.File', on_delete=models.SET_NULL, related_name='establishment_logo', null=True)
    cover_image = models.ForeignKey('medias.File', on_delete=models.SET_NULL, related_name='establishment_cover_image', null=True)
    primary_color = models.TextField(default='#ffffff', null=True)
    secondary_color = models.TextField(default='#cccccc', null=True)
    text_color = models.TextField(default='#333333', null=True)
    opening_date = models.DateTimeField(null=True)
    closing_date = models.DateTimeField(null=True)
    measurement_activity_unit = models.CharField(max_length=50, choices=MEASUREMENT_ACTIVITY_UNITS, default= "DAY")
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
    establishment_parent = models.ForeignKey('self', on_delete=models.SET_NULL, related_name='establishment_childs', null=True)
    folder = models.ForeignKey('medias.Folder', on_delete=models.SET_NULL, null=True)
    establishment_category = models.ForeignKey('data_management.EstablishmentCategory', on_delete=models.SET_NULL, null=True)
    establishment_type = models.ForeignKey('data_management.EstablishmentType', on_delete=models.SET_NULL, null=True)
    company = models.ForeignKey('companies.Company', on_delete=models.SET_NULL, related_name='company_establishments', null=True)
    creator = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, related_name='establishment_creator', null=True)
    is_deleted = models.BooleanField(default=False, null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)
    
    def save(self, *args, **kwargs):
        # Générer le numéro unique lors de la sauvegarde si ce n'est pas déjà défini
        if not self.number:
            self.number = self.generate_unique_number()

        super(Establishment, self).save(*args, **kwargs)

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
        while Establishment.objects.filter(number=number).exists():
            number_suffix = current_time.strftime("%Y%m%d%H%M%S")
            number = f'{number_prefix}{number_suffix}'

        return number

    def get_monthly_capacity(self, year, month):
        """
        Retourne la dernière capacité saisie pour un mois donné.

        :param year: Année pour laquelle la capacité est calculée.
        :param month: Mois pour lequel la capacité est calculée (1-12).
        :return: Dernière capacité saisie (float) ou None si aucune.
        """
        year=int(year)
        month=int(month)
        start_date = datetime(year, month, 1)
        if month == 12:
            end_date = datetime(year + 1, 1, 1)
        else:
            end_date = datetime(year, month + 1, 1)

        # Filtrer les ActivityAuthorization pour cet établissement dans le mois donné
        last_activity = self.activity_authorizations.filter(
            is_active=True,
            starting_date_time__lt=end_date,
            ending_date_time__gte=start_date,
        ).order_by('-starting_date_time').first()

        # Retourner la capacité de la dernière autorisation
        return last_activity.capacity if last_activity else 0

    def __str__(self):
        return self.name

# Create your models here.
class EstablishmentManager(models.Model):
    establishment = models.ForeignKey(Establishment, on_delete=models.SET_NULL, null=True, related_name='managers')
    employee = models.ForeignKey('human_ressources.Employee', on_delete=models.SET_NULL, related_name='establishment_manager', null=True)
    creator = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, related_name='establishment_manager_former', null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return str(self.id)

# Create your models here.
class ActivityAuthorization(models.Model):
    establishment = models.ForeignKey(Establishment, on_delete=models.SET_NULL, null=True, related_name='activity_authorizations')
    document = models.ForeignKey('medias.File', on_delete=models.SET_NULL, related_name='activity_authorization_file', null=True)
    starting_date_time = models.DateTimeField(null=True)
    ending_date_time = models.DateTimeField(null=True)
    capacity = models.FloatField(null=True)
    temporary_capacity = models.FloatField(null=True)
    is_active = models.BooleanField(default=True, null=True)
    creator = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, related_name='activity_authorization_former', null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return str(self.id)