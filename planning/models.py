from django.db import models
from datetime import timedelta, date
import holidays

# Create your models here.
class EmployeeAbsence(models.Model):
	ABSENCE_TYPES = [
		('LEAVE', "Congé"),
		('ABSENCE', "Absence"),
	]
	LEAVE_TYPE_CHOICES = [
		('PAID', 'Congés payés (CP)'),
		('UNPAID', 'Congé Sans Solde'),
		('RWT', 'Temps de Travail Réduit (RTT)'),
		('TEMPORARY', 'Congé Trimestriel (CT)'),
		('ANNUAL', 'Congé Annuel'),
		('SICK', 'Congé Maladie'),
		('MATERNITY', 'Congé Maternité'),
		('PATERNITY', 'Congé Paternité'),
		('PARENTAL', 'Congé Parental'),
		('BEREAVEMENT', 'Congé de Décès'),
		('MARRIAGE', 'Congé de Mariage'),
		('STUDY', 'Congé de Formation'),
		('ADOPTION', "Congé d'Adoption"),
		('SABBATICAL', 'Congé Sabbatique'),
		('CAREGIVER', 'Congé de Proche Aidant'),
		('FAMILY_SOLIDARITY', 'Congé de Solidarité Familiale'),
		('MOBILITY', 'Congé de Mobilité'),
		('RECONVERSION', 'Congé de Reconversion'),
		('BUSINESS_CREATION', 'Congé pour Création ou Reprise d’Entreprise'),
		('MANDATE', 'Congé pour Exercice de Mandat'),
		('CHILD_SICKNESS', 'Congé pour Enfant Malade'),
		('CHILD_BEREAVEMENT', 'Congé pour Deuil d’un Enfant'),

		('ABSENCE', "Absence absence Injustifiée"),
	    ('SICK_LEAVE', 'Arrêt Maladie'),
	    ('WORK_ACCIDENT', 'Accident du Travail'),
	    ('PROFESSIONAL_ILLNESS', 'Maladie Professionnelle'),
	    ('LONG_TERM_LEAVE', 'Arrêt Longue Durée'),
	    ('CHILDCARE_LEAVE', 'Garde d’Enfant Malade'),
	    ('FAMILY_REASON', 'Absence pour Motif Familial'),
	    ('UNPAID_AUTHORIZED', 'Absence Autorisée Sans Solde'),
	    ('LATE', 'Retard Non Justifié'),
	    ('EXCEPTIONAL', 'Absence Exceptionnelle'),
	    ('RELIGIOUS_HOLIDAY', 'Jour Férié Religieux (Non Chômé)'),
	    ('TRAINING_INTERRUPTION', 'Interruption de Formation'),
	    ('CONTRACT_SUSPENSION', 'Suspension du Contrat (hors maladie)'),
	    ('OTHER', 'Autre'),

	]
	STATUS_CHOICES = [
		('PENDING', 'En attente de traitement'),
		('APPROVED', 'Approuvé'),
		('REJECTED', 'Rejeté'),
	    ('NOT_JUSTIFIED', 'Non Justifié'),
	    ('TO_JUSTIFY', 'À Justifier'),
	    ('JUSTIFIED', 'Justifié'),
	]
	number = models.CharField(max_length=255, editable=False, null=True)
	label = models.CharField(max_length=255, blank=True, null=True)
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
	entry_type = models.CharField(max_length=50, choices=ABSENCE_TYPES, default='ABSENCE')
	leave_type = models.CharField(max_length=50, choices=LEAVE_TYPE_CHOICES, default='ABSENCE')
	status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='PENDING')
	approved_by = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, related_name='approved_employee_absences', null=True)
	rejected_by = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, related_name='rejected_employee_absences', null=True)
	put_on_hold_by = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, related_name='put_on_hold_by_employee_absences', null=True)
	company = models.ForeignKey('companies.Company', on_delete=models.SET_NULL, related_name='employee_absences', null=True)
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

	def generate_label(self):
	    absence_items = self.employees.all()
	    if not absence_items.exists():
	        return ''

	    employee_names = []
	    for item in absence_items:
	        if item.employee:
	            last_name = item.employee.last_name.upper()
	            first_name = item.employee.first_name.capitalize()
	            employee_names.append(f"{last_name} {first_name}")

	    names_str = ", ".join(employee_names)
	    leave_type_label = dict(self.LEAVE_TYPE_CHOICES).get(self.leave_type, 'Unknown Type')
	    start_date_str = self.starting_date_time.strftime('%d/%m/%Y') if self.starting_date_time else '??/??/????'
	    duration = self.duration  # Durée de l'absence

	    return f"{leave_type_label} - {names_str} - {start_date_str} - {duration} jour(s)"

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

class EmployeeShift(models.Model):
	SHIFT_CHOICES = [
		('MORNING', 'Matin'),
		('AFTERNOON', 'Après-midi'),
		('NIGHT', 'Nuit'),
	]
	STATUS_CHOICES = [
		('PENDING', 'En Attente'),
		('APPROVED', 'Approuvé'),
		('REJECTED', 'Rejeté'),
		('COMPLETED', 'Terminé'),
		('CANCELLED', 'Annulé'),
	]
	number = models.CharField(max_length=255, editable=False, null=True)
	title = models.CharField(max_length=255,default='', blank=True, null=True)
	description = models.TextField(default='', blank=True, null=True)
	employee = models.ForeignKey('human_ressources.Employee', on_delete=models.SET_NULL, related_name='employee_shifts', null=True)
	employee_group = models.ForeignKey('human_ressources.EmployeeGroup', on_delete=models.SET_NULL, related_name='employee_shifts', null=True)
	starting_date_time = models.DateTimeField(null=True)
	ending_date_time = models.DateTimeField(null=True)
	scheduled_date_time = models.DateTimeField(null=True)
	is_recurring = models.BooleanField(default=False) # Indique si le shift est récurrent
	recurrence_rule = models.TextField(blank=True, null=True) # Ex : 'RRULE:FREQ=WEEKLY;INTERVAL=1;BYDAY=MO,WE,FR;COUNT=10'
	shift_type = models.CharField(max_length=50, choices=SHIFT_CHOICES, default='MORNING')
	status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='APPROVED')
	company = models.ForeignKey('companies.Company', on_delete=models.SET_NULL, related_name='employee_shifts', null=True)
	creator = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, related_name='employee_shifts', null=True)
	is_deleted = models.BooleanField(default=False, null=True)
	created_at = models.DateTimeField(auto_now_add=True, null=True)
	updated_at = models.DateTimeField(auto_now=True, null=True)


	def __str__(self):
		return f"{self.employee.first_name} {self.employee.last_name} - {self.starting_date_time} to {self.ending_date_time} ({self.recurrence_rule})"

