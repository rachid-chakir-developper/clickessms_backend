from django.db import models
import uuid
from django.conf import settings
from django.utils.timezone import now
from datetime import timedelta
from the_mailer.services.recruitment_services import get_default_sent_email, send_application_interest_email, send_application_rejection_email, send_application_acceptance_email, send_job_candidate_information_sheet_email

# Create your models here.
class JobPosition(models.Model):
	STATUS_CHOICES = [
		('PENDING', 'En attente'),
		('REJECTED', 'Rejeté'),
		('ACCEPTED', 'Accepté'),
	]
	number = models.CharField(max_length=255, editable=False, null=True)
	CONTRACT_TYPES = [
		("CDI", "CDI"),
		("CDD", "CDD"),
		("APPRENTICESHIP_CONTRACT", "Contrat d'apprentissage"),
		("SINGLE_INTEGRATION_CONTRACT", "Contrat Unique d'Insertion (CUI)"),
		("PROFESSIONALIZATION_CONTRACT", "Contrat de professionnalisation"),
		("SEASONAL_CONTRACT", "Contrat saisonnier"),
		("TEMPORARY_CONTRACT", "Contrat intérimaire"),
		("PART_TIME_CONTRACT", "Contrat à temps partiel"),
		("FULL_TIME_CONTRACT", "Contrat à temps plein"),
		("INTERNSHIP_CONTRACT", "Contrat de stage")
	]
	title = models.CharField(max_length=255)
	establishment = models.ForeignKey('companies.Establishment', on_delete=models.SET_NULL, related_name='job_positions', null=True)
	sector = models.CharField(max_length=255)
	contract_type = models.CharField(max_length=50, choices=CONTRACT_TYPES, default= "CDI")
	hiring_date = models.DateField(null=True, blank=True)
	duration = models.CharField(max_length=50, null=True, blank=True)
	description = models.TextField(default='', null=True)
	observation = models.TextField(default='', null=True)
	status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="PENDING")
	is_active = models.BooleanField(default=True, null=True)
	folder = models.ForeignKey('medias.Folder', on_delete=models.SET_NULL, null=True)
	employee = models.ForeignKey('human_ressources.Employee', on_delete=models.SET_NULL, related_name='job_positions', null=True)
	company = models.ForeignKey('companies.Company', on_delete=models.SET_NULL, related_name='company_job_positions', null=True)
	creator = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, related_name='creator_job_positions', null=True)
	is_deleted = models.BooleanField(default=False, null=True)
	created_at = models.DateTimeField(auto_now_add=True, null=True)
	updated_at = models.DateTimeField(auto_now=True, null=True)

	def __str__(self):
		return f"{self.title}"

class JobPosting(models.Model):
	number = models.CharField(max_length=255, editable=False, null=True)
	job_position = models.ForeignKey(
		'JobPosition', on_delete=models.CASCADE, related_name='job_postings'
	)
	title = models.CharField(max_length=255)
	publication_date = models.DateField(auto_now_add=True)
	expiration_date = models.DateField(null=True, blank=True)
	description = models.TextField(default='', null=True)
	observation = models.TextField(default='', null=True)
	folder = models.ForeignKey('medias.Folder', on_delete=models.SET_NULL, null=True)
	employee = models.ForeignKey('human_ressources.Employee', on_delete=models.SET_NULL, related_name='job_postings', null=True)
	company = models.ForeignKey('companies.Company', on_delete=models.SET_NULL, related_name='company_job_postings', null=True)
	creator = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, related_name='creator_job_postings', null=True)
	is_deleted = models.BooleanField(default=False, null=True)
	created_at = models.DateTimeField(auto_now_add=True, null=True)
	updated_at = models.DateTimeField(auto_now=True, null=True)

	def __str__(self):
		return f"{self.title}"

class JobPostingPlatform(models.Model):
	job_posting = models.ForeignKey(JobPosting, on_delete=models.SET_NULL, null=True, related_name='job_platforms')
	job_platform = models.ForeignKey('data_management.JobPlatform', on_delete=models.SET_NULL, null=True)
	post_link = models.URLField(max_length=255, null=True)
	creator = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True)
	created_at = models.DateTimeField(auto_now_add=True, null=True)
	updated_at = models.DateTimeField(auto_now=True, null=True)

	def __str__(self):
		return f"{self.id}"

