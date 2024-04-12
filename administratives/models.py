from django.db import models
from datetime import datetime
import random
from data_management.models import PhoneNumber, HomeAddress

# Create your models here.
class Call(models.Model):
	CALL_TYPES = [
		("INCOMING", "Entrant"),
		("OUTGOING", "Sortant"),
	]
	number = models.CharField(max_length=255, editable=False, null=True)
	title = models.CharField(max_length=255)
	call_type = models.CharField(max_length=50, choices=CALL_TYPES, default= "INCOMING", null=True)
	image = models.ForeignKey('medias.File', on_delete=models.SET_NULL, related_name='call_image', null=True)
	entry_date_time = models.DateTimeField(null=True)
	duration = models.FloatField(null=True)
	description = models.TextField(default='', null=True)
	observation = models.TextField(default='', null=True)
	is_active = models.BooleanField(default=True, null=True)
	folder = models.ForeignKey('medias.Folder', on_delete=models.SET_NULL, null=True)
	employee = models.ForeignKey('human_ressources.Employee', on_delete=models.SET_NULL, related_name='employee_calls', null=True)
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

	def setCaller(self, caller_data=None, creator=None):
		if self.id and Caller.objects.filter(call__id=self.id).exists():
			Caller.objects.filter(call__id=self.id).delete()
		caller = Caller(**caller_data)
		caller.call = self
		caller.creator = creator
		print(f'*************{caller_data}')
		if caller_data.caller_type == 'PhoneNumber' and ('phone_number_id' not in caller_data or caller_data.phone_number_id is None):
			phone_number = PhoneNumber.objects.filter(phone=caller_data.phone).first()
			phone_number = phone_number if phone_number else PhoneNumber.objects.create(phone=caller_data.phone)
			caller.phone_number = phone_number
		caller.save()
		self.save()
	def __str__(self):
		return self.title

# Create your models here.
class Caller(models.Model):
	name = models.CharField(max_length=255, null=True)
	phone = models.CharField(max_length=255, null=True)
	caller_type = models.CharField(max_length=255, null=True)
	call = models.ForeignKey(Call, on_delete=models.SET_NULL, null=True)
	employee = models.ForeignKey('human_ressources.Employee', on_delete=models.SET_NULL, related_name='call_employee_callers', null=True)
	beneficiary = models.ForeignKey('human_ressources.Beneficiary', on_delete=models.SET_NULL, related_name='call_beneficiary_callers', null=True)
	partner = models.ForeignKey('partnerships.Partner', on_delete=models.SET_NULL, related_name='call_partner_callers', null=True)
	supplier = models.ForeignKey('purchases.Supplier', on_delete=models.SET_NULL, related_name='call_supplier_callers', null=True)
	client = models.ForeignKey('sales.Client', on_delete=models.SET_NULL, related_name='call_client_callers', null=True)
	establishment = models.ForeignKey('companies.Establishment', on_delete=models.SET_NULL, related_name='call_establishment_callers', null=True)
	phone_number = models.ForeignKey('data_management.PhoneNumber', on_delete=models.SET_NULL, related_name='call_phone_number_callers', null=True)
	creator = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, related_name='call_caller_former', null=True)
	created_at = models.DateTimeField(auto_now_add=True, null=True)
	updated_at = models.DateTimeField(auto_now=True, null=True)

	def __str__(self):
		return str(self.id)

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
class Letter(models.Model):
	CALL_TYPES = [
		("INCOMING", "Entrant"),
		("OUTGOING", "Sortant"),
	]
	number = models.CharField(max_length=255, editable=False, null=True)
	title = models.CharField(max_length=255)
	letter_type = models.CharField(max_length=50, choices=CALL_TYPES, default= "INCOMING", null=True)
	image = models.ForeignKey('medias.File', on_delete=models.SET_NULL, related_name='letter_image', null=True)
	entry_date_time = models.DateTimeField(null=True)
	duration = models.FloatField(null=True)
	description = models.TextField(default='', null=True)
	observation = models.TextField(default='', null=True)
	is_active = models.BooleanField(default=True, null=True)
	folder = models.ForeignKey('medias.Folder', on_delete=models.SET_NULL, null=True)
	employee = models.ForeignKey('human_ressources.Employee', on_delete=models.SET_NULL, related_name='employee_letters', null=True)
	creator = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True)
	created_at = models.DateTimeField(auto_now_add=True, null=True)
	updated_at = models.DateTimeField(auto_now=True, null=True)
    
	def save(self, *args, **kwargs):
	    # Générer le numéro unique lors de la sauvegarde si ce n'est pas déjà défini
	    if not self.number:
	        self.number = self.generate_unique_number()

	    super(Letter, self).save(*args, **kwargs)

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
	    while Letter.objects.filter(number=number).exists():
	        number_suffix = current_time.strftime("%Y%m%d%H%M%S")
	        number = f'{number_prefix}{number_suffix}'

	    return number
	    
	def __str__(self):
		return self.title

