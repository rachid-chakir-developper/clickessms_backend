from django.db import models
from django.utils.timezone import make_aware
from datetime import datetime, date, timedelta
import random
from django.utils import timezone
from decimal import Decimal, ROUND_HALF_UP

from django.db.models import Count, Q, F, ExpressionWrapper, IntegerField, Sum, Case, When, Value, DateTimeField
from django.db.models.functions import ExtractMonth, TruncDay, Greatest, TruncDate
from collections import defaultdict
from calendar import monthrange

from planning.models import EmployeeAbsenceItem

# Create your models here.
class Employee(models.Model):
    number = models.CharField(max_length=255, editable=False, null=True)
    registration_number = models.CharField(max_length=255, null=True)
    gender = models.ForeignKey('data_management.HumanGender', on_delete=models.SET_NULL, null=True)
    preferred_name = models.CharField(max_length=255, null=True)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    email = models.EmailField(blank=False, max_length=255, verbose_name="email")
    social_security_number = models.CharField(max_length=15, blank=True, null=True)
    photo = models.ForeignKey('medias.File', on_delete=models.SET_NULL, related_name='employee_photo', null=True)
    cover_image = models.ForeignKey('medias.File', on_delete=models.SET_NULL, related_name='employee_cover_image', null=True)
    position = models.CharField(max_length=255, null=True)
    birth_date = models.DateTimeField(null=True)
    birth_place = models.CharField(max_length=255, null=True)
    nationality = models.CharField(max_length=255, null=True)
    hiring_date = models.DateTimeField(null=True)
    probation_end_date = models.DateTimeField(null=True)
    work_end_date = models.DateTimeField(null=True)
    starting_salary = models.FloatField(null=True)
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
    company = models.ForeignKey('companies.Company', on_delete=models.SET_NULL, related_name='company_employees', null=True)
    creator = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, related_name='employee_former', null=True)
    is_deleted = models.BooleanField(default=False, null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)
    
    def save(self, *args, **kwargs):
        # Générer le numéro unique lors de la sauvegarde si ce n'est pas déjà défini
        if not self.number:
            self.number = self.generate_unique_number()

        super(Employee, self).save(*args, **kwargs)

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
        while Employee.objects.filter(number=number).exists():
            number_suffix = current_time.strftime("%Y%m%d%H%M%S")
            number = f'{number_prefix}{number_suffix}'

        return number
    @property
    def user(self):
        managed_company = self.managed_companies.filter(company=self.company).first()
        return managed_company.user if managed_company else self.employee_user.all().first()

    @property
    def sce_roles(self):
        sce_members = self.sce_members.all()
        roles = [f"{sce_member.role}_IN_CSE" for sce_member in sce_members]
        if roles:
            roles.insert(0, 'MEMBER_IN_SCE')
        return roles
    @property
    def current_contract(self):
        current_time = timezone.now()
        contracts = self.employee_contracts.filter(starting_date__lte=current_time)
        current_contracts = contracts.filter(models.Q(ending_date__isnull=True) | models.Q(ending_date__gte=current_time))
        if current_contracts.exists():
            return current_contracts.latest('starting_date')
        if contracts.exists():
            return contracts.latest('starting_date')
        return None

    def __str__(self):
        return self.email

    # Create your models here.
class EmployeeGroup(models.Model):
    number = models.CharField(max_length=255, editable=False, null=True)
    name = models.CharField(max_length=255)
    image = models.ForeignKey('medias.File', on_delete=models.SET_NULL, related_name='employee_group_image', null=True)
    description = models.TextField(default='', null=True)
    observation = models.TextField(default='', null=True)
    is_active = models.BooleanField(default=True, null=True)
    folder = models.ForeignKey('medias.Folder', on_delete=models.SET_NULL, null=True)
    company = models.ForeignKey('companies.Company', on_delete=models.SET_NULL, related_name='company_employee_groups', null=True)
    creator = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, related_name='employee_group_former', null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return self.name

    # Create your models here.
