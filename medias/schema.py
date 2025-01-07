import os
import graphene
from graphene_django import DjangoObjectType
from graphql_jwt.decorators import login_required
from graphene_file_upload.scalars import Upload
from django.template import Template, Context
from django.utils.html import escape, mark_safe
import re
from datetime import date, datetime

from medias.models import Folder, File, ContractTemplate
from human_ressources.models import EmployeeContract

class ChildrenFolderType(DjangoObjectType):
	class Meta:
		model = Folder
		fields = "__all__"

class MediaInput(graphene.InputObjectType):
	id = graphene.ID(required=False)
	image = Upload(required=False)
	video = Upload(required=False)
	file = Upload(required=False)
	media = Upload(required=False)
	caption = graphene.String(required=False)
		
def getFileTypeFromFileInstance(file_instance=None):
	# Extraire l'extension du fichier depuis l'URL
	_, file_extension = os.path.splitext(file_instance.file.url)

	# Mapper l'extension à une catégorie (video, image, autre)
	if file_extension.lower() in ['.mp4', '.avi', '.mkv', '.mov']:
		return 'VIDEO'
	elif file_extension.lower() in ['.jpg', '.jpeg', '.png', '.gif']:
		return 'IMAGE'
	else:
		return file_instance.file_type

class ChildrenFileType(DjangoObjectType):
	class Meta:
		model = File
		fields = "__all__"
	def resolve_name( instance, info, **kwargs ):
		name = instance.name if instance.name and instance.name!='' else instance.caption
		return name if name and name!='' else 'Fichier sans nom'
	def resolve_file( instance, info, **kwargs ):
		return instance.file and info.context.build_absolute_uri(instance.file.url)
	def resolve_video( instance, info, **kwargs ):
		return instance.video and info.context.build_absolute_uri(instance.video.url)
	def resolve_thumbnail( instance, info, **kwargs ):
		return instance.thumbnail and info.context.build_absolute_uri(instance.thumbnail.url)
	def resolve_image( instance, info, **kwargs ):
		return instance.image and info.context.build_absolute_uri(instance.image.url)
	def resolve_file_type ( instance, info, **kwargs ):
		return getFileTypeFromFileInstance(file_instance=instance)

class FolderType(DjangoObjectType):
	class Meta:
		model = Folder
		fields = "__all__"
	folders = graphene.List(ChildrenFolderType)
	files = graphene.List(ChildrenFileType)
	def resolve_folders ( instance, info, **kwargs ):
		return instance.children_folders.all()
	def resolve_files ( instance, info, **kwargs ):
		return instance.file_set.all()

class FolderInput(graphene.InputObjectType):
	id = graphene.ID(required=False)
	number = graphene.String(required=False)
	name = graphene.String(required=True)
	folder_type = graphene.String(required=False)
	description = graphene.String(required=False)
	observation = graphene.String(required=False)
	is_active = graphene.Boolean(required=False)
	folder_id = graphene.Int(name="folder", required=False)

class FileType(DjangoObjectType):
	class Meta:
		model = File
		fields = "__all__"
	def resolve_name( instance, info, **kwargs ):
		name = instance.name if instance.name and instance.name!='' else instance.caption
		return name if name and name!='' else 'Fichier sans nom'
	def resolve_file( instance, info, **kwargs ):
		return instance.file and info.context.build_absolute_uri(instance.file.url)
	def resolve_video( instance, info, **kwargs ):
		return instance.video and info.context.build_absolute_uri(instance.video.url)
	def resolve_thumbnail( instance, info, **kwargs ):
		return instance.thumbnail and info.context.build_absolute_uri(instance.thumbnail.url)
	def resolve_image( instance, info, **kwargs ):
		return instance.image and info.context.build_absolute_uri(instance.image.url)

class FileInput(graphene.InputObjectType):
	id = graphene.ID(required=False)
	number = graphene.String(required=False)
	name = graphene.String(required=True)
	file_type = graphene.String(required=False)
	description = graphene.String(required=False)
	observation = graphene.String(required=False)
	is_active = graphene.Boolean(required=False)
	folder_id = graphene.Int(name="folder", required=False)


