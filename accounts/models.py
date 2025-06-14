from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.text import slugify
import string
import random
from the_mailer.services.accounts_services import get_default_sent_email

# Create your models here.
class Role(models.Model):
    ROLE_CHOICES = [
        ('SUPER_ADMIN', 'Super admin'),
        ('ADMIN', 'Admin'),
        ('MANAGER', 'Employé'),
        ('SCE_MANAGER', 'Responsable CSE'),
        ('GOVERNANCE_MANAGER', 'Responsable Gouvernance'),
        ('QUALITY_MANAGER', 'Responsable Qualité'),
        ('ACTIVITY_MANAGER', 'Responsable Activité'),
        ('SUPPORT_WORKER', 'Accompagnant'),
        ('ADMINISTRATIVE_MANAGER', 'Responsable Administratif'),
        ('HR_MANAGER', 'Responsable RH'),
        ('FACILITY_MANAGER', 'Responsable Services Généraux'),
        ('FINANCE_MANAGER', 'Responsable Finance'),
        ('EMPLOYEE', 'Employee'),
        ('MECHANIC', 'Garagiste'),
    ]
    name = models.CharField(max_length=100, choices=ROLE_CHOICES, unique=True)
    description = models.TextField(null=True, blank=True)
    def __str__(self):
        return self.name