class EmployeeGroupItem(models.Model):
    employee = models.ForeignKey('human_ressources.Employee', on_delete=models.SET_NULL, related_name='employee_items', null=True)
    employee_group = models.ForeignKey('human_ressources.EmployeeGroup', on_delete=models.SET_NULL, related_name='employee_group_items', null=True)
    creator = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, related_name='employee_group_item_former', null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    # Create your models here.
class EmployeeContract(models.Model):

    CONTRACT_TYPES = [
        ("CDI", "CDI"),
        ("CDD", "CDD"),
        ("APPRENTICESHIP_CONTRACT", "Contrat d'apprentissage"),
        ("SINGLE_INTEGRATION_CONTRACT", "Contrat Unique d'Insertion (CUI)"),
        ("PROFESSIONALIZATION_CONTRACT", "Contrat de professionnalisation"),
        ("SEASONAL_CONTRACT", "Contrat saisonnier"),
        ("TEMPORARY_CONTRACT", "Contrat intérimaire"),
        ("PART_TIME_CONTRACT", "Contrat à temps partiel"),
        ("FULL_TIME_CONTRACT", "Contrat à temps plein"),
        ("INTERNSHIP_CONTRACT", "Contrat de stage")
    ]
    number = models.CharField(max_length=255, editable=False, null=True)
    title = models.CharField(max_length=255, null=True)
    document = models.ForeignKey('medias.File', on_delete=models.SET_NULL, related_name='employee_contract_doucument', null=True)
    starting_date = models.DateTimeField(null=True)
    ending_date = models.DateTimeField(null=True)
    position = models.CharField(max_length=255, null=True)
    monthly_gross_salary = models.DecimalField("Monthly Gross Salary", max_digits=10, decimal_places=2, default=0.0)
    salary = models.DecimalField("Annual Gross Salary", max_digits=10, decimal_places=2, help_text="Optional if Monthly Gross Salary is provided", null=True, blank=True)
    started_at = models.DateTimeField(null=True)
    ended_at = models.DateTimeField(null=True)
    initial_paid_leave_days = models.DecimalField("Initial Annual Leave Days (CP)", max_digits=5, decimal_places=2, default=25.0)
    initial_rwt_days = models.DecimalField("Initial RTT Days", max_digits=5, decimal_places=2, default=10.0)
    initial_temporary_days = models.DecimalField("Initial Temporary Leave Days (CT)", max_digits=5, decimal_places=2, default=5.0)
    description = models.TextField(default='', null=True)
    observation = models.TextField(default='', null=True)
    contract_type = models.CharField(max_length=50, choices=CONTRACT_TYPES, default= "CDI")
    employee = models.ForeignKey('human_ressources.Employee', on_delete=models.SET_NULL, related_name='employee_contracts', null=True)
    is_active = models.BooleanField(default=True, null=True)
    folder = models.ForeignKey('medias.Folder', on_delete=models.SET_NULL, null=True)
    creator = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, related_name='employee_contract_former', null=True)
    is_deleted = models.BooleanField(default=False, null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    @property
    def rest_paid_leave_days(self):
        # il faut revoir ça pour calculer aussi les jours reportés
        today = timezone.now().date()
        current_year = today.year
        acquisition_start = date(current_year if today.month >= 6 else current_year - 1, 6, 1)
        acquisition_end = date(current_year if today.month >= 6 else current_year - 1, 5, 31) + timedelta(days=365)
        absences_in_period = EmployeeAbsenceItem.objects.filter(
            employee=self.employee,
            employee_absence__leave_type='PAID',
            employee_absence__status='APPROVED',
            employee_absence__starting_date_time__gte=acquisition_start,
            employee_absence__ending_date_time__lte=acquisition_end
        )
        total_days_taken = sum(absence.employee_absence.duration for absence in absences_in_period)
        remaining_days = self.initial_paid_leave_days - total_days_taken
        return remaining_days

    @property
    def rest_rwt_leave_days(self):
        # il faut revoir ça pour calculer aussi les jours reportés
        current_year = timezone.now().year
        absences_in_period = EmployeeAbsenceItem.objects.filter(
            employee=self.employee,
            employee_absence__leave_type='RWT',
            employee_absence__status='APPROVED',
            employee_absence__starting_date_time__year=current_year
        )
        total_days_taken = sum(absence.employee_absence.duration for absence in absences_in_period)
        remaining_days = self.initial_rwt_days - total_days_taken
        return remaining_days

    @property
    def rest_temporary_leave_days(self):
        # il faut revoir ça pour calculer aussi les jours reportés
        current_year = timezone.now().year
        absences_in_period = EmployeeAbsenceItem.objects.filter(
            employee=self.employee,
            employee_absence__leave_type='TEMPORARY',
            employee_absence__status='APPROVED',
            employee_absence__starting_date_time__year=current_year
        )
        total_days_taken = sum(absence.employee_absence.duration for absence in absences_in_period)
        remaining_days = self.initial_temporary_days - total_days_taken
        return remaining_days
    @property
    def acquired_paid_leave_days_by_month(self):
        return Decimal(self.initial_paid_leave_days / 12).quantize(Decimal('0.001'), rounding=ROUND_HALF_UP)
    @property
    def acquired_paid_leave_days(self):
        today = timezone.now().date()
        if today.month < 6:
            acquisition_start = date(today.year - 1, 6, 1)
        else:
            acquisition_start = date(today.year, 6, 1)
        acquisition_end = today
        months_in_acquisition_period = ((today.year - acquisition_start.year) * 12 + today.month - acquisition_start.month)
        if today.day == 1:
           months_in_acquisition_period -= 1
        days_per_month_acquisition = self.initial_paid_leave_days / 12
        acquired_paid_leave_days = months_in_acquisition_period * days_per_month_acquisition
        return Decimal(acquired_paid_leave_days).quantize(Decimal('0.001'), rounding=ROUND_HALF_UP)
    @property
    def being_acquired_paid_leave_days(self):
        return Decimal(self.initial_paid_leave_days - self.acquired_paid_leave_days).quantize(Decimal('0.001'), rounding=ROUND_HALF_UP)
    def get_reported_paid_leave_days_per_year(self):
        reported_paid_leave_days_per_year = {}
        current_date = timezone.now().date()
        start_date = self.starting_date.date()
        acquisition_start_year = start_date.year if start_date.month >= 6 else start_date.year - 1
        acquisition_start = date(acquisition_start_year, 6, 1)
        reported_paid_leave_days = 0
        while acquisition_start < current_date:
            acquisition_end = date(acquisition_start.year + 1, 5, 31)
            if self.ending_date and self.ending_date.date() < acquisition_end:
                acquisition_end = self.ending_date.date()
            if acquisition_end > current_date:
                break
            months_in_period = ((acquisition_end.year - acquisition_start.year) * 12 + acquisition_end.month - acquisition_start.month) + 1
            days_per_month_acquisition = Decimal(self.initial_paid_leave_days) / 12
            acquired_paid_leave_days = months_in_period * days_per_month_acquisition
            absences_in_period = EmployeeAbsenceItem.objects.filter(
                employee=self.employee,
                employee_absence__leave_type='PAID',
                employee_absence__status='APPROVED',
                employee_absence__starting_date_time__gte=acquisition_start,
                employee_absence__ending_date_time__lte=acquisition_end
            )
            days_taken = sum(absence.employee_absence.duration for absence in absences_in_period)
            remaining_days = acquired_paid_leave_days - days_taken
            remaining_days += reported_paid_leave_days
            rounded_remaining_days = Decimal(remaining_days).quantize(Decimal('0.001'), rounding=ROUND_HALF_UP)
            if rounded_remaining_days == rounded_remaining_days.to_integral():
                rounded_remaining_days = int(rounded_remaining_days)
            reported_paid_leave_days_per_year[f"{acquisition_start.year}-{acquisition_start.year + 1}"] = rounded_remaining_days
            acquisition_start = date(acquisition_start.year + 1, 6, 1)
            reported_paid_leave_days = 0
        return reported_paid_leave_days_per_year
    @property
    def total_reported_paid_leave_days(self):
        reported_paid_leave_days = self.get_reported_paid_leave_days_per_year()
        return Decimal(sum(reported_paid_leave_days.values())).quantize(Decimal('0.001'), rounding=ROUND_HALF_UP)
    def __str__(self):
        return str(self.id)

# Create your models here.
class EmployeeContractMission(models.Model):
    employee_contract = models.ForeignKey(EmployeeContract, on_delete=models.SET_NULL, null=True, related_name='missions')
    mission = models.ForeignKey('data_management.EmployeeMission', on_delete=models.SET_NULL, related_name='employee_contract_missions', null=True)
    creator = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, related_name='employee_contract_mission_former', null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

# Create your models here.
class EmployeeContractEstablishment(models.Model):
    employee_contract = models.ForeignKey(EmployeeContract, on_delete=models.SET_NULL, null=True, related_name='establishments')
    establishment = models.ForeignKey('companies.Establishment', on_delete=models.SET_NULL, related_name='employee_contract_establishment', null=True)
    creator = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, related_name='employee_contract_establishment_former', null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

# Create your models here.
class EmployeeContractReplacedEmployee(models.Model):
    employee_contract = models.ForeignKey(EmployeeContract, on_delete=models.SET_NULL, null=True, related_name='replaced_employees')
    employee = models.ForeignKey(Employee, on_delete=models.SET_NULL, related_name='employee_contract_eeplaced_employee', null=True)
    position = models.CharField(max_length=255, null=True, blank=True)
    reason = models.CharField(max_length=255, null=True, blank=True)
    starting_date = models.DateTimeField(null=True)
    ending_date = models.DateTimeField(null=True)
    creator = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, related_name='employee_contract_eeplaced_employee_former', null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    @property
    def text(self):
        """Retourne une description complète de l'instance."""
        if self.employee and self.starting_date and self.ending_date:
            start_date_formatted = self.starting_date.strftime('%d %B %Y')
            end_date_formatted = self.ending_date.strftime('%d %B %Y')
            return f"{self.employee.last_name.upper()} {self.employee.first_name}, {self.position}, en {self.reason} du {start_date_formatted} au {end_date_formatted}"
        return f"Contrat employé remplacé ID: {self.id}"

# Create your models here.
class Beneficiary(models.Model):
    number = models.CharField(max_length=255, editable=False, null=True)
    gender = models.ForeignKey('data_management.HumanGender', on_delete=models.SET_NULL, null=True)
    preferred_name = models.CharField(max_length=255, null=True)
    first_name = models.CharField(max_length=255, null=True)
    last_name = models.CharField(max_length=255, null=True)
    email = models.EmailField(blank=False, max_length=255, verbose_name="email")
    photo = models.ForeignKey('medias.File', on_delete=models.SET_NULL, related_name='beneficiary_photo', null=True)
    cover_image = models.ForeignKey('medias.File', on_delete=models.SET_NULL, related_name='beneficiary_cover_image', null=True)
    birth_date = models.DateTimeField(null=True)
    admission_date = models.DateTimeField(null=True)
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
    company = models.ForeignKey('companies.Company', on_delete=models.SET_NULL, related_name='company_beneficiaries', null=True)
    creator = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, related_name='beneficiary_former', null=True)
    is_deleted = models.BooleanField(default=False, null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)
    
    def save(self, *args, **kwargs):
        # Générer le numéro unique lors de la sauvegarde si ce n'est pas déjà défini
        if not self.number:
            self.number = self.generate_unique_number()

        super(Beneficiary, self).save(*args, **kwargs)

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
        while Beneficiary.objects.filter(number=number).exists():
            number_suffix = current_time.strftime("%Y%m%d%H%M%S")
            number = f'{number_prefix}{number_suffix}'

        return number

    def __str__(self):
        return self.email