GENDERS = [
	("MALE", "Homme"),
	("FEMALE", "Femme"),
	("NOT_SPECIFIED", "Non spécifié"),
]
class JobCandidate(models.Model):
	number = models.CharField(max_length=255, editable=False, null=True)
	gender = models.CharField(max_length=50, choices=GENDERS, default="NOT_SPECIFIED", null=True, blank=True)
	preferred_name = models.CharField(max_length=255, null=True)
	first_name = models.CharField(max_length=255)
	last_name = models.CharField(max_length=255)
	email = models.EmailField()
	phone = models.CharField(max_length=20)
	job_title = models.CharField(max_length=255)
	availability_date = models.DateField(null=True, blank=True)
	job_platform = models.ForeignKey('data_management.JobPlatform', on_delete=models.SET_NULL, null=True)
	cv = models.ForeignKey('medias.File', on_delete=models.SET_NULL, related_name='cv_job_candidates', null=True)
	cover_letter = models.ForeignKey('medias.File', on_delete=models.SET_NULL, related_name='cover_letter_job_candidates', null=True)
	description = models.TextField(default='', null=True)
	observation = models.TextField(default='', null=True)
	rating = models.PositiveIntegerField(default=0)
	is_active = models.BooleanField(default=True, null=True)
	folder = models.ForeignKey('medias.Folder', on_delete=models.SET_NULL, null=True)
	employee = models.ForeignKey('human_ressources.Employee', on_delete=models.SET_NULL, related_name='job_candidates', null=True)
	company = models.ForeignKey('companies.Company', on_delete=models.SET_NULL, related_name='company_job_candidates', null=True)
	creator = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, related_name='creator_job_candidates', null=True)
	is_deleted = models.BooleanField(default=False, null=True)
	created_at = models.DateTimeField(auto_now_add=True, null=True)
	updated_at = models.DateTimeField(auto_now=True, null=True)

	def __str__(self):
		return self.first_name

class JobCandidateApplication(models.Model):
	STATUS_CHOICES = [
		('PENDING', 'En attente'),  # Le candidat a postulé, en cours d'examen.
		('INTERESTED', 'Intéressant'),  # Le profil nous intéresse, mais pas encore d'entretien prévu.
		('INTERVIEW', 'Entretien prévu'),  # Un entretien a été planifié avec le candidat.
		('OFFERED', 'Offre envoyée'),  # Une offre d'emploi a été envoyée au candidat.
		('REJECTED', 'Rejeté'),  # Le candidat n'a pas été retenu.
		('ACCEPTED', 'Accepté'),  # Le candidat a accepté l'offre et va rejoindre l'entreprise.
	]
	number = models.CharField(max_length=255, editable=False, null=True)
	gender = models.CharField(max_length=50, choices=GENDERS, default="NOT_SPECIFIED", null=True, blank=True)
	preferred_name = models.CharField(max_length=255, null=True)
	first_name = models.CharField(max_length=255)
	last_name = models.CharField(max_length=255)
	email = models.EmailField()
	phone = models.CharField(max_length=20)
	job_title = models.CharField(max_length=255)
	availability_date = models.DateField(null=True, blank=True)
	job_candidate = models.ForeignKey(JobCandidate, on_delete=models.SET_NULL, related_name='job_candidate_applications', null=True)
	job_platform = models.ForeignKey('data_management.JobPlatform', on_delete=models.SET_NULL, null=True)
	cv = models.ForeignKey('medias.File', on_delete=models.SET_NULL, related_name='cv_job_candidate_applications', null=True)
	cover_letter = models.ForeignKey('medias.File', on_delete=models.SET_NULL, related_name='cover_letter_job_candidate_applications', null=True)
	description = models.TextField(default='', null=True)
	observation = models.TextField(default='', null=True)
	rating = models.PositiveIntegerField(default=0)
	status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="PENDING")
	job_position = models.ForeignKey(JobPosition, on_delete=models.SET_NULL, null=True, blank=True)
	is_active = models.BooleanField(default=True, null=True)
	folder = models.ForeignKey('medias.Folder', on_delete=models.SET_NULL, null=True)
	employee = models.ForeignKey('human_ressources.Employee', on_delete=models.SET_NULL, related_name='job_candidate_applications', null=True)
	company = models.ForeignKey('companies.Company', on_delete=models.SET_NULL, related_name='company_job_candidate_applications', null=True)
	creator = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, related_name='creator_job_candidate_applications', null=True)
	is_deleted = models.BooleanField(default=False, null=True)
	created_at = models.DateTimeField(auto_now_add=True, null=True)
	updated_at = models.DateTimeField(auto_now=True, null=True)

	def get_default_sent_email(self):
		"""Appelle le service pour récupérer l'email par défaut."""
		return get_default_sent_email(self)

	def send_application_interest_email(self):
		"""Envoie un email pour que le candidat remplisse sa fiche de renseignement."""
		return send_application_interest_email(self)

	def send_application_rejection_email(self):
		"""Refuse la candidature et envoie un email de refus."""
		return send_application_rejection_email(self)

	def send_application_acceptance_email(self):
		"""Accepte la candidature et envoie un email d'acceptation avec un lien de formulaire."""
		return send_application_acceptance_email(self)

	def __str__(self):
		return self.first_name