class ContractTemplateType(DjangoObjectType):
	class Meta:
		model = ContractTemplate
		fields = "__all__"

	image = graphene.String()

	def resolve_image(instance, info, **kwargs):
		return instance.image and info.context.build_absolute_uri(
			instance.image.image.url
		)

class ContractTemplateNodeType(graphene.ObjectType):
	nodes = graphene.List(ContractTemplateType)
	total_count = graphene.Int()

class ContractTemplateFilterInput(graphene.InputObjectType):
	keyword = graphene.String(required=False)
	starting_date_time = graphene.DateTime(required=False)
	ending_date_time = graphene.DateTime(required=False)
	contract_type = graphene.String(required=False)

class ContractTemplateInput(graphene.InputObjectType):
	id = graphene.ID(required=False)
	number = graphene.String(required=False)
	title = graphene.String(required=False)
	content = graphene.String(required=False)
	is_active = graphene.Boolean(required=False)
	contract_type = graphene.String(required=False)

class MediasQuery(graphene.ObjectType):
	folders = graphene.List(FolderType)
	folder = graphene.Field(FolderType, id = graphene.ID())
	files = graphene.List(FileType)
	file = graphene.Field(FileType, id = graphene.ID())
	contract_templates = graphene.Field(ContractTemplateNodeType, contract_template_filter= ContractTemplateFilterInput(required=False), id_company = graphene.ID(required=False), offset = graphene.Int(required=False), limit = graphene.Int(required=False), page = graphene.Int(required=False))
	contract_template = graphene.Field(ContractTemplateType, id = graphene.ID())

	def resolve_folders(root, info):
		# We can easily optimize query count in the resolve method
		folders = Folder.objects.all()
		return folders

	def resolve_folder(root, info, id):
		# We can easily optimize query count in the resolve method
		folder = Folder.objects.get(pk=id)
		return folder

	def resolve_files(root, info):
		# We can easily optimize query count in the resolve method
		files = File.objects.all()
		return files

	def resolve_file(root, info, id):
		# We can easily optimize query count in the resolve method
		file = File.objects.get(pk=id)
		return file

	def resolve_contract_templates(root, info, contract_template_filter=None, id_company=None, offset=None, limit=None, page=None):
		# We can easily optimize query count in the resolve method
		user = info.context.user
		company = user.current_company if user.current_company is not None else user.company
		total_count = 0
		contract_templates = ContractTemplate.objects.filter(company__id=id_company) if id_company else ContractTemplate.objects.filter(company=company)
		if contract_template_filter:
			keyword = contract_template_filter.get('keyword', '')
			contract_type = contract_template_filter.get('contract_type')
			starting_date_time = contract_template_filter.get('starting_date_time')
			ending_date_time = contract_template_filter.get('ending_date_time')
			if contract_type:
				contract_templates = contract_templates.filter(contract_type=contract_type)
			if keyword:
				contract_templates = contract_templates.filter(Q(title__icontains=keyword))
			if starting_date_time:
				contract_templates = contract_templates.filter(created_at__gte=starting_date_time)
			if ending_date_time:
				contract_templates = contract_templates.filter(created_at__lte=ending_date_time)
		contract_templates = contract_templates.order_by('-created_at')
		total_count = contract_templates.count()
		if page:
			offset = limit * (page - 1)
		if offset is not None and limit is not None:
			contract_templates = contract_templates[offset:offset + limit]
		return ContractTemplateNodeType(nodes=contract_templates, total_count=total_count)

	def resolve_contract_template(root, info, id):
		# We can easily optimize query count in the resolve method
		try:
			contract_template = ContractTemplate.objects.get(pk=id)
		except ContractTemplate.DoesNotExist:
			contract_template = None
		return contract_template

#*******************************************************************#