# Create your models here.
class BeneficiaryAdmissionDocument(models.Model):
    beneficiary = models.ForeignKey(Beneficiary, on_delete=models.SET_NULL, null=True, related_name='beneficiary_admission_documents')
    document = models.ForeignKey('medias.File', on_delete=models.SET_NULL, related_name='document_beneficiary_admission_documents', null=True)
    admission_document_type = models.ForeignKey('data_management.AdmissionDocumentType', on_delete=models.SET_NULL, null=True)
    financier = models.ForeignKey('partnerships.Financier', on_delete=models.SET_NULL, null=True)
    starting_date = models.DateTimeField(null=True)
    ending_date = models.DateTimeField(null=True)
    creator = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return self.id

# Create your models here.
class BeneficiaryStatusEntry(models.Model):
    beneficiary = models.ForeignKey(Beneficiary, on_delete=models.SET_NULL, null=True, related_name='beneficiary_status_entries')
    document = models.ForeignKey('medias.File', on_delete=models.SET_NULL, related_name='beneficiary_status_entries', null=True)
    beneficiary_status = models.ForeignKey('data_management.BeneficiaryStatus', on_delete=models.SET_NULL, null=True)
    starting_date = models.DateTimeField(null=True)
    ending_date = models.DateTimeField(null=True)
    creator = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return self.id

