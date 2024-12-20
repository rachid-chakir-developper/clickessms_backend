from django.db import models
from datetime import datetime, date, timedelta
import random
from django.utils import timezone
from decimal import Decimal, ROUND_HALF_UP

from django.db.models import Count, Q, F, ExpressionWrapper, IntegerField, Sum
from django.db.models.functions import ExtractMonth, TruncDay
from collections import defaultdict

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
    def monthly_statistics(self, year, establishments=None, company=None):
        # Filtrer les données de base
        queryset = self.objects.filter(beneficiary__company=company)

        if establishments:
            # Filtrer uniquement pour les établissements spécifiés
            queryset = queryset.filter(establishments__in=establishments)

        # Calculer le nombre de jours pour chaque enregistrement
        queryset = queryset.annotate(
            days_present=ExpressionWrapper(
                F('release_date') - F('entry_date'),
                output_field=IntegerField()
            )
        )

        # Annoter et grouper les données
        data = (
            queryset
            .values('establishments__id')  # Utilisation de l'ID
            .annotate(
                month=ExtractMonth('entry_date'),
                total_entries=Count('id', filter=Q(entry_date__year=year)),
                total_releases=Count('id', filter=Q(release_date__year=year)),
                total_due=Count('id', filter=Q(due_date__year=year)),
                total_days_present=Count(
                    'days_present',
                    filter=Q(entry_date__year=year) & Q(release_date__isnull=False)
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
                "total_days_present": 0
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
                "total_days_present": item['total_days_present'],
            }

        # Si aucun établissement n'est fourni, retourner les totaux globaux
        if establishments is None:
            totals = {
                month: {
                    "total_entries": 0,
                    "total_releases": 0,
                    "total_due": 0,
                    "total_days_present": 0
                }
                for month in range(1, 13)
            }
            for establishment, monthly_data in stats.items():
                for month, values in monthly_data.items():
                    totals[month]["total_entries"] += values["total_entries"]
                    totals[month]["total_releases"] += values["total_releases"]
                    totals[month]["total_due"] += values["total_due"]
                    totals[month]["total_days_present"] += values["total_days_present"]
            return {"global_totals": totals}

        return dict(stats)

    def __str__(self):
        return self.id

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