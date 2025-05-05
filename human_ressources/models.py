from django.db import models
from django.utils.timezone import make_aware, is_naive, now
from datetime import datetime, date, timedelta
import random
from django.utils import timezone
from decimal import Decimal, ROUND_HALF_UP

from django.db.models import Count, Q, F, ExpressionWrapper, IntegerField, Sum, Case, When, Value, DateTimeField
from django.db.models.functions import ExtractMonth, TruncDay, Greatest, TruncDate
from collections import defaultdict
from calendar import monthrange

from planning.models import EmployeeAbsenceItem


GENDERS = [
    ("MALE", "Homme"),
    ("FEMALE", "Femme"),
    ("NOT_SPECIFIED", "Non spécifié"),
]

# Create your models here.
class Employee(models.Model):
    number = models.CharField(max_length=255, editable=False, null=True)
    registration_number = models.CharField(max_length=255, null=True)
    genderh = models.ForeignKey('data_management.HumanGender', on_delete=models.SET_NULL, null=True)
    gender = models.CharField(max_length=50, choices=GENDERS, default="NOT_SPECIFIED", null=True, blank=True)
    preferred_name = models.CharField(max_length=255, null=True)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    email = models.EmailField(blank=False, max_length=255, verbose_name="email", null=True)
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
    web_site = models.URLField(max_length=255, null=True)
    other_contacts = models.CharField(max_length=255, null=True)
    iban = models.CharField(max_length=255, null=True)
    bic = models.CharField(max_length=255, null=True)
    bank_name = models.CharField(max_length=255, null=True)
    description = models.TextField(default='', null=True)
    observation = models.TextField(default='', null=True)
    signature = models.ForeignKey('medias.File', on_delete=models.SET_NULL, related_name='signature_employees', null=True)
    job_candidate = models.ForeignKey('recruitment.JobCandidate', on_delete=models.SET_NULL, related_name='employees', null=True)
    establishments = models.ManyToManyField('companies.Establishment', related_name='employees')
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
        managed_company = self.managed_companies.filter(company=self.company, user__isnull=False).first()
        return managed_company.user if managed_company else self.employee_user.all().first()

    @property
    def sce_roles(self):
        sce_members = self.sce_members.filter(is_deleted=False)
        roles = [f"{sce_member.role}_IN_CSE" for sce_member in sce_members]
        if roles:
            roles.insert(0, 'MEMBER_IN_SCE')
        return roles
    def can_manage_sce(self):
        """
        Vérifie si l'employé peut gérer le SCE en fonction de son rôle.
        """
        # Rôles autorisés pour gérer le SCE
        roles_autorises = ['PRESIDENT']
        
        # Vérifie si l'employé est un membre SCE avec l'un des rôles autorisés
        return self.sce_members.filter(is_active=True, is_deleted=False, role__in=roles_autorises).exists()
    def is_member_of_sce(self):
        return self.sce_members.filter(is_active=True, is_deleted=False).exists()
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
            else:
                rounded_remaining_days = float(rounded_remaining_days)
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
    genderh = models.ForeignKey('data_management.HumanGender', on_delete=models.SET_NULL, null=True)
    gender = models.CharField(max_length=50, choices=GENDERS, default="NOT_SPECIFIED", null=True, blank=True)
    preferred_name = models.CharField(max_length=255, null=True)
    first_name = models.CharField(max_length=255, null=True)
    last_name = models.CharField(max_length=255, null=True)
    email = models.EmailField(blank=False, max_length=255, verbose_name="email", null=True)
    photo = models.ForeignKey('medias.File', on_delete=models.SET_NULL, related_name='beneficiary_photo', null=True)
    cover_image = models.ForeignKey('medias.File', on_delete=models.SET_NULL, related_name='beneficiary_cover_image', null=True)
    birth_date = models.DateTimeField(null=True)
    birth_address = models.CharField(max_length=255, null=True)
    birth_city = models.CharField(max_length=255, null=True)
    birth_country = models.CharField(max_length=255, null=True)
    nationality = models.CharField(max_length=255, null=True)
    professional_status = models.ForeignKey('data_management.ProfessionalStatus', on_delete=models.SET_NULL, related_name='beneficiaries', null=True)
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

    @property
    def age(self):
        """
        Retourne l'âge du bénéficiaire sous le format :
        - 'X ans et Y mois'
        - 'X ans' (si Y mois = 0)
        - 'Y mois' (si < 1 an)
        """
        if self.birth_date:
            today = date.today()
            birth_date = self.birth_date.date() if isinstance(self.birth_date, datetime) else self.birth_date

            years = today.year - birth_date.year
            months = today.month - birth_date.month

            # Ajuster si le mois actuel est avant le mois de naissance
            if months < 0:
                years -= 1
                months += 12

            # Gestion des différents cas d'affichage
            if years == 0:
                return f"{months} mois" if months > 0 else "Nouveau-né"
            elif months == 0:
                return f"{years} ans"
            else:
                return f"{years} ans et {months} mois"

        return None  # Si la date de naissance n'est pas renseignée

    @property
    def age_exact(self):
        """
        Calculate and return the beneficiary's age as a float based on the birth_date.
        The age is calculated in years, including fractions of a year.
        """
        if self.birth_date:
            today = date.today()
            # Convert birth_date to a date object if it's a datetime
            birth_date = self.birth_date.date() if isinstance(self.birth_date, datetime) else self.birth_date
            # Calculate the difference in days
            delta = today - birth_date
            # Convert days to years with decimal precision
            age = delta.days / 365.25  # Using 365.25 to account for leap years
            return round(age, 2)  # Round the age to 2 decimal places
        return None  # Return None if birth_date is not set

    def get_custom_field_value(self, label):
        """
        Retourne la valeur lisible du champ personnalisé correspondant au label donné.
        Prend en charge les champs à options (SELECT, RADIO, CHECKBOX...).
        """
        try:
            # Recherche du champ personnalisé
            custom_field_value = self.custom_field_values.select_related('custom_field').get(custom_field__label=label)
            field = custom_field_value.custom_field

            # Champs à choix multiples
            if field.field_type in ['SELECT_MULTIPLE', 'CHECKBOX']:
                selected_values = custom_field_value.value.split(',') if custom_field_value.value else []
                labels = field.options.filter(value__in=selected_values).values_list('label', flat=True)
                return ', '.join(labels)

            # Champs à choix unique
            elif field.field_type in ['SELECT', 'RADIO']:
                option = field.options.filter(value=custom_field_value.value).first()
                return option.label if option else custom_field_value.value

            # Autres types (texte, nombre, date...)
            return custom_field_value.value

        except Exception as e:
            return ''

    @property
    def balance_details(self):
        """
        Propriété qui calcule les détails du solde et les totaux pour un bénéficiaire,
        regroupés par type de dotation.
        Retourne un dictionnaire contenant :
        - Les détails des soldes par type de dotation.
        - Les totaux globaux (solde initial total, dotations versées, dépenses totales, et balance).
        """

        # Initialiser un dictionnaire pour stocker les détails par type de dotation
        details = defaultdict(lambda: {"initial_balance": 0, "endowments_paid": 0, "expenses": 0})

        # Calculer le solde initial par type de dotation (pour les dotations commencées)
        dotations = self.beneficiary_endowment_entries.filter(
            starting_date__lte=now()
        ).values('endowment_type__name').annotate(total_initial=Sum('initial_balance'))

        for dotation in dotations:
            details[dotation['endowment_type__name']]['initial_balance'] = float(dotation['total_initial']) or 0

        # Calculer les dotations versées par type
        endowments = self.endowment_payments.values('endowment_type__name').annotate(
            total_paid=Sum('amount')
        )
        for endowment in endowments:
            details[endowment['endowment_type__name']]['endowments_paid'] = float(endowment['total_paid']) or 0

        # Calculer les dépenses totales par type si applicable (ou globalement si non lié)
        expenses = self.beneficiary_expenses.values('endowment_type__name').annotate(
            total_spent=Sum('amount')
        )
        for expense in expenses:
            details[expense['endowment_type__name']]['expenses'] = float(expense['total_spent']) or 0

        # Calculer les totaux globaux
        total_initial_balance = sum(d['initial_balance'] for d in details.values())
        total_endowments_paid = sum(d['endowments_paid'] for d in details.values())
        total_expenses = sum(d['expenses'] for d in details.values())
        total_balance = total_initial_balance + total_endowments_paid - total_expenses  # Balance = soldes initiaux + versements - dépenses

        # Structurer la réponse
        result = {
            "details": dict(details),  # Convertir le defaultdict en dict pour le rendre sérialisable
            "totals": {
                "balance": float(total_balance),  # Balance = initial_balance + endowments_paid - expenses
                "endowments_paid": float(total_endowments_paid),
                "expenses": float(total_expenses),
            },
        }
        return result

    @property
    def balance(self):
        """
        Propriété qui calcule la balance totale du bénéficiaire :
        Solde initial + Paiements - Dépenses.
        """
        total_initial_balance = sum(
            entry.initial_balance for entry in self.beneficiary_endowment_entries.filter(starting_date__lte=now())
        )
        total_endowments_paid = sum(payment.amount for payment in self.endowment_payments.all())
        total_expenses = sum(expense.amount for expense in self.beneficiary_expenses.all())
        
        # Calcul de la balance (solde initial + paiements - dépenses)
        return total_initial_balance + total_endowments_paid - total_expenses

    @property
    def total_expenses(self):
        """
        Propriété qui calcule les dépenses totales du bénéficiaire.
        Retourne la somme des dépenses.
        """
        return sum(expense.amount for expense in self.beneficiary_expenses.all())

    @property
    def total_payments(self):
        """
        Propriété qui calcule les paiements totaux effectués pour le bénéficiaire.
        Retourne la somme des paiements effectués.
        """
        return sum(payment.amount for payment in self.endowment_payments.all())
        
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
        return str(self.id)

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

    class Meta:
        ordering = ['starting_date']

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

    class Meta:
        ordering = ['starting_date']

    def __str__(self):
        return self.id

