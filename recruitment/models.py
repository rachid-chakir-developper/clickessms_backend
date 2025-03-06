from django.db import models

# Create your models here.
class JobPosition(models.Model):
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
	duration = models.CharField(max_length=50, null=True, blank=True)
	description = models.TextField(default='', null=True)
	observation = models.TextField(default='', null=True)
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

class JobCandidate(models.Model):
	number = models.CharField(max_length=255, editable=False, null=True)
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
	job_position = models.ForeignKey(JobPosition, on_delete=models.SET_NULL, null=True, blank=True)
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