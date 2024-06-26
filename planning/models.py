from django.db import models
from datetime import timedelta, date
import holidays

# Create your models here.
class EmployeeAbsence(models.Model):
	LEAVE_TYPE_CHOICES = [
        ('PAID', 'Congés payés (CP)'),
        ('UNPAID', 'Congé Sans Solde'),
        ('RWT', 'Temps de Travail Réduit (RTT)'),
        ('TEMPORARY', 'Congé Temporaire (CT)'),
        ('ANNUAL', 'Congé Annuel'),
        ('SICK', 'Congé Maladie'),
        ('MATERNITY', 'Congé Maternité'),
        ('PATERNITY', 'Congé Paternité'),
        ('PARENTAL', 'Congé Parental'),
        ('BEREAVEMENT', 'Congé de Décès'),
        ('MARRIAGE', 'Congé de Mariage'),
        ('STUDY', 'Congé de Formation'),
        ('ADOPTION', "Congé d'Adoption"),
        ('ABSENCE', "Absence"),
	]
	STATUS_CHOICES = [
        ('PENDING', 'En Attente'),
        ('APPROVED', 'Approuvé'),
        ('REJECTED', 'Rejeté'),
    ]
	number = models.CharField(max_length=255, editable=False, null=True)
	title = models.CharField(max_length=255)
	document = models.ForeignKey('medias.File', on_delete=models.SET_NULL, related_name='employee_absences', null=True)
	starting_date_time = models.DateTimeField(null=True)
	ending_date_time = models.DateTimeField(null=True)
	reasons = models.ManyToManyField('data_management.AbsenceReason', related_name='employee_absences')
	other_reasons = models.CharField(max_length=255, null=True)
	message = models.TextField(default='', null=True)
	comment = models.TextField(default='', null=True)
	observation = models.TextField(default='', null=True)
	folder = models.ForeignKey('medias.Folder', on_delete=models.SET_NULL, null=True)
	employee = models.ForeignKey('human_ressources.Employee', on_delete=models.SET_NULL, related_name='employee_absences', null=True)
	leave_type = models.CharField(max_length=50, choices=LEAVE_TYPE_CHOICES, default='ABSENCE')
	status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='PENDING')
	company = models.ForeignKey('companies.Company', on_delete=models.SET_NULL, related_name='employee_absences', null=True)
	approved_by = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, related_name='approved_employee_absences', null=True)
	rejected_by = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, related_name='rejected_employee_absences', null=True)
	put_on_hold_by = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, related_name='put_on_hold_by_employee_absences', null=True)
	creator = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, related_name='employee_absences', null=True)
	is_deleted = models.BooleanField(default=False, null=True)
	created_at = models.DateTimeField(auto_now_add=True, null=True)
	updated_at = models.DateTimeField(auto_now=True, null=True)

	@property
	def duration(self):
		if self.starting_date_time and self.ending_date_time:
			start_date = self.starting_date_time.date()
			end_date = self.ending_date_time.date()
			if end_date < start_date:
				return 0
			fr_holidays = holidays.France(years=range(start_date.year, end_date.year + 1))
			total_days = 0
			current_date = start_date
			while current_date <= end_date:
				if current_date.weekday() < 5 and current_date not in fr_holidays:
					total_days += 1
				current_date += timedelta(days=1)
			return total_days
		return 0

	def __str__(self):
		return str(self.id)

# Create your models here.
class EmployeeAbsenceItem(models.Model):
	employee_absence = models.ForeignKey(EmployeeAbsence, on_delete=models.SET_NULL, related_name='employees', null=True)
	employee = models.ForeignKey('human_ressources.Employee', on_delete=models.SET_NULL, related_name='employee_absence_items', null=True)
	creator = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, related_name='employee_absence_items', null=True)
	created_at = models.DateTimeField(auto_now_add=True, null=True)
	updated_at = models.DateTimeField(auto_now=True, null=True)

	def __str__(self):
		return str(self.id)
