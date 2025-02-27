from django.db import models
from moviepy.editor import VideoFileClip
import os
from django.conf import settings
from datetime import date, timedelta
from django.utils.timezone import now


# Create your models here.

class Folder(models.Model):
	FOLDER_TYPES = [
		("NORMAL", "Normal"),
	]
	number = models.CharField(max_length=255, editable=False, null=True)
	name = models.CharField(max_length=255)
	description = models.TextField(default='', null=True)
	observation = models.TextField(default='', null=True)
	is_active = models.BooleanField(default=True, null=True)
	folder = models.ForeignKey('self', on_delete=models.SET_NULL, related_name='children_folders', null=True)
	folder_type = models.CharField(max_length=50, choices=FOLDER_TYPES, default= "NORMAL")
	creator = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True)
	created_at = models.DateTimeField(auto_now_add=True, null=True)
	updated_at = models.DateTimeField(auto_now=True, null=True)

	def __str__(self):
		return self.name

def file_directory_path(instance, filename):
	# file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
	directory_path = ''
	upload_to = instance.upload_to
	if upload_to:
		directory_path = '/' + upload_to
	folder = instance.folder
	while (folder):
		directory_path = '/' + folder.name + directory_path
		folder = folder.folder
	return 'uploads' + directory_path + '/{0}'.format(filename)

class File(models.Model):
	FILE_TYPES = [
		("FILE", "Fichier"),
		("IMAGE", "Image"),
		("VIDEO", "Video")
	]
	number = models.CharField(max_length=255, editable=False, null=True)
	name = models.CharField(max_length=255, null=True)
	caption = models.TextField(default='', null=True)
	description = models.TextField(default='', null=True)
	observation = models.TextField(default='', null=True)
	upload_to = models.CharField(max_length=255, null=True)
	file_type = models.CharField(max_length=50, choices=FILE_TYPES, default= "FILE")
	file = models.FileField(upload_to=file_directory_path, null=True)
	video = models.FileField(upload_to=file_directory_path, null=True)
	thumbnail = models.ImageField(upload_to=file_directory_path, null=True)
	image = models.ImageField(upload_to=file_directory_path, null=True)
	is_active = models.BooleanField(default=True, null=True)
	folder = models.ForeignKey(Folder, on_delete=models.SET_NULL, null=True)
	company = models.ForeignKey('companies.Company', on_delete=models.SET_NULL, related_name='company_files', null=True)
	creator = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True)
	created_at = models.DateTimeField(auto_now_add=True, null=True)
	updated_at = models.DateTimeField(auto_now=True, null=True)
		
	def __str__(self):
		return self.name if self.name else 'file'

	def save(self, *args, **kwargs):
		if self.video and self.video.file:
			super().save(*args, **kwargs)
			# Chemin complet vers le fichier vidéo
			video_path = os.path.join(settings.MEDIA_ROOT, str(self.video).replace(settings.MEDIA_URL, ''))

			# Générer la miniature
			thumbnail_path = os.path.join(settings.MEDIA_ROOT, f'{self.video.name.split(".")[0]}.png')

			clip = VideoFileClip(video_path)
			clip.save_frame(thumbnail_path, t=2)  # Obtenir une capture d'écran à la deuxième seconde
			# Mettre à jour le champ de la miniature avec le chemin
			self.thumbnail.name = f'{self.video.name.split(".")[0]}.png'

			# Compresser la vidéo en MP4 #pip install imageio_ffmpeg
			## compressed_video_path = os.path.join(settings.MEDIA_ROOT, 'uploads', f'{self.video.name.split(".")[0]}.mp4')
			##clip.write_videofile(compressed_video_path, codec="libx264", audio_codec="aac")
			# Mettre à jour le champ de la vidéo avec le chemin compressé
			##self.video.name = f'uploads/{self.video.name.split(".")[0]}.mp4'

		super().save(*args, **kwargs)