class JobCandidateInformationSheet(models.Model):
	STATUS_CHOICES = [
		('PENDING', 'En attente'),
		('REJECTED', 'Rejeté'),
		('ACCEPTED', 'Accepté'),
	]
	number = models.CharField(max_length=255, editable=False, null=True)
	gender = models.CharField(max_length=50, choices=GENDERS, default="NOT_SPECIFIED", null=True, blank=True)
	preferred_name = models.CharField(max_length=255, null=True)
	first_name = models.CharField(max_length=255)
	last_name = models.CharField(max_length=255)
	email = models.EmailField()
	phone = models.CharField(max_length=20)
	job_title = models.CharField(max_length=255)
	job_candidate = models.ForeignKey(JobCandidate, on_delete=models.SET_NULL, related_name='job_candidate_information_sheets', null=True)
	description = models.TextField(default='', null=True)
	observation = models.TextField(default='', null=True)
	message = models.TextField(default='', null=True)
	access_token = models.CharField(max_length=64, unique=True, blank=True, null=True)
	token_expiration = models.DateTimeField(blank=True, null=True)
	status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="PENDING")
	job_position = models.ForeignKey(JobPosition, on_delete=models.SET_NULL, null=True, blank=True)
	is_active = models.BooleanField(default=True, null=True)
	folder = models.ForeignKey('medias.Folder', on_delete=models.SET_NULL, null=True)
	employee = models.ForeignKey('human_ressources.Employee', on_delete=models.SET_NULL, related_name='job_candidate_information_sheets', null=True)
	company = models.ForeignKey('companies.Company', on_delete=models.SET_NULL, related_name='company_job_candidate_information_sheets', null=True)
	creator = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, related_name='creator_candidate_information_sheets', null=True)
	is_deleted = models.BooleanField(default=False, null=True)
	created_at = models.DateTimeField(auto_now_add=True, null=True)
	updated_at = models.DateTimeField(auto_now=True, null=True)

	def send_job_candidate_information_sheet_email(self):
		"""Envoie un email pour que le candidat remplisse sa fiche de renseignement."""
		return send_job_candidate_information_sheet_email(self)

	def generate_access_token(self):
		self.access_token = uuid.uuid4().hex  # Génère un token unique
		self.token_expiration = now() + timedelta(days=15)  # Expire dans 2 jours
		self.save()

	def get_access_link(self):
		"""Construit le lien d'accès au formulaire."""
		return f"{settings.FRONTEND_SITE_URL}/offline/ressources-humaines/recrutement/fiche-renseignement/{self.access_token}"

	def __str__(self):
		return self.first_name