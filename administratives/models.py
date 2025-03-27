from django.db import models
from datetime import datetime
from django.utils import timezone
import random
from data_management.models import PhoneNumber, HomeAddress
from qualities.models import UndesirableEvent
from works.models import TaskAction

from django.db.models.signals import post_save
from django.dispatch import receiver

from the_mailer.services.recruitment_services import send_interview_invitation

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
	is_create_undesirable_event_from = models.BooleanField(default=False, null=True)
	is_active = models.BooleanField(default=True, null=True)
	folder = models.ForeignKey('medias.Folder', on_delete=models.SET_NULL, null=True)
	employee = models.ForeignKey('human_ressources.Employee', on_delete=models.SET_NULL, related_name='employee_calls', null=True)
	company = models.ForeignKey('companies.Company', on_delete=models.SET_NULL, related_name='company_calls', null=True)
	creator = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True)
	is_deleted = models.BooleanField(default=False, null=True)
	created_at = models.DateTimeField(auto_now_add=True, null=True)
	updated_at = models.DateTimeField(auto_now=True, null=True)

	def create_undesirable_event(self):
		if self.is_create_undesirable_event_from and (not self.undesirable_events or self.undesirable_events is None):
			undesirable_event = UndesirableEvent.objects.create(
				title=f"Événement créé à partir d'un appel {self.title}",
				starting_date_time=timezone.now(),
				ending_date_time=timezone.now() + timezone.timedelta(hours=1),
				call=self,
				company=self.company,
				creator=self.creator,
				employee=self.employee,
				)
			self.save()
			return undesirable_event
		return None

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
		caller.company = creator.the_current_company
		if caller_data.caller_type == 'PhoneNumber' and ('phone_number_id' not in caller_data or caller_data.phone_number_id is None):
			phone_number = PhoneNumber.objects.filter(phone=caller_data.phone).first()
			phone_number = phone_number if phone_number else PhoneNumber.objects.create(phone=caller_data.phone, company=creator.the_current_company)
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
	call = models.ForeignKey(Call, on_delete=models.SET_NULL, null=True, related_name='callers')
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
class CallEstablishment(models.Model):
	call = models.ForeignKey(Call, on_delete=models.SET_NULL, null=True, related_name='establishments')
	establishment = models.ForeignKey('companies.Establishment', on_delete=models.SET_NULL, related_name='call_establishments', null=True)
	creator = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, related_name='call_establishments', null=True)
	created_at = models.DateTimeField(auto_now_add=True, null=True)
	updated_at = models.DateTimeField(auto_now=True, null=True)

	def __str__(self):
		return str(self.id)

# Create your models here.
class CallEmployee(models.Model):
	call = models.ForeignKey(Call, on_delete=models.SET_NULL, null=True, related_name='employees')
	employee = models.ForeignKey('human_ressources.Employee', on_delete=models.SET_NULL, related_name='call_employees', null=True)
	creator = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, related_name='call_employees', null=True)
	created_at = models.DateTimeField(auto_now_add=True, null=True)
	updated_at = models.DateTimeField(auto_now=True, null=True)

	def __str__(self):
		return str(self.id)

