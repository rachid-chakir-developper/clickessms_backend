from django.db import models
from datetime import datetime
import random

# Create your models here.
class SceMember(models.Model):
	ROLE_CHOICES = [
		('PRESIDENT', 'Président'),
		('TREASURER', 'Trésorier'),
		('ASSISTANT_TREASURER', 'Trésorier Adjoint'),
		('SECRETARY', 'Secrétaire'),
		('ASSISTANT_SECRETARY', 'Secrétaire Adjoint'),
		('MEMBER', 'Membre'),
		('SUBSTITUTE', 'Suppléant'),
		('PRIMARY_MEMBER', 'Titulaire'),
	]
	number = models.CharField(max_length=255, editable=False, null=True)
	employee = models.ForeignKey('human_ressources.Employee', on_delete=models.SET_NULL, related_name='sce_members', null=True)
	description = models.TextField(default='', null=True)
	observation = models.TextField(default='', null=True)
	is_active = models.BooleanField(default=True, null=True)
	role = models.CharField(max_length=50, choices=ROLE_CHOICES, default= "MEMBER")
	folder = models.ForeignKey('medias.Folder', on_delete=models.SET_NULL, null=True)
	company = models.ForeignKey('companies.Company', on_delete=models.SET_NULL, related_name='company_sce_members', null=True)
	creator = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, related_name='sce_member_former', null=True)
	is_deleted = models.BooleanField(default=False, null=True)
	created_at = models.DateTimeField(auto_now_add=True, null=True)
	updated_at = models.DateTimeField(auto_now=True, null=True)
	
	def save(self, *args, **kwargs):
		# Générer le numéro unique lors de la sauvegarde si ce n'est pas déjà défini
		if not self.number:
			self.number = self.generate_unique_number()

		super(SceMember, self).save(*args, **kwargs)

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
		while SceMember.objects.filter(number=number).exists():
			number_suffix = current_time.strftime("%Y%m%d%H%M%S")
			number = f'{number_prefix}{number_suffix}'

		return number

	def __str__(self):
		return self.number

# Create your models here.
class SceBenefit(models.Model):
	number = models.CharField(max_length=255, editable=False, null=True)
	title = models.CharField(max_length=255, null=True, blank=True)
	content = models.TextField(default='', null=True)
	description = models.TextField(default='', null=True)
	observation = models.TextField(default='', null=True)
	is_active = models.BooleanField(default=True, null=True)
	folder = models.ForeignKey('medias.Folder', on_delete=models.SET_NULL, null=True)
	company = models.ForeignKey('companies.Company', on_delete=models.SET_NULL, related_name='company_sce_benefits', null=True)
	creator = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, related_name='sce_benefit_former', null=True)
	is_deleted = models.BooleanField(default=False, null=True)
	created_at = models.DateTimeField(auto_now_add=True, null=True)
	updated_at = models.DateTimeField(auto_now=True, null=True)
	
	def save(self, *args, **kwargs):
		# Générer le numéro unique lors de la sauvegarde si ce n'est pas déjà défini
		if not self.number:
			self.number = self.generate_unique_number()

		super(SceBenefit, self).save(*args, **kwargs)

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
		while SceBenefit.objects.filter(number=number).exists():
			number_suffix = current_time.strftime("%Y%m%d%H%M%S")
			number = f'{number_prefix}{number_suffix}'

		return number

	def __str__(self):
		return self.title