# Create your models here.
class LetterBeneficiary(models.Model):
	letter = models.ForeignKey(Letter, on_delete=models.SET_NULL, null=True)
	beneficiary = models.ForeignKey('human_ressources.Beneficiary', on_delete=models.SET_NULL, related_name='letter_beneficiary', null=True)
	creator = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, related_name='letter_beneficiary_former', null=True)
	created_at = models.DateTimeField(auto_now_add=True, null=True)
	updated_at = models.DateTimeField(auto_now=True, null=True)

	def __str__(self):
		return str(self.id)

# Create your models here.
class Meeting(models.Model):
	number = models.CharField(max_length=255, editable=False, null=True)
	title = models.CharField(max_length=255)
	video_call_link = models.URLField(max_length=255, null=True)
	starting_date_time = models.DateTimeField(null=True)
	ending_date_time = models.DateTimeField(null=True)
	reasons = models.ManyToManyField('data_management.MeetingReason', related_name='reason_meetings')
	other_reasons = models.CharField(max_length=255, null=True)
	description = models.TextField(default='', null=True)
	observation = models.TextField(default='', null=True)
	folder = models.ForeignKey('medias.Folder', on_delete=models.SET_NULL, null=True)
	employee = models.ForeignKey('human_ressources.Employee', on_delete=models.SET_NULL, related_name='employee_meetings', null=True)
	creator = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, related_name='meeting_former', null=True)
	created_at = models.DateTimeField(auto_now_add=True, null=True)
	updated_at = models.DateTimeField(auto_now=True, null=True)
    
	def save(self, *args, **kwargs):
	    # Générer le numéro unique lors de la sauvegarde si ce n'est pas déjà défini
	    if not self.number:
	        self.number = self.generate_unique_number()

	    super(Meeting, self).save(*args, **kwargs)

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
	    while Meeting.objects.filter(number=number).exists():
	        number_suffix = current_time.strftime("%Y%m%d%H%M%S")
	        number = f'{number_prefix}{number_suffix}'

	    return number
	    
	def __str__(self):
		return self.title

# Create your models here.
class MeetingReport(models.Model):
	meeting = models.ForeignKey(Meeting, on_delete=models.SET_NULL, null=True)
	creator = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, related_name='meeting_report_former', null=True)
	created_at = models.DateTimeField(auto_now_add=True, null=True)
	updated_at = models.DateTimeField(auto_now=True, null=True)

	def __str__(self):
		return str(self.id)

# Create your models here.
class MeetingReportItem(models.Model):
	meeting_report = models.ForeignKey(MeetingReport, on_delete=models.SET_NULL, null=True)
	report = models.CharField(max_length=255, null=True)
	decision = models.TextField(default='', null=True)
	points_to_review = models.TextField(default='', null=True)
	creator = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True)
	created_at = models.DateTimeField(auto_now_add=True, null=True)
	updated_at = models.DateTimeField(auto_now=True, null=True)

	def __str__(self):
		return self.name

# Create your models here.
class ParticipantMeetingItem(models.Model):
	meeting = models.ForeignKey(Meeting, on_delete=models.SET_NULL, null=True)
	employee = models.ForeignKey('human_ressources.Employee', on_delete=models.SET_NULL, related_name='participant_meeting_items', null=True)
	creator = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, related_name='participant_meeting_item_former', null=True)
	created_at = models.DateTimeField(auto_now_add=True, null=True)
	updated_at = models.DateTimeField(auto_now=True, null=True)

	def __str__(self):
		return str(self.id)
# Create your models here.
class BeneficiaryMeetingItem(models.Model):
	meeting = models.ForeignKey(Meeting, on_delete=models.SET_NULL, null=True)
	beneficiary = models.ForeignKey('human_ressources.Beneficiary', on_delete=models.SET_NULL, related_name='beneficiary_meeting_items', null=True)
	creator = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, related_name='beneficiary_meeting_item_former', null=True)
	created_at = models.DateTimeField(auto_now_add=True, null=True)
	updated_at = models.DateTimeField(auto_now=True, null=True)

	def __str__(self):
		return str(self.id)