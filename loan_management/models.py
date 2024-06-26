from django.db import models
from datetime import datetime
import random

# Create your models here.
class TheObject(models.Model):
	number = models.CharField(max_length=255, editable=False, null=True)
	name = models.CharField(max_length=255)
	image = models.ForeignKey('medias.File', on_delete=models.SET_NULL, related_name='the_object_image', null=True)
	description = models.TextField(default='', null=True)
	observation = models.TextField(default='', null=True)
	is_active = models.BooleanField(default=True, null=True)
	client = models.ForeignKey('sales.Client', on_delete=models.SET_NULL, related_name='the_object_client', null=True)
	partner = models.ForeignKey('partnerships.Partner', on_delete=models.SET_NULL, related_name='the_object_partner', null=True)
	company = models.ForeignKey('companies.Company', on_delete=models.SET_NULL, related_name='company_the_objects', null=True)
	creator = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True)
	created_at = models.DateTimeField(auto_now_add=True, null=True)
	updated_at = models.DateTimeField(auto_now=True, null=True)

	def save(self, *args, **kwargs):
		# Générer le numéro unique lors de la sauvegarde si ce n'est pas déjà défini
		if not self.number:
		    self.number = self.generate_unique_number()

		super(TheObject, self).save(*args, **kwargs)

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
	    while TheObject.objects.filter(number=number).exists():
	        number_suffix = current_time.strftime("%Y%m%d%H%M%S")
	        number = f'{number_prefix}{number_suffix}'

	    return number

	def __str__(self):
		return self.name

# Create your models here.
class ObjectRecovery(models.Model):
	number = models.CharField(max_length=255, editable=False, null=True)
	name = models.CharField(max_length=255)
	description = models.TextField(default='', null=True)
	observation = models.TextField(default='', null=True)
	recovery_date = models.DateTimeField(null=True)
	return_date = models.DateTimeField(null=True)
	images = models.ManyToManyField('medias.File', related_name='object_recovery_images')
	videos = models.ManyToManyField('medias.File', related_name='object_recovery_videos')
	the_object = models.ForeignKey(TheObject, on_delete=models.SET_NULL, related_name='the_object_recoveries', null=True)
	creator = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True)
	created_at = models.DateTimeField(auto_now_add=True, null=True)
	updated_at = models.DateTimeField(auto_now=True, null=True)
    
	def save(self, *args, **kwargs):
	    # Générer le numéro unique lors de la sauvegarde si ce n'est pas déjà défini
	    if not self.number:
	        self.number = self.generate_unique_number()

	    super(ObjectRecovery, self).save(*args, **kwargs)

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
	    while ObjectRecovery.objects.filter(number=number).exists():
	        number_suffix = current_time.strftime("%Y%m%d%H%M%S")
	        number = f'{number_prefix}{number_suffix}'

	    return number

	def __str__(self):
		return self.name