# Create your models here.
class DocumentRecord(models.Model):
	NOTIFICATION_PERIOD_UNITS = [
		("HOUR", "Heure"),#
		("DAY", "Jour"),#
		("WEEK", "Semaine"),#
		("MONTH", "Mois")#
	]
	number = models.CharField(max_length=255, editable=False, null=True)
	beneficiary = models.ForeignKey('human_ressources.Beneficiary', on_delete=models.SET_NULL, related_name='document_records', null=True)
	name = models.CharField(max_length=255)
	document = models.ForeignKey('medias.File', on_delete=models.SET_NULL, related_name='document_records', null=True)
	document_type = models.ForeignKey('data_management.DocumentType', on_delete=models.SET_NULL, related_name='document_records', null=True)
	beneficiary_document_type = models.ForeignKey('data_management.BeneficiaryDocumentType', on_delete=models.SET_NULL, related_name='document_records', null=True)
	starting_date = models.DateField(null=True)
	ending_date = models.DateField(null=True)
	description = models.TextField(default='', null=True)
	is_notification_enabled = models.BooleanField(default=True, null=True)
	notification_period_unit = models.CharField(max_length=50, choices=NOTIFICATION_PERIOD_UNITS, default= "MONTH")
	notification_period_value = models.PositiveIntegerField(default=1, null=True)
	is_active = models.BooleanField(default=True, null=True)
	company = models.ForeignKey('companies.Company', on_delete=models.SET_NULL, related_name='document_records', null=True)
	creator = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True)
	is_deleted = models.BooleanField(default=False, null=True)
	created_at = models.DateTimeField(auto_now_add=True, null=True)
	updated_at = models.DateTimeField(auto_now=True, null=True)

	@property
	def expiration_status(self):
		if not self.ending_date:
			return "NO_EXPIRATION_DATE"
		today = date.today()

		# Compute notification period (ex: 10 jours, 2 semaines, etc.)
		delta = self.get_notification_timedelta()

		# Début de la période de notification
		notify_start_date = self.ending_date - delta

		# Seuil de 20% AVANT la date de fin
		alert_threshold = self.ending_date - (delta * 0.2)

		if today > self.ending_date:
			return "EXPIRED"
		elif today >= alert_threshold:
			return "ALMOST_EXPIRED"
		elif today >= notify_start_date:
			return "EXPIRING_SOON"
		else:
			return "NOT_YET_EXPIRED"

	def get_notification_timedelta(self):
		"""Returns the notification duration as a timedelta."""
		if not self.notification_period_value:
			return timedelta(days=0)

		if self.notification_period_unit == "HOUR":
			return timedelta(hours=self.notification_period_value)
		elif self.notification_period_unit == "DAY":
			return timedelta(days=self.notification_period_value)
		elif self.notification_period_unit == "WEEK":
			return timedelta(weeks=self.notification_period_value)
		elif self.notification_period_unit == "MONTH":
			return timedelta(days=self.notification_period_value * 30)  # Approximation
		return timedelta(days=0)

	def __str__(self):
		return self.name

class ContractTemplate(models.Model):
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
	number = models.CharField(max_length=255, editable=False, null=True)
	title = models.CharField(max_length=255, null=True)
	content = models.TextField(default='', null=True)
	image = models.ForeignKey('medias.File', on_delete=models.SET_NULL, related_name='contract_templates', null=True)
	contract_type = models.CharField(max_length=50, choices=CONTRACT_TYPES, default= "CDI")
	employee = models.ForeignKey('human_ressources.Employee', on_delete=models.SET_NULL, related_name='contract_templates', null=True)
	is_active = models.BooleanField(default=True, null=True)
	company = models.ForeignKey('companies.Company', on_delete=models.SET_NULL, related_name='contract_templates', null=True)
	creator = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, related_name='contract_templates_former', null=True)
	is_deleted = models.BooleanField(default=False, null=True)
	created_at = models.DateTimeField(auto_now_add=True, null=True)
	updated_at = models.DateTimeField(auto_now=True, null=True)

	def __str__(self):
		return self.name
