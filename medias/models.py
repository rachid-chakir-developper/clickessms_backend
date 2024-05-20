from django.db import models
from moviepy.editor import VideoFileClip
import os
from django.conf import settings

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
		return self.name

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