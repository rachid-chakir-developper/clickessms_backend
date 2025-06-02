from django.db import models
from datetime import datetime
from django.utils.timezone import now
import random

# Create your models here.
class GovernanceMember(models.Model):
    number = models.CharField(max_length=255, editable=False, null=True)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    email = models.EmailField(blank=False, max_length=255, verbose_name="email")
    photo = models.ForeignKey('medias.File', on_delete=models.SET_NULL, related_name='governance_member_photo', null=True)
    cover_image = models.ForeignKey('medias.File', on_delete=models.SET_NULL, related_name='governance_member_cover_image', null=True)
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
    role = models.CharField(max_length=255, blank=True, null=True)
    folder = models.ForeignKey('medias.Folder', on_delete=models.SET_NULL, null=True)
    company = models.ForeignKey('companies.Company', on_delete=models.SET_NULL, related_name='company_governance_members', null=True)
    creator = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, related_name='governance_member_former', null=True)
    is_archived = models.BooleanField(default=False, null=True)
    is_deleted = models.BooleanField(default=False, null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)
    
    def save(self, *args, **kwargs):
        # Générer le numéro unique lors de la sauvegarde si ce n'est pas déjà défini
        if not self.number:
            self.number = self.generate_unique_number()

        super(GovernanceMember, self).save(*args, **kwargs)

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
        while GovernanceMember.objects.filter(number=number).exists():
            number_suffix = current_time.strftime("%Y%m%d%H%M%S")
            number = f'{number_prefix}{number_suffix}'

        return number

    def archive(self):
        self.archived = True
        self.save()
    def unarchive(self):
        self.archived = False
        self.save()

    @property
    def governance_roles(self):
        roles = [f"{self.current_role}_IN_GOVERNANCE"] if self.current_role else []
        if roles and 'MEMBER_IN_GOVERNANCE' not in roles:
            roles.insert(0, 'MEMBER_IN_GOVERNANCE')
        return roles

    @property
    def current_role(self):
        """
        Retourne le rôle actuel du membre de la gouvernance en fonction de la date actuelle.
        Si aucun rôle en cours n'est trouvé, retourne 'MEMBER' par défaut.
        """
        today = now()
        current = self.governance_member_roles.filter(
            starting_date_time__lte=today,
        ).filter(
            models.Q(ending_date_time__gte=today) | models.Q(ending_date_time__isnull=True)
        ).order_by('-starting_date_time').first()
        current_role=current.role if current else "MEMBER"
        return current_role if current_role!="OTHER" else current.other_role

    def can_manage_governance(self):
        roles_autorises = ['PRESIDENT']
        return self.current_role in roles_autorises or True

    def __str__(self):
        return self.email

class GovernanceMemberRole(models.Model):
    ROLE_CHOICES = [
        ('PRESIDENT', 'Président'),
        ('TREASURER', 'Trésorier'),
        ('ASSISTANT_TREASURER', 'Trésorier Adjoint'),
        ('SECRETARY', 'Secrétaire'),
        ('ASSISTANT_SECRETARY', 'Secrétaire Adjoint'),
        ('MEMBER', 'Membre'),
        ('OTHER', 'Autre'),
    ]
    governance_member = models.ForeignKey(GovernanceMember, on_delete=models.SET_NULL, null=True, related_name='governance_member_roles')
    role = models.CharField(max_length=50, choices=ROLE_CHOICES, default= "MEMBER")
    other_role = models.CharField(max_length=255, blank=True, null=True)
    starting_date_time = models.DateTimeField(null=True)
    ending_date_time = models.DateTimeField(null=True)
    is_active = models.BooleanField(default=True, null=True)
    creator = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, related_name='governance_member_roles', null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return str(self.id)