class CreateFolder(graphene.Mutation):
	class Arguments:
		folder_data = FolderInput(required=True)

	folder = graphene.Field(FolderType)

	def mutate(root, info, folder_data=None):
		creator = info.context.user
		folder = Folder(**folder_data)
		folder.creator = creator
		folder.save()
		return CreateFolder(folder=folder)

class UpdateFolder(graphene.Mutation):
	class Arguments:
		id = graphene.ID()
		folder_data = FolderInput(required=True)

	folder = graphene.Field(FolderType)

	def mutate(root, info, id, folder_data=None):
		Folder.objects.filter(pk=id).update(**folder_data)
		folder = Folder.objects.get(pk=id)
		return UpdateFolder(folder=folder)


class DeleteFolder(graphene.Mutation):
	class Arguments:
		id = graphene.ID()

	folder = graphene.Field(FolderType)
	id = graphene.ID()
	deleted = graphene.Boolean()
	success = graphene.Boolean()
	message = graphene.String()

	def mutate(root, info, id):
		deleted = False
		success = False
		message = ''
		current_user = info.context.user
		try:
			folder = Folder.objects.get(pk=id)
			if current_user.is_superuser or folder.creator.id == current_user.id:
				folder.delete()
				deleted = True
				success = True
			else:
				message = "Vous n'êtes pas un Superuser."
		except Folder.DoesNotExist:
			message = "Ce fichier n'exite pas pour le supprimer."
		return DeleteFolder(deleted=deleted, success=success, message=message, id=id)

#*******************************************************************#

class CreateFile(graphene.Mutation):
	class Arguments:
		file_data = FileInput(required=True)
		file_upload = Upload(required=True)

	file = graphene.Field(FileType)

	def mutate(root, info, file_upload, file_data=None):
		creator = info.context.user
		file = File(**file_data)
		file.creator = creator
		file.company = creator.current_company if creator.current_company is not None else creator.company
		if info.context.FILES:
			# file_upload = info.context.FILES['1']
			file.file = file_upload
		file.save()
		return CreateFile(file=file)

class UpdateFile(graphene.Mutation):
	class Arguments:
		id = graphene.ID()
		file_data = FileInput(required=True)
		file_upload = Upload(required=False)

	file = graphene.Field(FileType)

	def mutate(root, info, id, file_upload=None, file_data=None):
		File.objects.filter(pk=id).update(**file_data)
		file = File.objects.get(pk=id)
		if info.context.FILES:
			# file_upload = info.context.FILES['1']
			file.file = file_upload
			file.save()
		return UpdateFile(file=file)


class DeleteFile(graphene.Mutation):
	class Arguments:
		id = graphene.ID()

	file = graphene.Field(FileType)
	id = graphene.ID()
	deleted = graphene.Boolean()
	success = graphene.Boolean()
	message = graphene.String()

	def mutate(root, info, id):
		deleted = False
		success = False
		message = ''
		current_user = info.context.user
		try:
			file = File.objects.get(pk=id)
			if current_user.is_superuser or file.creator.id == current_user.id:
				file.delete()
				deleted = True
				success = True
			else:
				message = "Vous n'êtes pas un Superuser."
		except File.DoesNotExist:
			message = "Ce fichier n'exite pas pour le supprimer."
		return DeleteFile(deleted=deleted, success=success, message=message, id=id)


#********************************************************************************************************************
#***************************************************************************

class CreateContractTemplate(graphene.Mutation):
	class Arguments:
		contract_template_data = ContractTemplateInput(required=True)
		image = Upload(required=False)

	contract_template = graphene.Field(ContractTemplateType)

	def mutate(root, info, image=None, contract_template_data=None):
		creator = info.context.user
		contract_template = ContractTemplate(**contract_template_data)
		contract_template.creator = creator
		contract_template.company = creator.current_company if creator.current_company is not None else creator.company
		if info.context.FILES:
			# file1 = info.context.FILES['1']
			if image and isinstance(image, UploadedFile):
				image_file = contract_template.image
				if not image_file:
					image_file = File()
					image_file.creator = creator
				image_file.image = image
				image_file.save()
				contract_template.image = image_file
		contract_template.save()
		return CreateContractTemplate(contract_template=contract_template)

