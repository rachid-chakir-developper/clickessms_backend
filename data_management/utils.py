from data_management.models import CustomFieldValue
from django.db import DatabaseError

class CustomFieldEntityBase:
	@classmethod
	def save_custom_fields(cls, instance, custom_field_values):
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