# Create your models here.
class CallBeneficiary(models.Model):
	call = models.ForeignKey(Call, on_delete=models.SET_NULL, null=True, related_name='beneficiaries')
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
	document = models.ForeignKey('medias.File', on_delete=models.SET_NULL, related_name='document_letters', null=True)
	entry_date_time = models.DateTimeField(null=True)
	duration = models.FloatField(null=True)
	description = models.TextField(default='', null=True)
	observation = models.TextField(default='', null=True)
	is_active = models.BooleanField(default=True, null=True)
	folder = models.ForeignKey('medias.Folder', on_delete=models.SET_NULL, null=True)
	employee = models.ForeignKey('human_ressources.Employee', on_delete=models.SET_NULL, related_name='employee_letters', null=True)
	company = models.ForeignKey('companies.Company', on_delete=models.SET_NULL, related_name='company_letters', null=True)
	creator = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True)
	is_deleted = models.BooleanField(default=False, null=True)
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
		
	def setSender(self, sender_data=None, creator=None):
		if sender_data:
			sender = LetterSender.objects.create(
				letter=self,
				name=sender_data.get('name', ''),
				sender_type=sender_data.get('type', ''),
				other_sender=sender_data.get('otherSender', ''),
				creator=creator, company=creator.the_current_company
			)
			
			if sender_data.get('type') == 'PARTNER' and sender_data.get('partner_id'):
				sender.partner_id = sender_data.get('partner_id')
			elif sender_data.get('type') == 'SUPPLIER' and sender_data.get('supplier_id'):
				sender.supplier_id = sender_data.get('supplier_id')
			elif sender_data.get('type') == 'FINANCIER' and sender_data.get('financier_id'):
				sender.financier_id = sender_data.get('financier_id')
			elif sender_data.get('type') == 'EMPLOYEE' and sender_data.get('employee_id'):
				sender.employee_id = sender_data.get('employee_id')
				
			sender.save()
		
	def __str__(self):
		return self.title
		
# Create your models here.
class LetterSender(models.Model):
	name = models.CharField(max_length=255, null=True)
	sender_type = models.CharField(max_length=255, null=True)
	other_sender = models.CharField(max_length=255, null=True)
	letter = models.ForeignKey(Letter, on_delete=models.SET_NULL, null=True, related_name='senders')
	employee = models.ForeignKey('human_ressources.Employee', on_delete=models.SET_NULL, related_name='letter_employee_senders', null=True)
	partner = models.ForeignKey('partnerships.Partner', on_delete=models.SET_NULL, related_name='letter_partner_senders', null=True)
	supplier = models.ForeignKey('purchases.Supplier', on_delete=models.SET_NULL, related_name='letter_supplier_senders', null=True)
	financier = models.ForeignKey('partnerships.Financier', on_delete=models.SET_NULL, related_name='letter_financier_senders', null=True)
	creator = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, related_name='letter_sender_former', null=True)
	created_at = models.DateTimeField(auto_now_add=True, null=True)
	updated_at = models.DateTimeField(auto_now=True, null=True)
	
	def __str__(self):
		return self.name or f"Expéditeur {self.id}"
		
# Create your models here.
class LetterEstablishment(models.Model):
	letter = models.ForeignKey(Letter, on_delete=models.SET_NULL, null=True, related_name='establishments')
	establishment = models.ForeignKey('companies.Establishment', on_delete=models.SET_NULL, related_name='letter_establishments', null=True)
	creator = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, related_name='letter_establishments', null=True)
	created_at = models.DateTimeField(auto_now_add=True, null=True)
	updated_at = models.DateTimeField(auto_now=True, null=True)

	def __str__(self):
		return str(self.id)

# Create your models here.
class LetterEmployee(models.Model):
	letter = models.ForeignKey(Letter, on_delete=models.SET_NULL, null=True, related_name='employees')
	employee = models.ForeignKey('human_ressources.Employee', on_delete=models.SET_NULL, related_name='letter_employees', null=True)
	creator = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, related_name='letter_employees', null=True)
	created_at = models.DateTimeField(auto_now_add=True, null=True)
	updated_at = models.DateTimeField(auto_now=True, null=True)

	def __str__(self):
		return str(self.id)

# Create your models here.
class LetterBeneficiary(models.Model):
	letter = models.ForeignKey(Letter, on_delete=models.SET_NULL, null=True, related_name='beneficiaries')
	beneficiary = models.ForeignKey('human_ressources.Beneficiary', on_delete=models.SET_NULL, related_name='letter_beneficiary', null=True)
	creator = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, related_name='letter_beneficiary_former', null=True)
	created_at = models.DateTimeField(auto_now_add=True, null=True)
	updated_at = models.DateTimeField(auto_now=True, null=True)

	def __str__(self):
		return str(self.id)