class UpdateContractTemplate(graphene.Mutation):
	class Arguments:
		id = graphene.ID()
		contract_template_data = ContractTemplateInput(required=True)
		image = Upload(required=False)

	contract_template = graphene.Field(ContractTemplateType)

	def mutate(root, info, id, image=None, contract_template_data=None):
		creator = info.context.user
		ContractTemplate.objects.filter(pk=id).update(**contract_template_data)
		contract_template = ContractTemplate.objects.get(pk=id)
		if not image and contract_template.image:
			image_file = contract_template.image
			image_file.delete()
		if info.context.FILES:
			# file1 = info.context.FILES['1']
			if image and isinstance(image, UploadedFile):
				image_file = contract_template.image
				if not image_file:
					image_file = File()
					image_file.creator = creator
				image_file.image = image
				image_file.save()
				contract_template.image = image_file
		contract_template.save()
		return UpdateContractTemplate(contract_template=contract_template)

class UpdateContractTemplateState(graphene.Mutation):
	class Arguments:
		id = graphene.ID()

	contract_template = graphene.Field(ContractTemplateType)
	done = graphene.Boolean()
	success = graphene.Boolean()
	message = graphene.String()

	def mutate(root, info, id, contract_template_fields=None):
		creator = info.context.user
		done = True
		success = True
		contract_template = None
		message = ''
		try:
			contract_template = ContractTemplate.objects.get(pk=id)
			ContractTemplate.objects.filter(pk=id).update(is_active=not contract_template.is_active)
			contract_template.refresh_from_db()
		except Exception as e:
			done = False
			success = False
			contract_template=None
			message = "Une erreur s'est produite."
		return UpdateContractTemplateState(done=done, success=success, message=message,contract_template=contract_template)


def get_field_value(obj, field):
	"""
	Recursively retrieves the value of a nested field, supporting
	`ManyToMany`, `ForeignKey`, and direct field attributes.
	"""
	parts = field.split('__')
	value = obj

	for part in parts:
		if value is None:
			return ''
		
		# Handling ManyToMany relationships or reverse ForeignKey
		if hasattr(value, 'all'):
			related_values = []
			for related_obj in value.all():
				related_values.append(get_field_value(related_obj, '__'.join(parts[1:])))
			return '; '.join(related_values)
		else:
			# If the object has a display method for the current part
			display_method = f'get_{part}_display'
			if hasattr(value, display_method):
				value = getattr(value, display_method)()
			else:
				value = getattr(value, part, None)
	return value or ''

