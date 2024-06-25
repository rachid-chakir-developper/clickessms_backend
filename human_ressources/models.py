from django.db import models
from datetime import datetime
import random
from django.utils.timezone import now
from planning.models import EmployeeAbsenceItem

# Create your models here.
class Employee(models.Model):
    number = models.CharField(max_length=255, editable=False, null=True)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    email = models.EmailField(blank=False, max_length=255, verbose_name="email")
    photo = models.ForeignKey('medias.File', on_delete=models.SET_NULL, related_name='employee_photo', null=True)
    cover_image = models.ForeignKey('medias.File', on_delete=models.SET_NULL, related_name='employee_cover_image', null=True)
    position = models.CharField(max_length=255, null=True)
    birth_date = models.DateTimeField(null=True)
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
    def current_contract(self):
        current_time = now()
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
    ]
    number = models.CharField(max_length=255, editable=False, null=True)
    title = models.CharField(max_length=255, null=True)
    document = models.ForeignKey('medias.File', on_delete=models.SET_NULL, related_name='employee_contrat_doucument', null=True)
    starting_date = models.DateTimeField(null=True)
    ending_date = models.DateTimeField(null=True)
    position = models.CharField(max_length=255, null=True)
    monthly_gross_salary = models.DecimalField("Monthly Gross Salary", max_digits=10, decimal_places=2, default=0.0)
    salary = models.DecimalField("Annual Gross Salary", max_digits=10, decimal_places=2, help_text="Optional if Monthly Gross Salary is provided", null=True, blank=True)
    started_at = models.DateTimeField(null=True)
    ended_at = models.DateTimeField(null=True)
    initial_annual_leave_days = models.DecimalField("Initial Annual Leave Days (CP)", max_digits=5, decimal_places=2, default=25.0)
    initial_rtt_days = models.DecimalField("Initial RTT Days", max_digits=5, decimal_places=2, default=10.0)
    initial_ct_days = models.DecimalField("Initial Temporary Leave Days (CT)", max_digits=5, decimal_places=2, default=5.0)
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
    def rest_leave_days(self):
        # il faut revoir ça pour calculer aussi les jours reportés
        current_year = now().year
        absences = EmployeeAbsenceItem.objects.filter(employee=self.employee, employee_absence__starting_date_time__year=current_year)
        total_days_taken = sum((absence.employee_absence.ending_date_time - absence.employee_absence.starting_date_time).days + 1
            for absence in absences if absence.employee_absence.starting_date_time and absence.employee_absence.ending_date_time)
        remaining_days = self.initial_annual_leave_days - total_days_taken
        return remaining_days

    def __str__(self):
        return str(self.id)

# Create your models here.
class EmployeeContractEstablishment(models.Model):
    employee_contract = models.ForeignKey(EmployeeContract, on_delete=models.SET_NULL, null=True, related_name='establishments')
    establishment = models.ForeignKey('companies.Establishment', on_delete=models.SET_NULL, related_name='employee_contract_establishment', null=True)
    creator = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, related_name='employee_contract_establishment_former', null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

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
        return self.name

# Create your models here.
class BeneficiaryEntry(models.Model):
    beneficiary = models.ForeignKey(Beneficiary, on_delete=models.SET_NULL, null=True, related_name='beneficiary_entries')
    entry_date = models.DateTimeField(null=True)
    release_date = models.DateTimeField(null=True)
    establishments = models.ManyToManyField('companies.Establishment', related_name='establishments_beneficiary_entries')
    internal_referents = models.ManyToManyField('human_ressources.Employee', related_name='referents_beneficiary_entries')
    creator = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return self.name

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