# Create your models here.
class User(AbstractUser):

    ACCOUNT_TYPES = [
        ("PRO", "Pro"),
        ("STANDARD", "standard"),
    ]
    email = models.EmailField(blank=False, max_length=255, verbose_name="email", unique=True)
    account_type = models.CharField(max_length=50, choices=ACCOUNT_TYPES, default= "PRO", null=True)
    photo = models.ForeignKey('medias.File', on_delete=models.SET_NULL, related_name='user_photo', null=True)
    cover_image = models.ForeignKey('medias.File', on_delete=models.SET_NULL, related_name='user_cover_image', null=True)
    is_cgu_accepted = models.BooleanField(null=True)
    is_online = models.BooleanField(default=False, null=True)
    is_must_change_password = models.BooleanField(default=True, null=True)
    number_current_connexions = models.PositiveIntegerField(default=0, null=True)
    description = models.TextField(default='', null=True)
    observation = models.TextField(default='', null=True)
    current_latitude = models.CharField(max_length=255, null=True)
    current_longitude = models.CharField(max_length=255, null=True)
    company = models.ForeignKey('companies.Company', on_delete=models.SET_NULL, related_name='company_admins', null=True)
    current_company = models.ForeignKey('companies.Company', on_delete=models.SET_NULL, related_name='current_company_users', null=True)
    employee = models.ForeignKey('human_ressources.Employee', on_delete=models.SET_NULL, related_name='employee_user', null=True)
    governance_member = models.ForeignKey('governance.GovernanceMember', on_delete=models.SET_NULL, related_name='governance_member_user', null=True)
    partner = models.ForeignKey('partnerships.Partner', on_delete=models.SET_NULL, related_name='partner_user', null=True)
    financier = models.ForeignKey('partnerships.Financier', on_delete=models.SET_NULL, related_name='financier_user', null=True)
    supplier = models.ForeignKey('purchases.Supplier', on_delete=models.SET_NULL, related_name='supplier_user', null=True)
    creator = models.ForeignKey('self', on_delete=models.SET_NULL, null=True)
    is_deleted = models.BooleanField(default=False, null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)
    number_current_openai_tokens = models.PositiveIntegerField(default=5, null=False)

    roles = models.ManyToManyField(Role, related_name='users', blank=True)

    USERNAME_FIELD = "username"
    EMAIL_FIELD = "email"

    def add_company(self, company):
        if not self.managed_companies.filter(company=company).exists():
            UserCompany.objects.create(user=self, company=company)
            return True
        return False
        
    @property
    def the_current_company(self):
        return self.current_company if self.current_company is not None else self.company

    def get_current_company(self):
        return self.current_company if self.current_company is not None else self.company

    def remove_company(self, company):
        user_company = self.managed_companies.filter(company=company).first()
        if user_company:
            user_company.delete()
            return True
        return False

    def get_employee_in_company(self, company=None):
        company = company or self.current_company or self.company
        user_company = self.managed_companies.filter(company=company, employee__isnull=False).first()
        return user_company.employee if user_company and user_company.employee else self.employee

    def set_employee_for_company(self, employee_id, company=None):
        from human_ressources.models import Employee
        company = company or self.current_company or self.company
        try:
            employee = Employee.objects.get(id=employee_id)
        except Employee.DoesNotExist:
            employee = None
        user_company, created = self.managed_companies.get_or_create(company=company)
        user_company.employee = employee
        user_company.save()

    def get_governance_member_in_company(self, company=None):
        company = company or self.current_company or self.company
        user_company = self.managed_companies.filter(company=company).first()
        return user_company.governance_member if user_company and user_company.governance_member else self.governance_member

    def set_governance_member_for_company(self, governance_member_id, company=None):
        from governance.models import GovernanceMember
        company = company or self.current_company or self.company
        try:
            governance_member = GovernanceMember.objects.get(id=governance_member_id)
        except GovernanceMember.DoesNotExist:
            governance_member = None
        user_company, created = self.managed_companies.get_or_create(company=company)
        user_company.governance_member = governance_member
        user_company.save()

    def get_partner_in_company(self, company=None):
        company = company or self.current_company or self.company
        user_company = self.managed_companies.filter(company=company).first()
        return user_company.partner if user_company and user_company.partner else self.partner

    def set_partner_for_company(self, partner_id, company=None):
        from partnerships.models import Partner
        company = company or self.current_company or self.company
        try:
            partner = Partner.objects.get(id=partner_id)
        except Partner.DoesNotExist:
            partner = None
        user_company, created = self.managed_companies.get_or_create(company=company)
        user_company.partner = partner
        user_company.save()

    def get_financier_in_company(self, company=None):
        company = company or self.current_company or self.company
        user_company = self.managed_companies.filter(company=company).first()
        return user_company.financier if user_company and user_company.financier else self.financier

    def set_financier_for_company(self, financier_id, company=None):
        from partnerships.models import Financier
        company = company or self.current_company or self.company
        try:
            financier = Financier.objects.get(id=financier_id)
        except Financier.DoesNotExist:
            financier = None
        user_company, created = self.managed_companies.get_or_create(company=company)
        user_company.financier = financier
        user_company.save()

    def get_supplier_in_company(self, company=None):
        company = company or self.current_company or self.company
        user_company = self.managed_companies.filter(company=company).first()
        return user_company.supplier if user_company and user_company.supplier else self.supplier

    def set_supplier_for_company(self, supplier_id, company=None):
        from purchases.models import Supplier
        company = company or self.current_company or self.company
        try:
            supplier = Supplier.objects.get(id=supplier_id)
        except Supplier.DoesNotExist:
            supplier = None
        user_company, created = self.managed_companies.get_or_create(company=company)
        user_company.supplier = supplier
        user_company.save()

    def sort_roles(self, roles):
        ROLE_ORDER = {role[0]: index for index, role in enumerate(Role.ROLE_CHOICES)}
        return sorted(roles, key=lambda role: ROLE_ORDER.get(role, len(ROLE_ORDER)))

    @property
    def user_roles(self):
        roles = [role.name for role in self.roles] if self.roles.exists() else []
        if self.is_superuser and 'SUPER_ADMIN' not in roles:
            roles.append('SUPER_ADMIN')
        elif not roles:
            roles.append('EMPLOYEE')
        return self.sort_roles(roles)

    def get_roles_in_company(self, company=None):
        company = company or self.current_company or self.company
        user_company = self.managed_companies.filter(company=company).first()
        roles = [role.name for role in user_company.roles.all()] if user_company and user_company.roles.exists() else []
        if self.is_superuser and 'SUPER_ADMIN' not in roles:
            roles.append('SUPER_ADMIN')
        elif not roles:
            roles.append('EMPLOYEE')
        return self.sort_roles(roles)

    def has_role_in_company(self, role_name, company=None):
        company = company or self.current_company or self.company
        user_company = self.managed_companies.filter(company=company).first()
        return user_company.roles.filter(name=role_name).exists() if user_company else self.roles.filter(name=role_name).exists()

    def has_roles_in_company(self, roles_names=None, company=None):
        if not roles_names:
            return False
        company = company or self.current_company or self.company
        user_company = self.managed_companies.filter(company=company).first()
        return user_company.roles.filter(name__in=roles_names).exists() if user_company else self.roles.filter(name__in=roles_names).exists()

    def add_role_in_company(self, role_name, company=None):
        company = company or self.current_company or self.company
        role, created = Role.objects.get_or_create(name=role_name)
        user_company, created = self.managed_companies.get_or_create(company=company)
        user_company.roles.add(role)
    def set_roles_in_company(self, roles_names=None, company=None):
        if roles_names is not None:
            company = company or self.current_company or self.company
            user_company = self.managed_companies.filter(company=company).first()
            roles = user_company.roles.all() if user_company else self.roles.all()
            for role in roles:
                if role.name not in roles_names:
                    user_company.roles.remove(role)
            for role_name in roles_names:
                self.add_role_in_company(role_name=role_name, company=company)

    def remove_role_in_company(self, role_name, company=None):
        company = company or self.current_company or self.company
        try:
            role = Role.objects.get(name=role_name)
            user_company = self.managed_companies.filter(company=company).first()
            if user_company:
                if role in user_company.roles.all():
                    user_company.roles.remove(role)
                    user_company.save()
                    return True
        except Role.DoesNotExist:
            return False
        return False
    def is_admin(self, user=None):
        roles = ['ADMIN']
        return user.has_roles_in_company(roles) if user else self.has_roles_in_company(roles)
    def is_manager(self, user=None):
        roles = ['MANAGER']
        return user.has_roles_in_company(roles) if user else self.has_roles_in_company(roles)
    def is_support_worker(self, user=None):
        roles = ['SUPPORT_WORKER']
        return user.has_roles_in_company(roles) if user else self.has_roles_in_company(roles)
    def can_manage_sce(self, user=None):
        if self.is_superuser:
            return True

        # Rôles autorisés pour gérer le SCE
        roles = ['SUPER_ADMIN', 'ADMIN', 'SCE_MANAGER']

        # Si un utilisateur est passé en paramètre, obtenir son employé
        employe = user.get_employee_in_company() if user else self.get_employee_in_company()

        # Vérifie si l'utilisateur a l'un des rôles autorisés dans la société
        can_manage_roles = (user.has_roles_in_company(roles) if user else self.has_roles_in_company(roles))

        # Vérifie également si l'employé peut gérer le SCE
        can_manage_employee_sce = employe and employe.can_manage_sce() if employe else False

        return can_manage_roles or can_manage_employee_sce
    def is_member_of_sce(self, user=None):
        """
        Vérifie si l'utilisateur est membre du SCE en fonction de ses rôles.
        """
        if self.is_superuser:
            return True

        employe = user.get_employee_in_company() if user else self.get_employee_in_company()
        
        return employe and employe.is_member_of_sce()
    def can_manage_governance(self, user=None):
        if self.is_superuser:
            return True

        # Rôles autorisés pour gérer la gouvernance
        roles = ['SUPER_ADMIN', 'ADMIN', 'GOVERNANCE_MANAGER']
        governance_member = user.get_governance_member_in_company() if user else self.get_governance_member_in_company()
        can_manage_roles = (user.has_roles_in_company(roles) if user else self.has_roles_in_company(roles))
        can_manage_governance = governance_member and governance_member.can_manage_governance() if governance_member else False
        return can_manage_roles or can_manage_governance

    def can_manage_quality(self, user=None):
        if self.is_superuser:
            return True
        roles = ['SUPER_ADMIN', 'ADMIN' ,'QUALITY_MANAGER']
        return user.has_roles_in_company(roles) if user else self.has_roles_in_company(roles)
    def can_manage_activity(self, user=None):
        if self.is_superuser:
            return True
        roles = ['SUPER_ADMIN', 'ADMIN' ,'ACTIVITY_MANAGER']
        return user.has_roles_in_company(roles) if user else self.has_roles_in_company(roles)
    def can_manage_administration(self, user=None):
        if self.is_superuser:
            return True
        roles = ['SUPER_ADMIN', 'ADMIN' ,'ADMINISTRATIVE_MANAGER']
        return user.has_roles_in_company(roles) if user else self.has_roles_in_company(roles)
    def can_manage_human_ressources(self, user=None):
        if self.is_superuser:
            return True
        roles = ['SUPER_ADMIN', 'ADMIN' ,'HR_MANAGER']
        return user.has_roles_in_company(roles) if user else self.has_roles_in_company(roles)
    def can_manage_finance(self, user=None):
        if self.is_superuser:
            return True
        roles = ['SUPER_ADMIN', 'ADMIN' ,'FINANCE_MANAGER']
        return user.has_roles_in_company(roles) if user else self.has_roles_in_company(roles)
    def can_manage_facility(self, user=None):
        if self.is_superuser:
            return True
        roles = ['SUPER_ADMIN', 'ADMIN' ,'FACILITY_MANAGER']
        return user.has_roles_in_company(roles) if user else self.has_roles_in_company(roles)
    def can_manage_parking(self, user=None):
        if self.is_superuser:
            return True
        roles = ['SUPER_ADMIN', 'ADMIN' ,'FACILITY_MANAGER', 'MECHANIC']
        return user.has_roles_in_company(roles) if user else self.has_roles_in_company(roles)
    @classmethod
    def get_quality_managers_in_user_company(cls, user=None, company=None):
        company = company or user.current_company or user.company
        quality_managers = cls.objects.filter(
            managed_companies__roles__name='QUALITY_MANAGER',
            managed_companies__company=company
        ).distinct()
        if not quality_managers.exists():
            quality_managers = cls.objects.filter(roles__name='QUALITY_MANAGER', company=company).distinct()
        return quality_managers
    @classmethod
    def get_activity_managers_in_user_company(cls, user=None, company=None):
        company = company or user.current_company or user.company
        activity_managers = cls.objects.filter(
            managed_companies__roles__name='ACTIVITY_MANAGER',
            managed_companies__company=company
        ).distinct()
        if not activity_managers.exists():
            activity_managers = cls.objects.filter(roles__name='ACTIVITY_MANAGER', company=company).distinct()
        return activity_managers
    @classmethod
    def get_facility_managers_in_user_company(cls, user=None, company=None):
        company = company or user.current_company or user.company
        facility_managers = cls.objects.filter(
            managed_companies__roles__name='FACILITY_MANAGER',
            managed_companies__company=company
        ).distinct()
        if not facility_managers.exists():
            facility_managers = cls.objects.filter(roles__name='FACILITY_MANAGER', company=company).distinct()
        return facility_managers
    @classmethod
    def get_finance_managers_in_user_company(cls, user=None, company=None):
        company = company or user.current_company or user.company
        finance_managers = cls.objects.filter(
            managed_companies__roles__name='FINANCE_MANAGER',
            managed_companies__company=company
        ).distinct()
        if not finance_managers.exists():
            finance_managers = cls.objects.filter(roles__name='FINANCE_MANAGER', company=company).distinct()
        return finance_managers

    def get_default_sent_email(self, default_password=None):
        """Appelle le service pour récupérer l'email par défaut."""
        if not default_password:
            default_password = ''.join(random.choices(string.ascii_letters + string.digits, k=10))
        self.set_password(default_password)
        self.save()
        return get_default_sent_email(self, default_password)

    def save(self, *args, **kwargs):
        # 1. Génération du username
        if not self.username:
            if self.first_name and self.last_name:
                base_first_name = slugify(f"{self.first_name}")
                base_last_name = slugify(f"{self.last_name}")
                base_username = f"{base_first_name}.{base_last_name}"
            elif self.email:
                base_username = slugify(self.email.split('@')[0])
            else:
                base_username = "user"

            username = base_username
            counter = 1
            while User.objects.filter(username=username).exists():
                username = f"{base_username}{counter}"
                counter += 1
            self.username = username

        # 2. Génération de l'email si non fourni
        if not self.email:
            # Récupérer le domaine de l’entreprise si dispo
            company_domain = None
            if self.company and self.company.email:
                company_domain = self.company.email.split('@')[-1]

            domain = company_domain or "roberp.fr"
            self.email = f"{self.username}@{domain}"

        super(User, self).save(*args, **kwargs)


