from django.db import models
from datetime import datetime
import random

# Create your models here.
class Partner(models.Model):
	PARTNER_TYPES = [
		("BUSINESS", "Entreprise"),
		("INDIVIDUAL", "Particulier"),
	]
	number = models.CharField(max_length=255, editable=False, null=True)
	name = models.CharField(max_length=255)
	email = models.EmailField(blank=False, max_length=255, verbose_name="email")
	photo = models.ForeignKey('medias.File', on_delete=models.SET_NULL, related_name='partner_photo', null=True)
	cover_image = models.ForeignKey('medias.File', on_delete=models.SET_NULL, related_name='partner_cover_image', null=True)
	partner_type = models.CharField(max_length=50, choices=PARTNER_TYPES, default= "INDIVIDUAL", null=True)
	manager_name = models.CharField(max_length=255, null=True)
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
	company = models.ForeignKey('companies.Company', on_delete=models.SET_NULL, related_name='company_partners', null=True)
	creator = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, related_name='partner_former', null=True)
	is_deleted = models.BooleanField(default=False, null=True)
	created_at = models.DateTimeField(auto_now_add=True, null=True)
	updated_at = models.DateTimeField(auto_now=True, null=True)
    
	def save(self, *args, **kwargs):
	    # Générer le numéro unique lors de la sauvegarde si ce n'est pas déjà défini
	    if not self.number:
	        self.number = self.generate_unique_number()

	    super(Partner, self).save(*args, **kwargs)

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
	    while Partner.objects.filter(number=number).exists():
	        number_suffix = current_time.strftime("%Y%m%d%H%M%S")
	        number = f'{number_prefix}{number_suffix}'

	    return number
        
	def __str__(self):
		return self.email

# Create your models here.
class Financier(models.Model):
	FINANCIER_TYPES = [
		("BUSINESS", "Entreprise"),
		("INDIVIDUAL", "Particulier"),
	]
	number = models.CharField(max_length=255, editable=False, null=True)
	external_number = models.CharField(default='', max_length=255, null=True)
	name = models.CharField(max_length=255)
	email = models.EmailField(blank=False, max_length=255, verbose_name="email")
	photo = models.ForeignKey('medias.File', on_delete=models.SET_NULL, related_name='financier_photo', null=True)
	cover_image = models.ForeignKey('medias.File', on_delete=models.SET_NULL, related_name='financier_cover_image', null=True)
	financier_type = models.CharField(max_length=50, choices=FINANCIER_TYPES, default= "INDIVIDUAL", null=True)
	manager_name = models.CharField(max_length=255, null=True)
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
	company = models.ForeignKey('companies.Company', on_delete=models.SET_NULL, related_name='company_financiers', null=True)
	creator = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, related_name='financier_former', null=True)
	is_deleted = models.BooleanField(default=False, null=True)
	created_at = models.DateTimeField(auto_now_add=True, null=True)
	updated_at = models.DateTimeField(auto_now=True, null=True)
    
	def save(self, *args, **kwargs):
	    # Générer le numéro unique lors de la sauvegarde si ce n'est pas déjà défini
	    if not self.number:
	        self.number = self.generate_unique_number()

	    super(Financier, self).save(*args, **kwargs)

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
	    while Financier.objects.filter(number=number).exists():
	        number_suffix = current_time.strftime("%Y%m%d%H%M%S")
	        number = f'{number_prefix}{number_suffix}'

	    return number
        
	def __str__(self):
		return self.email