from django.db import models
from datetime import datetime
import random

# Create your models here.
class DecisionDocument(models.Model):
	number = models.CharField(max_length=255, editable=False, null=True)
	name = models.CharField(max_length=255)
	document = models.ForeignKey('medias.File', on_delete=models.SET_NULL, related_name='decision_document_file', null=True)
	decision_date = models.DateTimeField(null=True)
	reception_date_time = models.DateTimeField(null=True)
	description = models.TextField(default='', null=True)
	observation = models.TextField(default='', null=True)
	is_active = models.BooleanField(default=True, null=True)
	financier = models.ForeignKey('partnerships.Financier', on_delete=models.SET_NULL, null=True)
	folder = models.ForeignKey('medias.Folder', on_delete=models.SET_NULL, null=True)
	company = models.ForeignKey('companies.Company', on_delete=models.SET_NULL, related_name='company_decision_documents', null=True)
	creator = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True)
	is_deleted = models.BooleanField(default=False, null=True)
	created_at = models.DateTimeField(auto_now_add=True, null=True)
	updated_at = models.DateTimeField(auto_now=True, null=True)
    
	def save(self, *args, **kwargs):
	    # Générer le numéro unique lors de la sauvegarde si ce n'est pas déjà défini
	    if not self.number:
	        self.number = self.generate_unique_number()

	    super(DecisionDocument, self).save(*args, **kwargs)

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
	    while DecisionDocument.objects.filter(number=number).exists():
	        number_suffix = current_time.strftime("%Y%m%d%H%M%S")
	        number = f'{number_prefix}{number_suffix}'

	    return number
	    
	def __str__(self):
		return self.name

# Create your models here.
class DecisionDocumentItem(models.Model):
	decision_document = models.ForeignKey(DecisionDocument, on_delete=models.SET_NULL, null=True)
	establishment = models.ForeignKey('companies.establishment', on_delete=models.SET_NULL, related_name='establishment_decision_document_items', null=True)
	starting_date_time = models.DateTimeField(null=True)
	ending_date_time = models.DateTimeField(null=True)
	price = models.FloatField(null=True)
	endowment = models.FloatField(null=True)
	occupancy_rate = models.FloatField(null=True)
	theoretical_number_unit_work = models.FloatField(null=True)
	creator = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, related_name='decision_document_item_former', null=True)
	created_at = models.DateTimeField(auto_now_add=True, null=True)
	updated_at = models.DateTimeField(auto_now=True, null=True)

	def __str__(self):
		return str(self.id)
