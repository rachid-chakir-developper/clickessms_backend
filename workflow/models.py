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
	# Types de validateurs autorisés
	VALIDATOR_TYPE_CHOICES = [
		("ROLE", "Rôle"),
		("POSITION", "Poste spécifique"),
		("MANAGER", "Manager du demandeur"),
	]

	# Lien vers le workflow parent
	workflow = models.ForeignKey('ValidationWorkflow', on_delete=models.CASCADE, related_name='steps')

	# Ordre d'exécution de l'étape
	step_order = models.PositiveIntegerField()

	# Conditions pour activer l'étape : rôle ou service du demandeur
	role_condition = models.CharField(max_length=100, blank=True, null=True)
	service_condition = models.CharField(max_length=100, blank=True, null=True)

	# Type de validateur choisi (rôle, poste ou manager)
	validator_type = models.CharField(max_length=20, choices=VALIDATOR_TYPE_CHOICES)

	# Rôle utilisé comme validateur (si applicable)
	role = models.ForeignKey('accounts.Role', null=True, blank=True, on_delete=models.SET_NULL)

	# Poste utilisé comme validateur (si applicable)
	position = models.ForeignKey('data_management.EmployeePosition', null=True, blank=True, on_delete=models.SET_NULL)

	# Nombre de validations requises pour valider l'étape
	required_approval_count = models.PositiveIntegerField(default=1)

	# Condition d'expression logique pour évaluer dynamiquement l'étape (optionnel)
	condition_expression = models.TextField(blank=True, null=True)

	# Utilisateur ayant créé cette étape
	creator = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True, related_name='validation_steps')

	# Suppression logique
	is_deleted = models.BooleanField(default=False)

	# Dates de création et de mise à jour
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		ordering = ['step_order']

	def __str__(self):
		return f"{self.workflow} - Étape {self.step_order}"


class FallbackRule(models.Model):

	# Types de fallback possibles
	FALLBACK_TYPE_CHOICES = [
		("REPLACEMENT", "Remplaçant déclaré"),
		("HIERARCHY", "Supérieur hiérarchique"),
		("ADMIN", "Notifier l’administrateur"),
	]

	# Étape concernée par cette règle de fallback
	step = models.ForeignKey('ValidationStep', related_name="fallbacks", on_delete=models.CASCADE)

	# Type de fallback (remplaçant, hiérarchie, admin)
	fallback_type = models.CharField(max_length=50, choices=FALLBACK_TYPE_CHOICES)

	# Rôle de secours (optionnel)
	fallback_role = models.ForeignKey('accounts.Role', null=True, blank=True, on_delete=models.SET_NULL)

	# Poste de secours (optionnel)
	fallback_position = models.ForeignKey('data_management.EmployeePosition', null=True, blank=True, on_delete=models.SET_NULL)

	# Ordre d'évaluation des fallbacks
	order = models.PositiveIntegerField()

	# Créateur de cette règle
	creator = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True, related_name='fallback_rules')

	# Suppression logique
	is_deleted = models.BooleanField(default=False)

	# Dates de création et de mise à jour
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		ordering = ["order"]

	def __str__(self):
		return f"Fallback #{self.order} pour étape {self.step.step_order}"


