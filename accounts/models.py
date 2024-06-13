from django.db import models
from django.contrib.auth.models import AbstractUser

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

    USERNAME_FIELD = "username"
    EMAIL_FIELD = "email"

    def addCompany(self, company):
        if not self.managed_companies.filter(company=company).exists():
            UserCompany.objects.create(user=self, company=company)
            return True
        return False

    def removeCompany(self, company):
        user_company = self.managed_companies.filter(company=company).first()
        if user_company:
            user_company.delete()
            return True
        return False

    def getEmployeeInCompany(self, company=None):
        company = company or self.current_company or self.company
        user_company = self.managed_companies.filter(company=company).first()
        return user_company.employee if user_company and user_company.employee else self.employee

    def setEmployeeForCompany(self, employee_id, company=None):
        from human_ressources.models import Employee
        company = company or self.current_company or self.company
        try:
            employee = Employee.objects.get(id=employee_id)
        except Employee.DoesNotExist:
            employee = None
        user_company, created = self.managed_companies.get_or_create(company=company)
        user_company.employee = employee
        user_company.save()

    def getPartnerInCompany(self, company=None):
        company = company or self.current_company or self.company
        user_company = self.managed_companies.filter(company=company).first()
        return user_company.partner if user_company and user_company.partner else self.partner

    def setPartnerForCompany(self, partner_id, company=None):
        from partnerships.models import Partner
        company = company or self.current_company or self.company
        try:
            partner = Partner.objects.get(id=partner_id)
        except Partner.DoesNotExist:
            partner = None
        user_company, created = self.managed_companies.get_or_create(company=company)
        user_company.partner = partner
        user_company.save()

    def getFinancierInCompany(self, company=None):
        company = company or self.current_company or self.company
        user_company = self.managed_companies.filter(company=company).first()
        return user_company.financier if user_company and user_company.financier else self.financier

    def setFinancierForCompany(self, financier_id, company=None):
        from partnerships.models import Financier
        company = company or self.current_company or self.company
        try:
            financier = Financier.objects.get(id=financier_id)
        except Financier.DoesNotExist:
            financier = None
        user_company, created = self.managed_companies.get_or_create(company=company)
        user_company.financier = financier
        user_company.save()

    def getSupplierInCompany(self, company=None):
        company = company or self.current_company or self.company
        user_company = self.managed_companies.filter(company=company).first()
        return user_company.supplier if user_company and user_company.supplier else self.supplier

    def setSupplierForCompany(self, supplier_id, company=None):
        from purchases.models import Supplier
        company = company or self.current_company or self.company
        try:
            supplier = Supplier.objects.get(id=supplier_id)
        except Supplier.DoesNotExist:
            supplier = None
        user_company, created = self.managed_companies.get_or_create(company=company)
        user_company.supplier = supplier
        user_company.save()

class UserCompany(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='managed_companies', null=True)
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