# Create your models here.
class BeneficiaryEntry(models.Model):
    beneficiary = models.ForeignKey(Beneficiary, on_delete=models.SET_NULL, null=True, related_name='beneficiary_entries')
    entry_date = models.DateTimeField(null=True)
    due_date = models.DateTimeField(null=True)
    release_date = models.DateTimeField(null=True)
    establishments = models.ManyToManyField('companies.Establishment', related_name='establishments_beneficiary_entries')
    internal_referents = models.ManyToManyField('human_ressources.Employee', related_name='referents_beneficiary_entries')
    creator = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    @classmethod
    def monthly_statistics(cls, year, establishments=None, company=None):
        # Filtrer les données de base
        year=int(year)
        queryset = cls.objects.filter(beneficiary__company=company)

        if establishments:
            # Filtrer uniquement pour les établissements spécifiés
            queryset = queryset.filter(establishments__in=establishments)

        # Annoter les dates d'entrée et de sortie avec des valeurs par défaut si nécessaire
        queryset = queryset.annotate(
            effective_entry_date=Case(
                When(entry_date__year__lt=year, then=Value(datetime(year, 1, 1))),  # 1er janvier de l'année donnée
                default=F('entry_date'),
                output_field=models.DateTimeField()
            ),
            effective_release_date=Case(
                When(release_date__isnull=True, then=Value(datetime(year, 12, 31, 23, 59, 59))),  # Dernière seconde de l'année
                default=F('release_date'),
                output_field=models.DateTimeField()
            )
        )
        # Calculer le nombre de jours en utilisant la fonction `TruncDate` pour obtenir les jours exacts
        queryset = queryset.annotate(
            days_present_in_month=ExpressionWrapper(
                Greatest(
                    TruncDate(F('effective_release_date')) - TruncDate(F('effective_entry_date')),
                    Value(0)
                ),
                output_field=IntegerField()
            )
        )

        # Annoter et grouper les données
        data = (
            queryset
            .values('establishments__id')  # Utilisation de l'ID de l'établissement
            .annotate(
                month=ExtractMonth('entry_date'),
                total_entries=Count('id', filter=Q(entry_date__year=year)),
                total_releases=Count('id', filter=Q(release_date__year=year)),
                total_due=Count('id', filter=Q(due_date__year=year)),
                present_at_end_of_month=Count(
                    'id',
                    filter=Q(release_date__year=year) &
                           (Q(release_date__month__gt=F('month')) | Q(release_date__isnull=False)) |
                           Q(release_date__year__gt=year)
                ),
                total_days_present=Sum('days_present_in_month'),
                # Capacité totale pour chaque mois et établissement
                capacity=Sum(
                    'establishments__activity_authorizations__capacity', 
                    filter=Q(establishments__activity_authorizations__is_active=True) &
                           Q(establishments__activity_authorizations__starting_date_time__year=year) &
                           Q(establishments__activity_authorizations__starting_date_time__month=F('month'))
                ),
                # Capacité temporaire pour chaque mois et établissement
                temporary_capacity=Sum(
                    'establishments__activity_authorizations__temporary_capacity', 
                    filter=Q(establishments__activity_authorizations__is_active=True) &
                           Q(establishments__activity_authorizations__starting_date_time__year=year) &
                           Q(establishments__activity_authorizations__starting_date_time__month=F('month'))
                )
            )
            .order_by('establishments__id', 'month')
        )

        # Structurer les données pour inclure les mois manquants
        stats = defaultdict(lambda: {
            month: {
                "total_entries": 0,
                "total_releases": 0,
                "total_due": 0,
                "present_at_end_of_month": 0,
                "total_days_present": 0,
                "capacity": 0,
                "temporary_capacity": 0
            }
            for month in range(1, 13)
        })

        for item in data:
            establishment_id = item['establishments__id']
            month = item['month']
            stats[establishment_id][month] = {
                "total_entries": item['total_entries'],
                "total_releases": item['total_releases'],
                "total_due": item['total_due'],
                "present_at_end_of_month": item['present_at_end_of_month'],
                "total_days_present": item['total_days_present'],
                "capacity": item['capacity'],
                "temporary_capacity": item['temporary_capacity'],
            }

        # Si aucun établissement n'est fourni, retourner les totaux globaux
        if establishments is None:
            totals = {
                month: {
                    "total_entries": 0,
                    "total_releases": 0,
                    "total_due": 0,
                    "present_at_end_of_month": 0,
                    "total_days_present": 0,
                    "capacity": 0,
                    "temporary_capacity": 0
                }
                for month in range(1, 13)
            }
            for establishment, monthly_data in stats.items():
                for month, values in monthly_data.items():
                    totals[month]["total_entries"] += values["total_entries"]
                    totals[month]["total_releases"] += values["total_releases"]
                    totals[month]["total_due"] += values["total_due"]
                    totals[month]["present_at_end_of_month"] += values["present_at_end_of_month"]
                    totals[month]["total_days_present"] += values["total_days_present"]
            return {"global_totals": totals}

        return dict(stats)

    @classmethod
    def monthly_presence_statistics(cls, year, establishments=None, company=None):
        year = int(year)

        # Convertir les datetime naïfs en datetime conscients des fuseaux horaires
        start_of_year = datetime(year, 1, 1)
        end_of_year = datetime(year, 12, 31)

        # Si les dates sont naïves, les rendre conscientes
        print('heeerrrr11')
        start_of_year = make_aware(start_of_year) if start_of_year.tzinfo is None else start_of_year
        end_of_year = make_aware(end_of_year) if end_of_year.tzinfo is None else end_of_year

        # Étape 1 : Filtrer les enregistrements de base
        queryset = cls.objects.filter(entry_date__year__lte=year).annotate(
            effective_entry_date=Case(
                When(entry_date__lt=start_of_year, then=Value(start_of_year)),
                default=F('entry_date'),
                output_field=DateTimeField()
            ),
            effective_release_date=Case(
                When(release_date__isnull=True, then=Value(end_of_year)),
                When(release_date__gt=end_of_year, then=Value(end_of_year)),
                default=F('release_date'),
                output_field=DateTimeField()
            )
        )

        print('heeerrrr222221')
        # Filtrer par société si fourni
        if company:
            queryset = queryset.filter(beneficiary__company=company)

        # Filtrer par établissements si fourni
        if establishments:
            queryset = queryset.filter(establishments__in=establishments)

        # Étape 2 : Calculer les statistiques mensuelles
        monthly_data = defaultdict(lambda: {month: {"total_days_present": 0, "present_at_end_of_month": 0} for month in range(1, 13)})
        print('heeerrrr3333333333333331')
        for entry in queryset:
            for establishment in entry.establishments.all():
                print('heeerrrr44444')
                start_date = entry.effective_entry_date
                end_date = entry.effective_release_date
                print('heeerrrr5555')
                # Rendre start_date et end_date conscients si nécessaire
                start_date = make_aware(start_date) if start_date.tzinfo is None else start_date
                end_date = make_aware(end_date) if end_date.tzinfo is None else end_date
                print('herrr6666')
                while start_date <= end_date:
                    month_start = datetime(start_date.year, start_date.month, 1)
                    month_end = (month_start + timedelta(days=32)).replace(day=1) - timedelta(seconds=1)
                    print('heeerrr7777')
                    # Rendre month_start et month_end conscients si nécessaire
                    month_start = make_aware(month_start) if month_start.tzinfo is None else month_start
                    month_end = make_aware(month_end) if month_end.tzinfo is None else month_end
                    print('heeerrrr8888')
                    days_in_month = (min(end_date, month_end) - max(start_date, month_start)).days + 1

                    # Ajouter au total des jours pour le mois
                    monthly_data[establishment.id][start_date.month]["total_days_present"] += max(0, days_in_month)

                    # Ajouter au compteur des bénéficiaires présents jusqu'à la fin du mois
                    if entry.release_date is None or entry.release_date > month_end:
                        monthly_data[establishment.id][start_date.month]["present_at_end_of_month"] += 1

                    start_date = month_end + timedelta(seconds=1)

        # Étape 3 : S'assurer que tous les établissements incluent les 12 mois
        establishments_ids = establishments or queryset.values_list('establishments__id', flat=True).distinct()
        for establishment_id in establishments_ids:
            if establishment_id not in monthly_data:
                monthly_data[establishment_id] = {month: {"total_days_present": 0, "present_at_end_of_month": 0} for month in range(1, 13)}

        # Retourner les données structurées
        return dict(monthly_data)

        
    @classmethod
    def present_beneficiaries(cls, year, month, establishments=None, company=None):
        """
        Retourne une liste des `BeneficiaryEntry` pour chaque établissement
        qui sont toujours accompagnés dans un mois donné.
        """
        year = int(year)
        month = int(month)

        # Début et fin du mois spécifié
        start_date = datetime(year, month, 1)
        if month == 12:
            end_date = datetime(year + 1, 1, 1)
        else:
            end_date = datetime(year, month + 1, 1)

        # Filtrer les données de base par entreprise
        queryset = cls.objects.filter(beneficiary__company=company)

        if establishments:
            # Filtrer uniquement pour les établissements spécifiés
            queryset = queryset.filter(establishments__in=establishments)

        # Filtrer les bénéficiaires toujours présents dans le mois spécifié
        queryset = queryset.filter(
            Q(entry_date__lt=end_date),  # Entré avant ou pendant le mois
            Q(release_date__isnull=True) | Q(release_date__gte=start_date)  # Pas encore sorti ou sortie après le début du mois
        )

        # Regrouper par établissement
        result = {}
        for establishment in queryset.values_list('establishments', flat=True).distinct():
            establishment_queryset = queryset.filter(establishments=establishment)
            result[establishment] = list(establishment_queryset)

        return result

    def __str__(self):
        return str(self.id)

