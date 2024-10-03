from django.db import models

# Create your models here.
class Comment(models.Model):
	text = models.TextField(default='', null=True)
	image = models.ForeignKey('medias.File', on_delete=models.SET_NULL, related_name='comment_image', null=True)
	parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE)
	ticket = models.ForeignKey('works.Ticket', on_delete=models.SET_NULL, related_name='comments', null=True)
	task = models.ForeignKey('works.Task', on_delete=models.SET_NULL, related_name='comments', null=True)
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
	author_email = models.EmailField(max_length=254, null=True)
	satisfaction = models.CharField(max_length=50, choices=SATISFACTIONS, default= "MEDIUM")
	comment = models.TextField(default='', null=True)
	author = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, related_name='author_image', null=True)
	creator = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True)
	created_at = models.DateTimeField(auto_now_add=True, null=True)
	updated_at = models.DateTimeField(auto_now=True, null=True)
	
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