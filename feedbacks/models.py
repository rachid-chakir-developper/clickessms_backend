from django.db import models
import base64

# Create your models here.
class Comment(models.Model):
	text = models.TextField(default='', null=True)
	image = models.ForeignKey('medias.File', on_delete=models.SET_NULL, related_name='comment_image', null=True)
	parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE)
	ticket = models.ForeignKey('works.Ticket', on_delete=models.SET_NULL, related_name='comments', null=True)
	task = models.ForeignKey('works.Task', on_delete=models.SET_NULL, related_name='comments', null=True)
	task_action = models.ForeignKey('works.TaskAction', on_delete=models.SET_NULL, related_name='comments', null=True)
	expense = models.ForeignKey('purchases.Expense', on_delete=models.SET_NULL, related_name='comments', null=True)
	beneficiary_admission = models.ForeignKey('human_ressources.BeneficiaryAdmission', on_delete=models.SET_NULL, null=True, related_name='comments')
	creator = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True)
	created_at = models.DateTimeField(auto_now_add=True, null=True)
	updated_at = models.DateTimeField(auto_now=True, null=True)

	def __str__(self):
		return self.text

# Create your models here.
class Signature(models.Model):
	SATISFACTIONS = [
		("MEDIUM", "MEDIUM"),#
		("ANGRY", "ANGRY"),#
		("CONFUSED", "CONFUSED"),#
		("SMILE", "SMILE"),#
		("KISS", "KISS")#
	]
	base64_encoded = models.TextField(null=True)
	image = models.ForeignKey('medias.File', on_delete=models.SET_NULL, related_name='signature_image', null=True)
	author_name = models.TextField(null=True)
	author_number = models.TextField(null=True)
	author_position = models.CharField(max_length=255, null=True)
	author_email = models.EmailField(max_length=254, null=True)
	satisfaction = models.CharField(max_length=50, choices=SATISFACTIONS, default= "MEDIUM")
	comment = models.TextField(default='', null=True)
	author = models.ForeignKey('human_ressources.Employee', on_delete=models.SET_NULL, related_name='signatures', null=True)
	creator = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True)
	created_at = models.DateTimeField(auto_now_add=True, null=True)
	updated_at = models.DateTimeField(auto_now=True, null=True)
	
	def update_base64_encoded(self):
		"""
		Updates the base64_encoded field with the base64 representation of the associated image.
		"""
		if self.image and self.image.image:
			try:
				# Ouvrir le fichier image
				with self.image.image.open('rb') as img_file:
					# Lire le contenu du fichier
					image_data = img_file.read()
					# Encoder en base64
					self.base64_encoded = base64.b64encode(image_data).decode('utf-8')
			except Exception as e:
				raise ValueError(f"Erreur lors de l'encodage base64 de l'image : {str(e)}")

	def save(self, *args, **kwargs):
		"""
		Overriding the save method to update base64_encoded from the associated image.
		"""
		# Mettre à jour base64_encoded si elle est vide
		if not self.base64_encoded:
			self.update_base64_encoded()
		
		# Appeler la méthode save de base
		super().save(*args, **kwargs)

	def __str__(self):
		return self.base64_encoded

class StatusChange(models.Model):
	undesirable_event = models.ForeignKey('qualities.UndesirableEvent', on_delete=models.CASCADE, related_name='status_changes')
	name = models.CharField(max_length=255, null=True, default= "NEW")
	created_at = models.DateTimeField(auto_now_add=True, null=True)
	updated_at = models.DateTimeField(auto_now=True, null=True)
	
	def __str__(self):
		return self.status

class Feedback(models.Model):
	FEEDBACK_MODULES = [
		('APP', 'Application'),
		('DASHBOARD', 'Tableau de bord'),
		('QUALITY', 'Qualité'),
		('ACTIVITY', 'Activité'),
		('HR', 'Ressources Humaines'),
		('ADMINISTRATIF', 'Administratif'),
		('FACILITY', 'Services Généraux'),
		('FINANCE', 'Finance'),
		('IT', 'Informatique'),
		('PURCHASE', 'Achat'),
		('GOVERNANCE', 'Gouvernance'),
		('CSE', 'CSE'),
		('LEGAL', 'Juridiques'),
		('RESOURCES', 'Ressources'),
		('USERS', 'Utilisateurs'),
		('SETTINGS', 'Paramètres'),
	]
	feedback_module = models.CharField(max_length=50, choices=FEEDBACK_MODULES, default= "APP")
	title = models.CharField(max_length=255, null=True)
	image = models.ForeignKey('medias.File', on_delete=models.SET_NULL, related_name='feedbacks', null=True)
	message = models.TextField(null=True)
	is_active = models.BooleanField(default=True, null=True)
	company = models.ForeignKey('companies.Company', on_delete=models.SET_NULL, related_name='feedbacks', null=True)
	creator = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, related_name='feedbacks', null=True)
	created_at = models.DateTimeField(auto_now_add=True, null=True)
	updated_at = models.DateTimeField(auto_now=True, null=True)

	def __str__(self):
		return self.title