from django.db import models
from datetime import datetime
import random

# Create your models here.
class Call(models.Model):
	number = models.CharField(max_length=255, editable=False, null=True)
	title = models.CharField(max_length=255)
	image = models.ForeignKey('medias.File', on_delete=models.SET_NULL, related_name='call_image', null=True)
	entry_date_time = models.DateTimeField(null=True)
	duration = models.FloatField(null=True)
	description = models.TextField(default='', null=True)
	observation = models.TextField(default='', null=True)
	is_active = models.BooleanField(default=True, null=True)
	folder = models.ForeignKey('medias.Folder', on_delete=models.SET_NULL, null=True)
	creator = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True)
	created_at = models.DateTimeField(auto_now_add=True, null=True)
	updated_at = models.DateTimeField(auto_now=True, null=True)
    
	def save(self, *args, **kwargs):
	    # Générer le numéro unique lors de la sauvegarde si ce n'est pas déjà défini
	    if not self.number:
	        self.number = self.generate_unique_number()

	    super(Call, self).save(*args, **kwargs)

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
	    while Call.objects.filter(number=number).exists():
	        number_suffix = current_time.strftime("%Y%m%d%H%M%S")
	        number = f'{number_prefix}{number_suffix}'

	    return number
	    
	def __str__(self):
		return self.title

# Create your models here.
class CallBeneficiary(models.Model):
	call = models.ForeignKey(Call, on_delete=models.SET_NULL, null=True)
	beneficiary = models.ForeignKey('human_ressources.Beneficiary', on_delete=models.SET_NULL, related_name='call_beneficiary', null=True)
	creator = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, related_name='call_beneficiary_former', null=True)
	created_at = models.DateTimeField(auto_now_add=True, null=True)
	updated_at = models.DateTimeField(auto_now=True, null=True)

	def __str__(self):
		return str(self.id)

# Create your models here.
class CallBeneficiaryAbsence(models.Model):
	number = models.CharField(max_length=255, editable=False, null=True)
	title = models.CharField(max_length=255)
	call = models.ForeignKey(Call, on_delete=models.SET_NULL, null=True)
	beneficiary = models.ForeignKey('human_ressources.Beneficiary', on_delete=models.SET_NULL, related_name='call_beneficiary_absence', null=True)
	starting_date_time = models.DateTimeField(null=True)
	ending_date_time = models.DateTimeField(null=True)
	comment = models.TextField(default='', null=True)
	observation = models.TextField(default='', null=True)
	folder = models.ForeignKey('medias.Folder', on_delete=models.SET_NULL, null=True)
	creator = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, related_name='call_beneficiary_absence_former', null=True)
	created_at = models.DateTimeField(auto_now_add=True, null=True)
	updated_at = models.DateTimeField(auto_now=True, null=True)

	def __str__(self):
		return str(self.id)