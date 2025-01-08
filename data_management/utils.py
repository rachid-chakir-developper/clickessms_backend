from data_management.models import CustomFieldValue
from django.db import DatabaseError
import re

class CustomFieldEntityBase:
	@classmethod
	def save_custom_fields(cls, entity_name, instance, custom_field_values):
		if custom_field_values:
			try:
				# Récupérer les valeurs existantes
				existing_values = CustomFieldValue.objects.filter(employee_contract=instance)
				value_map = {val.custom_field_id: val for val in existing_values}

				# Mettre à jour ou créer de nouvelles valeurs
				custom_field_values_to_update = []
				custom_field_values_to_create = []

				for custom_field_value in custom_field_values:
					if custom_field_value.custom_field_id in value_map:
						# Mettre à jour l'existant
						existing_value = value_map[custom_field_value.custom_field_id]
						existing_value.value = custom_field_value.value
						custom_field_values_to_update.append(existing_value)
					else:
						# Créer une nouvelle valeur
						custom_field_values_to_create.append(
							CustomFieldValue(
								employee_contract=instance,
								custom_field_id=custom_field_value.custom_field_id,
								value=custom_field_value.value
							)
						)

				# Exécuter les opérations bulk
				if custom_field_values_to_create:
					CustomFieldValue.objects.bulk_create(custom_field_values_to_create)
				if custom_field_values_to_update:
					CustomFieldValue.objects.bulk_update(custom_field_values_to_update, ['value'])

			except DatabaseError as e:
				# Gérer l'erreur de base de données
				print(f"Erreur lors de l'enregistrement des champs personnalisés : {e}")
				# Vous pouvez aussi lever une exception personnalisée ou gérer le log selon votre besoin
				raise

			except Exception as e:
				# Gérer d'autres exceptions générales
				print(f"Une erreur s'est produite : {e}")
				raise
	@classmethod
	def camel_to_snake(cls, name):
		snake = re.sub(r'(?<!^)(?=[A-Z])', '_', name).lower()
		return snake
	@classmethod
	def set_custom_fields(cls, form_model, instance, custom_field_values):
		"""
		Méthode générique pour enregistrer ou mettre à jour les valeurs des champs personnalisés pour une entité donnée.

		Args:
			form_model (str): Nom de l'entité (par ex. 'employee_contract').
			instance (Model): Instance de l'entité.
			custom_field_values (list): Liste des données des champs personnalisés (dictionnaires ou objets).
		"""
		if not custom_field_values:
			return

		try:
			# Identifier dynamiquement le champ lié dans CustomFieldValue
			relation_field = cls.camel_to_snake(form_model)

			# Vérifier si le champ relationnel existe sur CustomFieldValue
			if not hasattr(CustomFieldValue, relation_field):
				raise ValueError(f"Le modèle CustomFieldValue ne contient pas de champ '{relation_field}'.")

			# Récupérer les valeurs existantes liées à l'entité
			filter_kwargs = {relation_field: instance}
			existing_values = CustomFieldValue.objects.filter(**filter_kwargs)
			value_map = {val.custom_field_id: val for val in existing_values}

			custom_field_values_to_update = []
			custom_field_values_to_create = []

			for custom_field_value in custom_field_values:
				custom_field_id = custom_field_value.get('custom_field_id')
				new_value = custom_field_value.get('value')

				if not custom_field_id:
					continue

				if custom_field_id in value_map:
					# Mettre à jour la valeur existante
					existing_value = value_map[custom_field_id]
					if existing_value.value != new_value:
						existing_value.value = new_value
						custom_field_values_to_update.append(existing_value)
				else:
					# Créer une nouvelle valeur
					custom_field_values_to_create.append(
						CustomFieldValue(
							**{relation_field: instance},  # Associer dynamiquement l'entité
							custom_field_id=custom_field_id,
							value=new_value,
						)
					)

			# Effectuer les opérations en masse
			if custom_field_values_to_create:
				CustomFieldValue.objects.bulk_create(custom_field_values_to_create)

			if custom_field_values_to_update:
				CustomFieldValue.objects.bulk_update(custom_field_values_to_update, ['value'])

		except DatabaseError as e:
			# Gérer les erreurs spécifiques à la base de données
			print(f"Erreur lors de l'enregistrement des champs personnalisés : {e}")
			raise
		except Exception as e:
			# Gérer toutes les autres exceptions
			print(f"Une erreur s'est produite : {e}")
			raise