# Create your models here.
class BeneficiaryEndowmentEntry(models.Model):
    beneficiary = models.ForeignKey(Beneficiary, on_delete=models.SET_NULL, null=True, related_name='beneficiary_endowment_entries')
    endowment_type = models.ForeignKey('data_management.TypeEndowment', on_delete=models.SET_NULL, related_name='beneficiary_endowment_entries', null=True)
    initial_balance = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    starting_date = models.DateTimeField(null=True)
    ending_date = models.DateTimeField(null=True)
    creator = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    class Meta:
        ordering = ['starting_date']

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

    class Meta:
        ordering = ['entry_date']  # Tri par date d'entrée décroissante (du plus récent au plus ancien)

    @classmethod
    def monthly_presence_statistics(cls, year, establishments=None, company=None):
        year = int(year)
        today = make_aware(datetime.today())

        # Convertir les datetime naïfs en datetime conscients des fuseaux horaires
        start_of_year = datetime(year, 1, 1, 00, 00, 00)
        end_of_year = datetime(year, 12, 31, 23, 59, 59)

        start_of_year = make_aware(start_of_year)
        end_of_year = make_aware(end_of_year)
        
        # Si les dates sont naïves, les rendre conscientes
        # Étape 1 : Filtrer les enregistrements de base
        queryset = cls.objects.filter(
            Q(entry_date__lt=end_of_year),
            Q(release_date__isnull=True) | Q(release_date__gte=start_of_year),
            beneficiary__is_deleted=False,
        )
        # Filtrer par société si fourni
        if company:
            queryset = queryset.filter(beneficiary__company=company)

        # Filtrer par établissements si fourni
        if establishments:
            queryset = queryset.filter(establishments__in=establishments)

        # Étape 2 : Calculer les statistiques mensuelles
        monthly_data = defaultdict(lambda: {month: 
            {
            "total_entries": 0,
            "entry_beneficiary_entries": [],
            "total_releases": 0,
            "release_beneficiary_entries": [],
            "total_due": 0,
            "due_beneficiary_entries": [],
            "total_days_present": 0,
            "total_days_present": 0,
            "present_at_end_of_month": 0,
            }
             for month in range(1, 13)})
        for entry in queryset:
            for establishment in entry.establishments.all():
                # Ajuster start_date en fonction de entry_date
                if entry.entry_date and entry.entry_date.year == year:
                    monthly_data[establishment.id][entry.entry_date.month]["total_entries"] += 1
                    monthly_data[establishment.id][entry.entry_date.month]["entry_beneficiary_entries"].append(entry)
                if entry.release_date and entry.release_date.year == year:
                    monthly_data[establishment.id][entry.release_date.month]["total_releases"] += 1
                    monthly_data[establishment.id][entry.entry_date.month]["release_beneficiary_entries"].append(entry)
                if entry.due_date and entry.due_date.year == year:
                    monthly_data[establishment.id][entry.due_date.month]["total_due"] += 1
                    monthly_data[establishment.id][entry.entry_date.month]["due_beneficiary_entries"].append(entry)
                start_date = entry.entry_date if entry.entry_date >= start_of_year else start_of_year
                
                # Ajuster end_date en fonction de release_date
                if entry.release_date is None:
                    end_date = end_of_year
                elif entry.release_date > end_of_year:
                    end_date = end_of_year
                else:
                    end_date = entry.release_date
                
                # Assurez-vous que start_date et end_date sont conscients
                start_date = make_aware(start_date) if is_naive(start_date) else start_date
                end_date = make_aware(end_date) if is_naive(end_date) else end_date
                # Rendre start_date et end_date conscients si nécessaire
                while start_date <= end_date:
                    end_date_aux = end_date
                    month_start = datetime(start_date.year, start_date.month, 1, 00, 00, 00)
                    month_end = (month_start + timedelta(days=32)).replace(day=1) - timedelta(seconds=1)
                    # Rendre month_start et month_end conscients si nécessaire
                    month_start = make_aware(month_start)
                    month_end = make_aware(month_end)
                    if start_date.year == today.year and start_date.month == today.month:
                        end_date_aux = min(end_date_aux, today)

                    days_in_month = (min(end_date_aux, month_end) - max(start_date, month_start)).days + 1
                    if (
                        entry.release_date is not None 
                        and entry.release_date <= month_end 
                        and entry.release_date.month == month_end.month
                        and entry.release_date.date() != start_date.date()
                    ):
                        days_in_month += 1

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
        queryset = cls.objects.filter(beneficiary__company=company, beneficiary__is_deleted=False)

        if establishments:
            # Filtrer uniquement pour les établissements spécifiés
            queryset = queryset.filter(establishments__in=establishments)

        # Filtrer les bénéficiaires toujours présents dans le mois spécifié
        queryset = queryset.filter(
            Q(entry_date__lt=end_date),  # Entré avant ou pendant le mois
            Q(release_date__isnull=True) | Q(release_date__gt=end_date)  # Toujours présent après le dernier jour du mois
        ).order_by('beneficiary__last_name', 'beneficiary__first_name')

        # Regrouper par établissement
        result = {}
        for establishment in queryset.values_list('establishments', flat=True).distinct():
            establishment_queryset = queryset.filter(establishments=establishment)
            result[establishment] = list(establishment_queryset)

        return result

    @classmethod
    def monthly_present_beneficiaries(cls, year, establishments=None, company=None):
        """
        Retourne un dictionnaire contenant les présences par mois pour une année donnée.

        :param year: Année pour laquelle récupérer les données
        :param establishments: Liste d'établissements (optionnel)
        :param company: Société (optionnel)
        :return: Dictionnaire {mois: {"presences": []}}
        """
        year = int(year)

        # Début et fin de l'année
        start_of_year = make_aware(datetime(year, 1, 1, 0, 0, 0))
        end_of_year = make_aware(datetime(year, 12, 31, 23, 59, 59))

        # Filtrer les enregistrements de base
        queryset = cls.objects.filter(
            Q(release_date__isnull=True) | Q(release_date__gt=start_of_year),  # Toujours actifs ou sortis après le début de l'année
            entry_date__lte=end_of_year,  # Entrés avant ou pendant l'année
            beneficiary__is_deleted=False,
        )

        # Filtrer par société si fourni
        if company:
            queryset = queryset.filter(beneficiary__company=company)

        # Filtrer par établissements si fourni
        if establishments:
            queryset = queryset.filter(establishments__in=establishments)

        # Initialiser le dictionnaire pour les données mensuelles
        monthly_data = defaultdict(lambda: {month: {
            "presences": [],
        } for month in range(1, 13)})

        # Calculer les présences par mois
        for month in range(1, 13):
            start_of_month = make_aware(datetime(year, month, 1, 0, 0, 0))
            if month == 12:
                end_of_month = make_aware(datetime(year + 1, 1, 1, 0, 0, 0)) - timedelta(seconds=1)
            else:
                end_of_month = make_aware(datetime(year, month + 1, 1, 0, 0, 0)) - timedelta(seconds=1)

            # Ajouter les présences pour le mois
            presences = queryset.filter(
                Q(release_date__isnull=True) | Q(release_date__gte=start_of_month),  # Pas encore sorti ou sortie après le début du mois
                entry_date__lte=end_of_month,  # Entré avant ou pendant le mois
            ).order_by('beneficiary__last_name', 'beneficiary__first_name')

            # Grouper les admissions par établissement
            for presence in presences:
                for establishment in presence.establishments.all():
                    monthly_data[establishment.id][month]["presences"].append(presence)
            # On ajoute des entrées pour les mois manquants pour chaque établissement
        establishments_ids = establishments or queryset.values_list('establishments', flat=True).distinct()
        for establishment in establishments_ids:
            if establishment.id not in monthly_data:
                    monthly_data[establishment.id] = {month: {"presences": []} for month in range(1, 13)}

        return {est_id: dict(months) for est_id, months in monthly_data.items()}

    @classmethod
    def monthly_beneficiary_attendance(cls, year, establishments=None, company=None):
        year = int(year)
        today = make_aware(datetime.today())

        start_of_year = make_aware(datetime(year, 1, 1, 0, 0, 0))
        end_of_year = make_aware(datetime(year, 12, 31, 23, 59, 59))

        queryset = cls.objects.filter(
            Q(release_date__isnull=True) | Q(release_date__gt=start_of_year),
            entry_date__lte=end_of_year,
            beneficiary__is_deleted=False,
        )

        if company:
            queryset = queryset.filter(beneficiary__company=company)

        if establishments:
            queryset = queryset.filter(establishments__in=establishments)

        # Dictionnaire pour structurer les données
        monthly_data = defaultdict(lambda: defaultdict(list))

        # Pour chaque mois de l'année
        for month in range(1, 13):
            start_of_month = make_aware(datetime(year, month, 1, 0, 0, 0))
            if year == today.year and month == today.month:
                end_of_month = today
            else:
                if month == 12:
                    end_of_month = make_aware(datetime(year + 1, 1, 1, 0, 0, 0)) - timedelta(seconds=1)
                else:
                    end_of_month = make_aware(datetime(year, month + 1, 1, 0, 0, 0)) - timedelta(seconds=1)

            # Filtrer les présences pour ce mois
            presences = queryset.filter(
                Q(release_date__isnull=True) | Q(release_date__gte=start_of_month),
                entry_date__lte=end_of_month
            ).order_by('beneficiary__last_name', 'beneficiary__first_name')

            # Traitement des présences pour chaque bénéficiaire et établissement
            for presence in presences:
                # Calcul du nombre de jours de présence
                days_count = (min(presence.release_date or end_of_month, end_of_month) - max(presence.entry_date, start_of_month)).days + 1
                if (
                    presence.release_date is not None 
                    and presence.release_date <= end_of_month 
                    and presence.release_date.month == end_of_month.month
                    and presence.release_date.date() != start_of_month.date()
                ):
                    days_count += 1
                for establishment in presence.establishments.all():
                    monthly_data[establishment.id][presence.beneficiary.id].append({
                        "month": month,
                        "days_count": days_count
                    })

        # Structure de résultat final
        result = {}

        # Organiser les données dans la structure souhaitée
        for establishment_id, beneficiaries in monthly_data.items():
            establishment_data = []

            for beneficiary_id, presences in beneficiaries.items():
                # Organiser les présences mensuelles pour chaque bénéficiaire
                monthly_attendance = {month: {"days_count": 0} for month in range(1, 13)}
                for presence in presences:
                    month = presence["month"]
                    monthly_attendance[month] = {"days_count": presence["days_count"]}

                # Ajouter chaque bénéficiaire avec ses mois de présence
                beneficiary = Beneficiary.objects.get(id=beneficiary_id)
                establishment_data.append({
                    "beneficiary": beneficiary,
                    "monthly_attendance": monthly_attendance
                })

            # Ajouter les bénéficiaires pour cet établissement
            result[establishment_id] = establishment_data

        # Ajout des établissements sans bénéficiaires
        if establishments:
            for establishment_id in establishments:
                if establishment_id not in result:
                    result[establishment_id] = []

        return result


    @classmethod
    def count_present_beneficiaries(cls, year, month, establishments=None, company=None):
        """
        Retourne le nombre de bénéficiaires présents au dernier jour du mois pour une année donnée.
        
        :param year: Année concernée (int).
        :param month: Mois concerné (int, 1-12).
        :param establishments: QuerySet ou liste d'ID des établissements concernés (optionnel).
        :param company: Entreprise concernée (optionnel, si applicable).
        :return: Nombre de bénéficiaires présents au dernier jour du mois (int).
        """
        year = int(year)
        month = int(month)
        if month <= 0:  
            month = 12  
            year -= 1  
        elif month > 12:  
            month = 1  
            year += 1

        # Début et fin du mois spécifié
        start_date = datetime(year, month, 1)
        if month == 12:
            end_date = datetime(year + 1, 1, 1)
        else:
            end_date = datetime(year, month + 1, 1)

        # Filtrer les données de base par entreprise
        queryset = cls.objects.filter(beneficiary__company=company, beneficiary__is_deleted=False)

        if establishments:
            # Filtrer uniquement pour les établissements spécifiés
            queryset = queryset.filter(establishments__in=establishments)

        # Filtrer les bénéficiaires toujours présents à la fin du mois spécifié
        queryset = queryset.filter(
            Q(entry_date__lt=end_date),  # Entré avant ou pendant le mois
            Q(release_date__isnull=True) | Q(release_date__gt=end_date)  # Toujours présents après le dernier jour du mois
        )

        # Compter le nombre de bénéficiaires distincts présents
        return queryset.distinct().count()

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
    pre_admission_date = models.DateTimeField(null=True)  # Added pre-admission date
    reception_date = models.DateTimeField(null=True)
    genderh = models.ForeignKey('data_management.HumanGender', on_delete=models.SET_NULL, null=True)
    gender = models.CharField(max_length=50, choices=GENDERS, default="NOT_SPECIFIED", null=True, blank=True)
    preferred_name = models.CharField(max_length=255, null=True)
    first_name = models.CharField(max_length=255, null=True)
    last_name = models.CharField(max_length=255, null=True)
    email = models.EmailField(blank=False, max_length=255, verbose_name="email", null=True)
    photo = models.ForeignKey('medias.File', on_delete=models.SET_NULL, related_name='photo_beneficiary_admissions', null=True)
    birth_date = models.DateTimeField(null=True)
    birth_address = models.CharField(max_length=255, null=True)
    birth_city = models.CharField(max_length=255, null=True)
    birth_country = models.CharField(max_length=255, null=True)
    nationality = models.CharField(max_length=255, null=True)
    professional_status = models.ForeignKey('data_management.ProfessionalStatus', on_delete=models.SET_NULL, related_name='beneficiary_admissions', null=True)
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
    web_site = models.URLField(max_length=255, null=True)
    other_contacts = models.CharField(max_length=255, null=True)
    description = models.TextField(default='', null=True)
    observation = models.TextField(default='', null=True)
    beneficiary = models.ForeignKey(Beneficiary, on_delete=models.SET_NULL, null=True, related_name='beneficiary_admissions')
    files = models.ManyToManyField('medias.File', related_name='file_beneficiary_admissions')
    financier = models.ForeignKey('partnerships.Financier', on_delete=models.SET_NULL, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="DRAFT")
    response_date = models.DateTimeField(null=True)
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

    @property
    def age(self):
        """
        Retourne l'âge du bénéficiaire sous le format :
        - 'X ans et Y mois'
        - 'X ans' (si Y mois = 0)
        - 'Y mois' (si < 1 an)
        """
        if self.birth_date:
            today = date.today()
            birth_date = self.birth_date.date() if isinstance(self.birth_date, datetime) else self.birth_date

            years = today.year - birth_date.year
            months = today.month - birth_date.month

            # Ajuster si le mois actuel est avant le mois de naissance
            if months < 0:
                years -= 1
                months += 12

            # Gestion des différents cas d'affichage
            if years == 0:
                return f"{months} mois" if months > 0 else "Nouveau-né"
            elif months == 0:
                return f"{years} ans"
            else:
                return f"{years} ans et {months} mois"

        return None  # Si la date de naissance n'est pas renseignée

    @property
    def age_exact(self):
        """
        Calculate and return the beneficiary's age as a float based on the birth_date.
        The age is calculated in years, including fractions of a year.
        """
        if self.birth_date:
            today = date.today()
            # Convert birth_date to a date object if it's a datetime
            birth_date = self.birth_date.date() if isinstance(self.birth_date, datetime) else self.birth_date
            # Calculate the difference in days
            delta = today - birth_date
            # Convert days to years with decimal precision
            age = delta.days / 365.25  # Using 365.25 to account for leap years
            return round(age, 2)  # Round the age to 2 decimal places
        return None  # Return None if birth_date is not set

    @classmethod
    def monthly_statistics(cls, year, establishments=None, company=None):
        year = int(year)
        queryset = cls.objects.filter(
            company=company,
            is_deleted=False,
            reception_date__year=year
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

    @classmethod
    def monthly_admissions(cls, year, establishments=None, company=None):
        """
        Retourne un dictionnaire contenant les admissions par mois et par établissement pour une année donnée.

        :param year: Année pour laquelle récupérer les données
        :param establishments: Liste d'établissements (optionnel)
        :param company: Société (optionnel)
        :return: Dictionnaire {mois: {établissement_id: {"admissions": []}}}
        """
        year = int(year)

        # Début et fin de l'année
        start_of_year = make_aware(datetime(year, 1, 1, 0, 0, 0))
        end_of_year = make_aware(datetime(year, 12, 31, 23, 59, 59))

        # Filtrer les enregistrements de base
        queryset = cls.objects.filter(
            reception_date__gte=start_of_year,
            reception_date__lte=end_of_year,
            status__in=["APPROVED", "REJECTED"],
            is_deleted=False,
        )

        # Filtrer par société si fourni
        if company:
            queryset = queryset.filter(company=company)

        # Filtrer par établissements si fourni
        if establishments:
            queryset = queryset.filter(establishments__in=establishments)

        # Initialiser le dictionnaire pour les données mensuelles par établissement
        monthly_data = defaultdict(lambda: {month: {
            "admissions": [],
        } for month in range(1, 13)})

        # Calculer les admissions par mois et par établissement
        for month in range(1, 13):
            start_of_month = make_aware(datetime(year, month, 1, 0, 0, 0))
            if month == 12:
                end_of_month = make_aware(datetime(year + 1, 1, 1, 0, 0, 0)) - timedelta(seconds=1)
            else:
                end_of_month = make_aware(datetime(year, month + 1, 1, 0, 0, 0)) - timedelta(seconds=1)

            # Ajouter les admissions pour le mois
            admissions = queryset.filter(
                reception_date__gte=start_of_month,
                reception_date__lte=end_of_month
            )

            # Grouper les admissions par établissement
            for admission in admissions:
                for establishment in admission.establishments.all():
                    monthly_data[establishment.id][month]["admissions"].append(admission)
            # On ajoute des entrées pour les mois manquants pour chaque établissement
        establishments_ids = establishments or queryset.values_list('establishments', flat=True).distinct()
        for establishment in establishments_ids:
            if establishment.id not in monthly_data:
                monthly_data[establishment.id] = {month: {"admissions": []} for month in range(1, 13)}

        return {est_id: dict(months) for est_id, months in monthly_data.items()}


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

# Create your models here.
class CareerEntry(models.Model):
    TYPE_CHOICES = [
        ("EDUCATION", "Scolarité"),
        ("INTERNSHIP", "Stage"),
        ("JOB", "Emploi"),
        ("TRAINING", "Formation"),
        ("VOLUNTEERING", "Bénévolat"),
        ("OTHER", "Autre"),
    ]
    number = models.CharField(max_length=255, editable=False, null=True)
    beneficiary = models.ForeignKey('human_ressources.Beneficiary', on_delete=models.SET_NULL, related_name='career_entries', null=True)
    career_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default="EDUCATION")
    institution = models.CharField(max_length=255, blank=False, null=True)
    professional_status = models.ForeignKey('data_management.ProfessionalStatus', on_delete=models.SET_NULL, related_name='career_entries', null=True)
    title = models.CharField(max_length=255, blank=False, null=True)
    starting_date = models.DateField(null=True)
    ending_date = models.DateField(null=True)
    email = models.EmailField(blank=False, max_length=255, verbose_name="email", null=True)
    full_address = models.TextField(default='', null=True)
    address = models.TextField(default='', null=True)
    additional_address = models.TextField(default='', null=True)
    latitude = models.CharField(max_length=255, null=True)
    longitude = models.CharField(max_length=255, null=True)
    city = models.CharField(max_length=255, null=True)
    country = models.CharField(max_length=255, null=True)
    zip_code = models.CharField(max_length=255, null=True)
    mobile = models.CharField(max_length=255, null=True)
    fix = models.CharField(max_length=255, null=True)
    fax = models.CharField(max_length=255, null=True)
    web_site = models.URLField(max_length=255, null=True)
    description = models.TextField(default='', null=True)
    other_contacts = models.CharField(max_length=255, null=True)
    company = models.ForeignKey('companies.Company', on_delete=models.SET_NULL, related_name='career_entries', null=True)
    creator = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, related_name='former_career_entries', null=True)
    is_deleted = models.BooleanField(default=False, null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    class Meta:
        ordering = ['starting_date'] 

class Advance(models.Model):
    """
    Modèle représentant une demande d'acompte faite par un employé.
    """
    STATUS_CHOICES = [
        ("PENDING", "En attente"),
        ("APPROVED", "Approuvé"),
        ("REJECTED", "Rejeté"),
        ("MODIFIED", "Modifié"),
    ]
    
    number = models.CharField(max_length=255, editable=False, null=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    month = models.DateField(help_text="Mois pour lequel l'acompte est demandé")
    reason = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="PENDING")
    comments = models.TextField(blank=True, null=True, help_text="Commentaires de la RH")
    employee = models.ForeignKey('human_ressources.Employee', on_delete=models.CASCADE, related_name='advances')
    validated_by = models.ForeignKey('human_ressources.Employee', on_delete=models.SET_NULL, related_name='validated_advances', null=True, blank=True)
    validation_date = models.DateTimeField(null=True, blank=True)
    company = models.ForeignKey('companies.Company', on_delete=models.SET_NULL, related_name='company_advances', null=True)
    creator = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, related_name='advance_former', null=True)
    is_deleted = models.BooleanField(default=False, null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)
    
    def save(self, *args, **kwargs):
        # Générer le numéro unique lors de la sauvegarde si ce n'est pas déjà défini
        if not self.number:
            self.number = self.generate_unique_number()

        super(Advance, self).save(*args, **kwargs)

    def generate_unique_number(self):
        # Utilisation de la date et de l'heure actuelles pour générer un numéro unique
        current_time = datetime.now()
        number_suffix = current_time.strftime("%Y%m%d%H%M%S")
        number_prefix = 'AC'  # Préfixe pour Acompte
        number = f'{number_prefix}{number_suffix}'

        # Vérifier s'il est unique dans la base de données
        while Advance.objects.filter(number=number).exists():
            number_suffix = current_time.strftime("%Y%m%d%H%M%S")
            number = f'{number_prefix}{number_suffix}'

        return number
    
    class Meta:
        ordering = ['-created_at']  # Tri par date de création décroissante
        
    def __str__(self):
        return f"Acompte {self.number} - {self.employee.first_name} {self.employee.last_name} - {self.amount} €"
