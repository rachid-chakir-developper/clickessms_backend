from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.
class Role(models.Model):
    ROLE_CHOICES = [
        ('SUPER_ADMIN', 'Super admin'),
        ('ADMIN', 'Admin'),
        ('MANAGER', 'Employé'),
        ('QUALITY_MANAGER', 'Responsable Qualité'),
        ('ACTIVITY_MANAGER', 'Responsable Activité'),
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
    email = models.EmailField(blank=False, max_length=255, verbose_name="email")
    account_type = models.CharField(max_length=50, choices=ACCOUNT_TYPES, default= "PRO", null=True)
    photo = models.ForeignKey('medias.File', on_delete=models.SET_NULL, related_name='user_photo', null=True)
    cover_image = models.ForeignKey('medias.File', on_delete=models.SET_NULL, related_name='user_cover_image', null=True)
    email = models.EmailField(max_length=254, null=True)
    is_cgu_accepted = models.BooleanField(null=True)
    is_online = models.BooleanField(default=False, null=True)
    number_current_connexions = models.PositiveIntegerField(default=0, null=True)
    description = models.TextField(default='', null=True)
    observation = models.TextField(default='', null=True)
    current_latitude = models.CharField(max_length=255, null=True)
    current_longitude = models.CharField(max_length=255, null=True)
    company = models.ForeignKey('companies.Company', on_delete=models.SET_NULL, related_name='company_admins', null=True)
    current_company = models.ForeignKey('companies.Company', on_delete=models.SET_NULL, related_name='current_company_users', null=True)
    employee = models.ForeignKey('human_ressources.Employee', on_delete=models.SET_NULL, related_name='employee_user', null=True)
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

    def remove_company(self, company):
        user_company = self.managed_companies.filter(company=company).first()
        if user_company:
            user_company.delete()
            return True
        return False

    def get_employee_in_company(self, company=None):
        company = company or self.current_company or self.company
        user_company = self.managed_companies.filter(company=company).first()
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
    def can_manage_quality(self, user=None):
        roles = ['SUPER_ADMIN', 'ADMIN', 'MANAGER' ,'QUALITY_MANAGER']
        return user.has_roles_in_company(roles) if user else self.has_roles_in_company(roles)
    def can_manage_activity(self, user=None):
        roles = ['SUPER_ADMIN', 'ADMIN', 'MANAGER' ,'ACTIVITY_MANAGER']
        return user.has_roles_in_company(roles) if user else self.has_roles_in_company(roles)
    def can_manage_administration(self, user=None):
        roles = ['SUPER_ADMIN', 'ADMIN', 'MANAGER' ,'ADMINISTRATIVE_MANAGER']
    def can_manage_human_ressources(self, user=None):
        roles = ['SUPER_ADMIN', 'ADMIN', 'MANAGER' ,'HR_MANAGER']
        return user.has_roles_in_company(roles) if user else self.has_roles_in_company(roles)
    def can_manage_finance(self, user=None):
        roles = ['SUPER_ADMIN', 'ADMIN', 'MANAGER' ,'FINANCE_MANAGER']
        return user.has_roles_in_company(roles) if user else self.has_roles_in_company(roles)
    def can_manage_facility(self, user=None):
        roles = ['SUPER_ADMIN', 'ADMIN', 'MANAGER' ,'FACILITY_MANAGER']
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


class UserCompany(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='managed_companies', null=True)
    roles = models.ManyToManyField(Role, related_name='managed_companies', blank=True)

    employee = models.ForeignKey('human_ressources.Employee', on_delete=models.SET_NULL, null=True)
    partner = models.ForeignKey('partnerships.Partner', on_delete=models.SET_NULL, null=True)
    financier = models.ForeignKey('partnerships.Financier', on_delete=models.SET_NULL, null=True)
    supplier = models.ForeignKey('purchases.Supplier', on_delete=models.SET_NULL, null=True)
    company = models.ForeignKey('companies.Company', on_delete=models.SET_NULL, null=True)
    creator = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return f"{self.user.username} - {self.company.name}"

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