class GenerateContractContent(graphene.Mutation):
	class Arguments:
		employee_contract_id = graphene.ID(required=True)
		contract_template_id = graphene.ID(required=True)

	contract_content = graphene.String()
	success = graphene.Boolean()
	message = graphene.String()

	def mutate(root, info, employee_contract_id, contract_template_id):
		creator = info.context.user
		success = True
		contract_content = None
		message = ''
		try:
			employee_contract = EmployeeContract.objects.get(pk=employee_contract_id)
			contract_template = ContractTemplate.objects.get(pk=contract_template_id)
			variables = re.findall(r'{{\s*(\w+(?:__\w+)?)(?:.size=(\d+))?\s*}}', contract_template.content)
			context = {}
			print(variables)
			for var, size in variables:
				try:
					keys = var.split('__')
					model = keys[0]
					key = keys[1]
					field_path = '__'.join(keys[1:])
					value = None
					size = int(size) if size else None
					
					# Vérification du modèle spécifié dans la variable
					if model == 'EmployeeContract':
						value = employee_contract
						# Vérification pour les champs personnalisés
						if key.startswith('custom_field_'):
							custom_field_value = employee_contract.custom_field_values.filter(custom_field__key=key).first()
							if custom_field_value:
								value = custom_field_value.value

					elif model == 'Employee':
						value = employee_contract.employee
						# Vérification pour les champs personnalisés
						if key.startswith('custom_field_'):
							custom_field_id = key.split('_')[-1]
							custom_field = CustomField.objects.filter(id=custom_field_id).first()
							if custom_field:
								custom_field_value = CustomFieldValue.objects.filter(
									custom_field=custom_field,
									employee=employee_contract.employee
								).first()
								if custom_field_value:
									value = custom_field_value.value

					elif model == 'Company':
						value = employee_contract.employee.company
						# Vérification pour les champs personnalisés
						if key.startswith('custom_field_'):
							custom_field_id = key.split('_')[-1]
							custom_field = CustomField.objects.filter(id=custom_field_id).first()
							if custom_field:
								custom_field_value = CustomFieldValue.objects.filter(
									custom_field=custom_field,
									employee__company=employee_contract.employee.company
								).first()
								if custom_field_value:
									value = custom_field_value.value

					elif model == 'Establishment':
						if employee_contract.establishments.exists():
							value = employee_contract.establishments.first().establishment
							# Vérification pour les champs personnalisés
							if key.startswith('custom_field_'):
								custom_field_id = key.split('_')[-1]
								custom_field = CustomField.objects.filter(id=custom_field_id).first()
								if custom_field:
									custom_field_value = CustomFieldValue.objects.filter(
										custom_field=custom_field,
										employee_contract__establishments__establishment=value
									).first()
									if custom_field_value:
										value = custom_field_value.value

					else:
						raise ValueError(f"Modèle non reconnu: {model}")

					# Get the field value using the get_field_value function
					if value and not key.startswith('custom_field_'):
						value = get_field_value(value, field_path)

					# Formatage des dates ou conversion en chaîne
					if isinstance(value, (date, datetime)):
						context[var] = escape(value.strftime('%d/%m/%Y'))
					else:
						if isinstance(value, File) and hasattr(value, "image") and value.image:
							image_url = escape(info.context.build_absolute_uri(value.image.url))
							alt_text = escape(value.name) if value.name else ""
							if size is not None:
								var = f'{var}.size={size}'
							context[var] = mark_safe(f'<img src="{image_url}" alt="{alt_text}" height="{size if size else 100}px"/>')
						else:
							context[var] = escape(str(value)) if value is not None else ''
				except Exception as e:
					print(f"Exception **** {e}")
					context[var] = ''

			template = Template(contract_template.content)
			contract_content = template.render(Context(context))
		except Exception as e:
			print(e)
			success = False
			contract_content=None
			message = "Une erreur s'est produite."
		return GenerateContractContent(success=success, message=message,contract_content=contract_content)

class DeleteContractTemplate(graphene.Mutation):
	class Arguments:
		id = graphene.ID()

	contract_template = graphene.Field(ContractTemplateType)
	id = graphene.ID()
	deleted = graphene.Boolean()
	success = graphene.Boolean()
	message = graphene.String()

	def mutate(root, info, id):
		deleted = False
		success = False
		message = ''
		current_user = info.context.user
		if current_user.is_superuser:
			contract_template = ContractTemplate.objects.get(pk=id)
			contract_template.delete()
			deleted = True
			success = True
		else:
			message = "Vous n'êtes pas un Superuser."
		return DeleteContractTemplate(deleted=deleted, success=success, message=message, id=id)

#************************************************************************

#********************************************************************************************************************

class MediasMutation(graphene.ObjectType):
	create_folder = CreateFolder.Field()
	update_folder = UpdateFolder.Field()
	delete_folder = DeleteFolder.Field()

	create_file = CreateFile.Field()
	update_file = UpdateFile.Field()
	delete_file = DeleteFile.Field()

	create_contract_template = CreateContractTemplate.Field()
	update_contract_template = UpdateContractTemplate.Field()
	update_contract_template_state = UpdateContractTemplateState.Field()
	delete_contract_template = DeleteContractTemplate.Field()
	generate_contract_content = GenerateContractContent.Field()