from django.db import models

# Create your models here.
class ValidationWorkflow(models.Model):
	WORKFLOW_TYPE_CHOICES = [
		("LEAVE", "Demande de congé"),
		("EXPENSE", "Note de frais"),
		("TASK", "Demande d’intervention"),
	]

	# Type de demande concernée (congé, note de frais, etc.)
	request_type = models.CharField(max_length=50, choices=WORKFLOW_TYPE_CHOICES)
	observation = models.TextField(default='', null=True)
	description = models.TextField(default='', null=True)
	# Entreprise à laquelle le workflow est rattaché
	company = models.ForeignKey('companies.Company', on_delete=models.SET_NULL, related_name='validation_workflows', null=True)

	# Utilisateur ayant créé ce workflow
	creator = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True, related_name='validation_workflows')

	is_active = models.BooleanField(default=True)

	# Suppression logique
	is_deleted = models.BooleanField(default=False)

	# Dates de création et de dernière mise à jour
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	def __str__(self):
		return f"{self.company.name} - {self.get_request_type_display()}"

class ValidationStep(models.Model):

	# Lien vers le workflow parent
	workflow = models.ForeignKey(
		ValidationWorkflow,
		on_delete=models.CASCADE,
		related_name='validation_steps',
		null=True
	)

	# Ordre d'exécution de l'étape
	order = models.PositiveIntegerField()

	comment = models.TextField(null=True, blank=True)

	# Utilisateur ayant créé cette étape
	creator = models.ForeignKey(
		'accounts.User',
		on_delete=models.SET_NULL,
		null=True,
		related_name='validation_steps'
	)

	# Suppression logique
	is_deleted = models.BooleanField(default=False)

	# Dates de création et de mise à jour
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		ordering = ['order']

	def __str__(self):
		return f"{self.workflow} - Étape {self.order}"



# Règle personnalisée de validation (par rôle, service, ou utilisateur)
class ValidationRule(models.Model):
	# Types de validateurs autorisés
	VALIDATOR_TYPE_CHOICES = [
		("ROLE", "Rôle"),
		("POSITION", "Poste spécifique"),
		("MANAGER", "Manager du demandeur"),
	]
	validation_step = models.ForeignKey(
		ValidationStep,
		on_delete=models.CASCADE,
		related_name="validation_rules"
	)

	# Cibles (demandeurs)
	target_employee_groups = models.ManyToManyField(
		"human_ressources.EmployeeGroup",
		blank=True,
		related_name="rules_as_target_employee_group"
	)

	target_employees = models.ManyToManyField(
		"human_ressources.Employee",
		blank=True,
		related_name="rules_as_target_employee"
	)
	target_roles = models.JSONField(
		null=True, blank=True,
		help_text="Liste des rôles des demandeurs concernés (format JSON)"
	)
	target_positions = models.ManyToManyField(
		"data_management.EmployeePosition",
		blank=True,
		related_name="rules_as_target_position"
	)

	# Validateurs
	validator_type = models.CharField(max_length=20, choices=VALIDATOR_TYPE_CHOICES, default="ROLE")

	validator_employees = models.ManyToManyField(
		"human_ressources.Employee",
		blank=True,
		related_name="rules_as_validator_employee"
	)
	validator_roles = models.JSONField(
		null=True, blank=True,
		help_text="Liste des rôles des validateurs (format JSON)"
	)
	validator_positions = models.ManyToManyField(
		"data_management.EmployeePosition",
		blank=True,
		related_name="rules_as_validator_position"
	)

	# Condition d'expression logique (optionnel)
	condition_expression = models.TextField(blank=True, null=True)

	comment = models.TextField(null=True, blank=True)

	is_active = models.BooleanField(default=True)
	is_deleted = models.BooleanField(default=False)

	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	def __str__(self):
		return f"Règle étape {self.validation_step.order}"



class FallbackRule(models.Model):
	# Types de fallback possibles
	FALLBACK_TYPE_CHOICES = [
		("REPLACEMENT", "Remplaçant déclaré"),
		("HIERARCHY", "Supérieur hiérarchique"),
		("ADMIN", "Notifier l’administrateur"),
	]

	# Étape concernée par cette règle de fallback
	validation_step = models.ForeignKey(
		ValidationStep,
		on_delete=models.CASCADE,
		related_name="fallback_rules",
		null=True
	)

	# Type de fallback (remplaçant, hiérarchie, admin)
	fallback_type = models.CharField(max_length=50, choices=FALLBACK_TYPE_CHOICES)

	# Plusieurs rôles de secours possibles
	fallback_roles = models.JSONField(null=True, blank=True)

	# Plusieurs employés de secours possibles
	fallback_employees = models.ManyToManyField(
		'human_ressources.Employee',
		blank=True,
		related_name='fallback_rules'
	)

	# Plusieurs postes de secours possibles
	fallback_positions = models.ManyToManyField(
		'data_management.EmployeePosition',
		blank=True,
		related_name='fallback_rules'
	)

	# Ordre d'évaluation des fallbacks
	order = models.PositiveIntegerField()

	# Créateur de cette règle
	creator = models.ForeignKey(
		'accounts.User',
		on_delete=models.SET_NULL,
		null=True,
		related_name='fallback_rules'
	)

	# Suppression logique
	is_deleted = models.BooleanField(default=False)

	# Dates de création et de mise à jour
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		ordering = ["order"]

	def __str__(self):
		return f"Fallback #{self.order} pour étape {self.validation_step.order if self.validation_step else 'N/A'}"



