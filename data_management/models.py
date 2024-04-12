from django.db import models
from accounts.models import User

# Create your models here.
class PhoneNumber(models.Model):
	id = models.AutoField(primary_key=True)
	name = models.CharField(default='Sans nom', max_length=255, null=True)
	phone = models.CharField(max_length=255)
	description = models.TextField(default='', null=True)
	creator = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

	def __str__(self):
		return str(self.number)

# Create your models here.
class HomeAddress(models.Model):
	id = models.AutoField(primary_key=True)
	name = models.CharField(default='Sans nom', max_length=255, null=True)
	address = models.TextField(default='', null=True)
	description = models.TextField(default='', null=True)
	creator = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

	def __str__(self):
		return str(self.address)

# Create your models here.
class DataModel(models.Model):
	id = models.AutoField(primary_key=True)
	name = models.CharField(max_length=255)
	description = models.TextField(default='', null=True)
	creator = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

	def __str__(self):
		return str(self.id)

	class Meta:
		abstract = True


class EstablishmentType(DataModel):
	def __str__(self):
		return str(self.id)
		
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

class MeetingReason(DataModel):
	def __str__(self):
		return str(self.id)