class UserCompany(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='managed_companies', null=True)
    roles = models.ManyToManyField(Role, related_name='managed_companies', blank=True)

    employee = models.ForeignKey('human_ressources.Employee', on_delete=models.SET_NULL, null=True, related_name='managed_companies')
    governance_member = models.ForeignKey('governance.GovernanceMember', on_delete=models.SET_NULL, related_name='managed_companies', null=True)
    partner = models.ForeignKey('partnerships.Partner', on_delete=models.SET_NULL, null=True, related_name='managed_companies')
    financier = models.ForeignKey('partnerships.Financier', on_delete=models.SET_NULL, null=True, related_name='managed_companies')
    supplier = models.ForeignKey('purchases.Supplier', on_delete=models.SET_NULL, null=True, related_name='managed_companies')
    company = models.ForeignKey('companies.Company', on_delete=models.SET_NULL, null=True, related_name='company_users')
    creator = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return f"{self.user} - {self.company.name}"

# Create your models here.
class Device(models.Model):
    token = models.TextField(max_length=255)
    platform = models.CharField(max_length=255, null=True)
    name = models.CharField(max_length=255, default='Device sans nom', null=True)
    description = models.TextField(default='', null=True)
    observation = models.TextField(default='', null=True)
    is_user_online_here = models.BooleanField(default='', null=True)
    is_active = models.BooleanField(default=True, null=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='device_user', null=True)
    creator = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True)
    is_deleted = models.BooleanField(default=False, null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)
    def __str__(self):
        return self.token
