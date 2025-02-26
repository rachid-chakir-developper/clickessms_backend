from django.db import models

# Create your models here.
class DashboardComment(models.Model):
	COMMENT_TYPE_CHOICES = [
		("SYNTHESIS", "Synthesis"),
		('ACTIVITY', 'Activity'),
		('GRAPH', 'Graph'),
		('OTHER', 'Other'),
	]
	text = models.TextField(default='', null=True)
	establishment = models.ForeignKey("companies.Establishment", on_delete=models.SET_NULL, related_name="dashboard_comments", null=True)
	year = models.CharField(max_length=255, null=True)
	month = models.CharField(max_length=255, null=True)
	comment_type = models.CharField(max_length=50, choices=COMMENT_TYPE_CHOICES, default= "SYNTHESIS", null=True)
	company = models.ForeignKey('companies.Company', on_delete=models.SET_NULL, related_name='dashboard_comments', null=True)
	creator = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True)
	created_at = models.DateTimeField(auto_now_add=True, null=True)
	updated_at = models.DateTimeField(auto_now=True, null=True)

	def __str__(self):
		return self.text