# Create your models here.
class Meeting(models.Model):
	MEETING_MODES = [
		('PV', 'Procès-Verbal'),
		('PV_SCE', 'Procès-Verbal cse'),
		('SIMPLE', 'Réunion Simple'),
		('INTERVIEW', 'Entretien'),
		('CANDIDATE_INTERVIEW', 'Entretien Candidat'),
	]
	number = models.CharField(max_length=255, editable=False, null=True)
	title = models.CharField(max_length=255, null=True)
	topics = models.TextField(default='', blank=True, null=True)
	video_call_link = models.URLField(max_length=255, null=True)
	starting_date_time = models.DateTimeField(null=True)
	ending_date_time = models.DateTimeField(null=True)
	meeting_mode = models.CharField(max_length=50, choices=MEETING_MODES, default= "SIMPLE")
	meeting_types = models.ManyToManyField('data_management.TypeMeeting', related_name='type_meetings')
	reasons = models.ManyToManyField('data_management.MeetingReason', related_name='reason_meetings')
	other_reasons = models.CharField(max_length=255, null=True)
	absent_participants = models.ManyToManyField('human_ressources.Employee', related_name='absent_participant_meetings')
	description = models.TextField(default='', null=True)
	observation = models.TextField(default='', null=True)
	notes = models.TextField(default='', null=True)
	is_active = models.BooleanField(default=True, null=True)
	folder = models.ForeignKey('medias.Folder', on_delete=models.SET_NULL, null=True)
	job_candidate = models.ForeignKey('recruitment.JobCandidate', on_delete=models.SET_NULL, related_name='job_candidate_meetings', null=True)
	job_position = models.ForeignKey('recruitment.JobPosition', on_delete=models.SET_NULL, related_name='job_position_meetings', null=True)
	employee = models.ForeignKey('human_ressources.Employee', on_delete=models.SET_NULL, related_name='employee_meetings', null=True)
	company = models.ForeignKey('companies.Company', on_delete=models.SET_NULL, related_name='company_meeting_beneficiarys', null=True)
	creator = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, related_name='meeting_former', null=True)
	is_deleted = models.BooleanField(default=False, null=True)
	created_at = models.DateTimeField(auto_now_add=True, null=True)
	updated_at = models.DateTimeField(auto_now=True, null=True)

	def send_mail_invitation_to_candidat(self):
		"""Utilise the_mailer pour envoyer un email d'invitation au candidat"""
		return send_interview_invitation(self)
	
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
class MeetingEstablishment(models.Model):
	meeting = models.ForeignKey(Meeting, on_delete=models.SET_NULL, null=True, related_name='establishments')
	establishment = models.ForeignKey('companies.Establishment', on_delete=models.SET_NULL, related_name='meeting_establishment', null=True)
	creator = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, related_name='meeting_establishment_former', null=True)
	created_at = models.DateTimeField(auto_now_add=True, null=True)
	updated_at = models.DateTimeField(auto_now=True, null=True)

	def __str__(self):
		return str(self.id)

# Create your models here.
class MeetingDecision(models.Model):
	meeting = models.ForeignKey(Meeting, on_delete=models.SET_NULL, null=True, related_name='meeting_decisions')
	decision = models.TextField(default='', null=True)
	due_date = models.DateTimeField(null=True)
	employees = models.ManyToManyField('human_ressources.Employee', related_name='employee_meeting_decisions')
	for_voters = models.ManyToManyField('human_ressources.Employee', related_name='voted_for_decisions')
	against_voters = models.ManyToManyField('human_ressources.Employee', related_name='voted_against_decisions')
	creator = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, related_name='meeting_decision_former', null=True)
	created_at = models.DateTimeField(auto_now_add=True, null=True)
	updated_at = models.DateTimeField(auto_now=True, null=True)

	def __str__(self):
		return str(self.id)

