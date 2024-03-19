from django.db import models
from accounts.models import User

# Create your models here.

class DataModel(models.Model):
	id = models.AutoField(primary_key=True)
	name = models.CharField(max_length=255)
	descreption = models.TextField(default='', null=True)
	creator = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

	def __str__(self):
		return str(self.id)

	class Meta:
		abstract = True

class AbsenceReason(DataModel):
	def __str__(self):
		return str(self.id)

class UndesirableEventNormalType(DataModel):
	def __str__(self):
		return str(self.id)

class UndesirableEventSeriousType(DataModel):
	def __str__(self):
		return str(self.id)

class UndesirableEventFrequency(DataModel):
	def __str__(self):
		return str(self.id)