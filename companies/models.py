from django.db import models
from datetime import datetime, timedelta
from django.utils.timezone import make_aware, is_naive
import random
from decimal import Decimal, ROUND_DOWN
from django.db.models import Q

# Create your models here.

    
class CompanyMedia(models.Model):
    sce_shop_url = models.URLField(max_length=255, null=True)
    blog_url = models.URLField(max_length=255, null=True)
    
    collective_agreement_url = models.URLField(max_length=255, null=True)
    company_agreement_url = models.URLField(max_length=255, null=True)
    labor_law_url = models.URLField(max_length=255, null=True)
    associations_foundations_code_url = models.URLField(max_length=255, null=True)
    safc_code_url = models.URLField(max_length=255, null=True)

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
    hidden_modules = models.TextField(blank=True, null=True) 
    folder = models.ForeignKey('medias.Folder', on_delete=models.SET_NULL, null=True)
    creator = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, related_name='company_creator', null=True)
    is_deleted = models.BooleanField(default=False, null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    def set_hidden_modules(self, module_list):
        self.hidden_modules = ",".join(module_list)

    @property
    def company_hidden_modules(self):
        return self.hidden_modules.split(",") if self.hidden_modules else []

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
        ("HOUR", "Heure"),#
        ("DAY", "Jour"),#
        ("WEEK", "Semaine"),#
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

    def get_all_children(self):
        """ Récupère tous les établissements enfants de manière itérative (évite la récursion infinie et les boucles) """
        children = []
        stack = list(self.establishment_childs.all())  # Initialiser avec les enfants directs
        visited = set()  # Stocke les IDs des établissements déjà visités

        while stack:
            current = stack.pop()  # Récupérer un élément de la pile
            if current.id in visited:
                # Boucle infinie détectée, on passe à l'élément suivant
                continue
            visited.add(current.id)  # Marquer l'établissement comme visité
            children.append(current)  # Ajouter l'établissement à la liste des enfants
            stack.extend(current.establishment_childs.all())  # Ajouter ses enfants à la pile

        return children

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
            Q(starting_date_time__lt=end_date),
            Q(ending_date_time__isnull=True) | Q(ending_date_time__gte=start_date),
        ).order_by('-starting_date_time').first()

        # Retourner la capacité de la dernière autorisation
        return last_activity.capacity if last_activity else 0

    def get_monthly_unit_price(self, year, month):
        """
        Retourne le prix pour un mois donné. Si aucun prix trouvé, recherche dans l'établissement parent.
        Évite les boucles infinies en cas de référence circulaire.

        :param year: Année (int).
        :param month: Mois (int).
        :return: Dernier prix trouvé (Decimal) ou 0 si aucun.
        """
        year = int(year)
        month = int(month)
        
        start_date = datetime(year, month, 1)
        end_date = datetime(year + 1, 1, 1) if month == 12 else datetime(year, month + 1, 1)

        establishment = self  
        visited = set()  # Stocker les établissements déjà visités

        while establishment:
            if establishment.id in visited:  # Détection d'une boucle infinie
                print(f"Boucle détectée dans la hiérarchie des établissements ! Arrêt.")
                break

            visited.add(establishment.id)  # Ajouter l'établissement à l'ensemble des visités

            try:
                last_decision_document_item = establishment.decision_document_items.filter(
                    Q(price__isnull=False) & ~Q(price=0),
                    Q(starting_date_time__lt=end_date),
                    Q(ending_date_time__isnull=True) | Q(ending_date_time__gte=start_date),
                ).order_by('-starting_date_time').first()
                
                if last_decision_document_item and last_decision_document_item.price:
                    return Decimal(last_decision_document_item.price)

            except Exception as e:
                print(f"Erreur lors de la récupération du prix: {e}")

            establishment = establishment.establishment_parent  # Passer au parent

        return Decimal(0)  # Aucun prix trouvé

        # Retourner la capacité de la dernière autorisation
        return last_decision_document_item.price if last_decision_document_item and last_decision_document_item.price else Decimal(0)

    def get_present_beneficiaries(self, year, month):
        year = int(year)
        month = int(month)

        # Début et fin du mois spécifié
        month_start = datetime(year, month, 1)
        if month == 12:
            month_end = datetime(year + 1, 1, 1)
        else:
            month_end = datetime(year, month + 1, 1)

        month_start = make_aware(month_start) if is_naive(month_start) else month_start
        month_end = make_aware(month_end) if is_naive(month_end) else month_end

        queryset = self.establishments_beneficiary_entries.filter(
            Q(entry_date__lt=month_end),
            Q(release_date__isnull=True) | Q(release_date__gte=month_start),
            beneficiary__is_deleted=False
        )

        beneficiaries = []
        for entry in queryset:
            # Déterminer les bornes ajustées
            start_date = max(entry.entry_date, month_start)
            end_date = entry.release_date if entry.release_date and entry.release_date < month_end else month_end

            start_date = make_aware(start_date) if is_naive(start_date) else start_date
            end_date = make_aware(end_date) if is_naive(end_date) else end_date

            # Calcul du nombre de jours incluant entrée et sortie
            delta_days = (end_date.date() - start_date.date()).days
            days_in_month = max(delta_days, 0)
            if entry.release_date and entry.release_date < month_end and entry.release_date.date() != start_date.date():
                days_in_month+=1
            elif entry.release_date and entry.release_date < month_end:
                days_in_month+=2

            beneficiaries.append({
                'beneficiary_entry': entry,
                'days_in_month': days_in_month,
                'establishment': self,
            })

        return beneficiaries


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