@receiver(post_save, sender=MeetingDecision)
def create_or_update_task_action(sender, instance, created, **kwargs):
	"""
	Signal pour créer ou mettre à jour une TaskAction
	lorsqu'une MeetingDecision est sauvegardée.
	"""
	if created:
		# Créer une nouvelle TaskAction
		print('h11111')
		task_action = TaskAction.objects.create(
			meeting_decision=instance,
			description=instance.decision,
			due_date=instance.due_date,
			company=instance.meeting.creator.company if instance.meeting.creator else None,
			creator=instance.meeting.creator,
		)
		task_action.employees.set(instance.employees.all())
	else:
		# Mettre à jour la TaskAction existante
		print('h222')
		task_action = TaskAction.objects.filter(meeting_decision=instance).first()
		if task_action:
			print(task_action.creator)
			task_action.description = instance.decision
			task_action.due_date = instance.due_date
			task_action.company=instance.meeting.creator.company if instance.meeting.creator else None
			task_action.creator=instance.meeting.creator
			task_action.save()
			task_action.employees.set(instance.employees.all())
		else:
			# Si aucune TaskAction n'existe, en créer une nouvelle
			print('h444')
			task_action = TaskAction.objects.create(
				ticket=None,  # Ajustez si nécessaire
				meeting_decision=instance,
				description=instance.decision,
				due_date=instance.due_date,
				company=instance.meeting.creator.company if instance.meeting.creator else None,
				creator=instance.meeting.creator,
			)
			task_action.employees.set(instance.employees.all())

# Create your models here.
class MeetingReviewPoint(models.Model):
	meeting = models.ForeignKey(Meeting, on_delete=models.SET_NULL, null=True, related_name='meeting_review_points')
	point_to_review = models.TextField(default='', null=True)
	creator = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, related_name='review_point_former', null=True)
	created_at = models.DateTimeField(auto_now_add=True, null=True)
	updated_at = models.DateTimeField(auto_now=True, null=True)

	def __str__(self):
		return self.name

# Create your models here.
class MeetingParticipant(models.Model):
	STATUS_CHOICES = [
		('PRESENT', 'Present'),
		('ABSENT', 'Absent'),
		('EXCUSED', 'Excused'),
	]
	meeting = models.ForeignKey(Meeting, on_delete=models.SET_NULL, null=True, related_name='participants')
	employee = models.ForeignKey('human_ressources.Employee', on_delete=models.SET_NULL, related_name='participant_meetings', null=True)
	status = models.CharField(max_length=50, choices=STATUS_CHOICES, default= "PRESENT")
	creator = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, related_name='participant_meeting_former', null=True)
	created_at = models.DateTimeField(auto_now_add=True, null=True)
	updated_at = models.DateTimeField(auto_now=True, null=True)

	def __str__(self):
		return str(self.id)
		
# Create your models here.
class MeetingBeneficiary(models.Model):
	meeting = models.ForeignKey(Meeting, on_delete=models.SET_NULL, null=True, related_name='beneficiaries')
	beneficiary = models.ForeignKey('human_ressources.Beneficiary', on_delete=models.SET_NULL, related_name='meeting_beneficiaries', null=True)
	creator = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, related_name='meeting_beneficiary_former', null=True)
	created_at = models.DateTimeField(auto_now_add=True, null=True)
	updated_at = models.DateTimeField(auto_now=True, null=True)

	def __str__(self):
		return str(self.id)

# Create your models here.
class FrameDocument(models.Model):
	number = models.CharField(max_length=255, editable=False, null=True)
	name = models.CharField(max_length=255)
	document = models.ForeignKey('medias.File', on_delete=models.SET_NULL, related_name='frame_documents', null=True)
	document_type = models.ForeignKey('data_management.DocumentType', on_delete=models.SET_NULL, related_name='frame_documents', null=True)
	description = models.TextField(default='', null=True)
	is_active = models.BooleanField(default=True, null=True)
	establishments = models.ManyToManyField('companies.Establishment', related_name='frame_documents')
	employee = models.ForeignKey('human_ressources.Employee', on_delete=models.SET_NULL, related_name='frame_documents', null=True)
	company = models.ForeignKey('companies.Company', on_delete=models.SET_NULL, related_name='frame_documents', null=True)
	creator = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True)
	is_deleted = models.BooleanField(default=False, null=True)
	created_at = models.DateTimeField(auto_now_add=True, null=True)
	updated_at = models.DateTimeField(auto_now=True, null=True)