# Create your models here.
class BeneficiaryAdmission(models.Model):
    STATUS_CHOICES = [
        ("DRAFT", "Brouillon"),
        ("NEW", "Nouveau"),
        ('PENDING', 'En Attente'),
        ('APPROVED', 'Approuvé'),
        ('REJECTED', 'Rejeté'),
        ('CANCELED', 'Annulé'),
    ]
    number = models.CharField(max_length=255, editable=False, null=True)
    gender = models.ForeignKey('data_management.HumanGender', on_delete=models.SET_NULL, null=True)
    preferred_name = models.CharField(max_length=255, null=True)
    first_name = models.CharField(max_length=255, null=True)
    last_name = models.CharField(max_length=255, null=True)
    email = models.EmailField(blank=False, max_length=255, verbose_name="email")
    photo = models.ForeignKey('medias.File', on_delete=models.SET_NULL, related_name='photo_beneficiary_admissions', null=True)
    birth_date = models.DateTimeField(null=True)
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
    description = models.TextField(default='', null=True)
    observation = models.TextField(default='', null=True)
    beneficiary = models.ForeignKey(Beneficiary, on_delete=models.SET_NULL, null=True, related_name='beneficiary_admissions')
    files = models.ManyToManyField('medias.File', related_name='file_beneficiary_admissions')
    financier = models.ForeignKey('partnerships.Financier', on_delete=models.SET_NULL, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="DRAFT")
    status_reason = models.TextField(default='', null=True)
    employee = models.ForeignKey('human_ressources.Employee', on_delete=models.SET_NULL, related_name='beneficiary_admissions', null=True)
    establishments = models.ManyToManyField('companies.Establishment', related_name='beneficiary_admissions')
    is_active = models.BooleanField(default=True, null=True)
    folder = models.ForeignKey('medias.Folder', on_delete=models.SET_NULL, null=True)
    company = models.ForeignKey('companies.Company', on_delete=models.SET_NULL, related_name='beneficiary_admissions', null=True)
    creator = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, related_name='beneficiary_admissions', null=True)
    is_deleted = models.BooleanField(default=False, null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    @classmethod
    def monthly_statistics(cls, year, establishments=None, company=None):
        year = int(year)
        queryset = cls.objects.filter(
            beneficiary__company=company,
            is_deleted=False,
            created_at__year=year
        )

        if establishments:
            queryset = queryset.filter(establishments__in=establishments)

        data = (
            queryset
            .annotate(
                month=ExtractMonth('created_at'),
                establishment_id=F('establishments__id'),
            )
            .values('establishment_id', 'month')
            .annotate(
                count_received=Count('id'),
                count_approved=Count('id', filter=Q(status="APPROVED")),
                count_rejected=Count('id', filter=Q(status="REJECTED")),
                count_canceled=Count('id', filter=Q(status="CANCELED")),
            )
            .order_by('establishment_id', 'month')
        )

        # Initialiser les statistiques avec des valeurs par défaut
        stats = defaultdict(lambda: {
            month: {
                "count_received": 0,
                "count_approved": 0,
                "count_rejected": 0,
                "count_canceled": 0,
            } for month in range(1, 13)
        })

        # Parcourir les données et remplir les statistiques
        for item in data:
            establishment_id = item['establishment_id']
            month = item['month']
            stats[establishment_id][month] = {
                "count_received": item["count_received"],
                "count_approved": item["count_approved"],
                "count_rejected": item["count_rejected"],
                "count_canceled": item["count_canceled"],
            }

        # Si aucun établissement n'est fourni, calculer les totaux globaux par mois
        if establishments is None:
            global_stats = {
                month: {
                    "count_received": 0,
                    "count_approved": 0,
                    "count_rejected": 0,
                    "count_canceled": 0,
                } for month in range(1, 13)
            }
            for establishment_data in stats.values():
                for month, values in establishment_data.items():
                    global_stats[month]["count_received"] += values["count_received"]
                    global_stats[month]["count_approved"] += values["count_approved"]
                    global_stats[month]["count_rejected"] += values["count_rejected"]
                    global_stats[month]["count_canceled"] += values["count_canceled"]

            return {"global_totals": global_stats}

        # Retourner les statistiques structurées par établissement
        return dict(stats)

    def __str__(self):
        return str(self.id)


    # Create your models here.
class BeneficiaryGroup(models.Model):
    number = models.CharField(max_length=255, editable=False, null=True)
    name = models.CharField(max_length=255)
    image = models.ForeignKey('medias.File', on_delete=models.SET_NULL, related_name='beneficiary_group_image', null=True)
    description = models.TextField(default='', null=True)
    observation = models.TextField(default='', null=True)
    is_active = models.BooleanField(default=True, null=True)
    folder = models.ForeignKey('medias.Folder', on_delete=models.SET_NULL, null=True)
    company = models.ForeignKey('companies.Company', on_delete=models.SET_NULL, related_name='company_beneficiary_groups', null=True)
    creator = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, related_name='beneficiary_group_former', null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return self.name

    # Create your models here.
class BeneficiaryGroupItem(models.Model):
    beneficiary = models.ForeignKey('human_ressources.Beneficiary', on_delete=models.SET_NULL, related_name='beneficiary_items', null=True)
    beneficiary_group = models.ForeignKey('human_ressources.BeneficiaryGroup', on_delete=models.SET_NULL, related_name='beneficiary_group_items', null=True)
    creator = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, related_name='beneficiary_group_item_former', null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return str(self.id)