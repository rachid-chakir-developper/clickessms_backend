import graphene
from graphene_django import DjangoObjectType
from django.core.files.uploadedfile import InMemoryUploadedFile, UploadedFile
from graphql_jwt.decorators import login_required
from graphene_file_upload.scalars import Upload

from django.db.models import Q

from computers.models import Software, TheBackup, ThePassword
from medias.models import Folder, File

class SoftwareType(DjangoObjectType):
	class Meta:
		model = Software
		fields = "__all__"
	image = graphene.String()
	def resolve_image( instance, info, **kwargs ):
		return instance.image and info.context.build_absolute_uri(instance.image.image.url)

class SoftwareNodeType(graphene.ObjectType):
	nodes = graphene.List(SoftwareType)
	total_count = graphene.Int()

class SoftwareFilterInput(graphene.InputObjectType):
	keyword = graphene.String(required=False)
	starting_date_time = graphene.DateTime(required=False)
	ending_date_time = graphene.DateTime(required=False)

class SoftwareInput(graphene.InputObjectType):
	id = graphene.ID(required=False)
	number = graphene.String(required=False)
	name = graphene.String(required=True)
	bar_code = graphene.String(required=False)
	is_blocked = graphene.Boolean(required=False)
	is_stock_auto = graphene.Boolean(required=False)
	designation = graphene.String(required=False)
	buying_price_ht = graphene.Float(required=False)
	tva = graphene.Float(required=False)
	quantity = graphene.Int(required=False)
	description = graphene.String(required=False)
	observation = graphene.String(required=False)
	is_active = graphene.Boolean(required=False)

class TheBackupType(DjangoObjectType):
	class Meta:
		model = TheBackup
		fields = "__all__"

class TheBackupNodeType(graphene.ObjectType):
	nodes = graphene.List(TheBackupType)
	total_count = graphene.Int()

class TheBackupFilterInput(graphene.InputObjectType):
	keyword = graphene.String(required=False)
	starting_date_time = graphene.DateTime(required=False)
	ending_date_time = graphene.DateTime(required=False)

class TheBackupInput(graphene.InputObjectType):
	id = graphene.ID(required=False)
	number = graphene.String(required=False)
	label = graphene.String(required=True)
	cycle_in_days = graphene.Float(required=False)
	last_backup_date_time = graphene.DateTime(required=False)
	description = graphene.String(required=False)
	observation = graphene.String(required=False)
	is_active = graphene.Boolean(required=False)

class ThePasswordType(DjangoObjectType):
	class Meta:
		model = ThePassword
		fields = "__all__"

class ThePasswordNodeType(graphene.ObjectType):
	nodes = graphene.List(ThePasswordType)
	total_count = graphene.Int()

class ThePasswordFilterInput(graphene.InputObjectType):
	keyword = graphene.String(required=False)
	starting_date_time = graphene.DateTime(required=False)
	ending_date_time = graphene.DateTime(required=False)

class ThePasswordInput(graphene.InputObjectType):
	id = graphene.ID(required=False)
	number = graphene.String(required=False)
	label = graphene.String(required=True)
	identifier = graphene.String(required=True)
	password_text = graphene.String(required=True)
	link = graphene.String(required=True)
	description = graphene.String(required=False)
	observation = graphene.String(required=False)
	is_active = graphene.Boolean(required=False)

class ComputersQuery(graphene.ObjectType):
	softwares = graphene.Field(SoftwareNodeType, software_filter= SoftwareFilterInput(required=False), offset = graphene.Int(required=False), limit = graphene.Int(required=False), page = graphene.Int(required=False))
	software = graphene.Field(SoftwareType, id = graphene.ID())
	the_backups = graphene.Field(TheBackupNodeType, the_backup_filter= TheBackupFilterInput(required=False), offset = graphene.Int(required=False), limit = graphene.Int(required=False), page = graphene.Int(required=False))
	the_backup = graphene.Field(TheBackupType, id = graphene.ID())
	the_passwords = graphene.Field(ThePasswordNodeType, the_password_filter= ThePasswordFilterInput(required=False), offset = graphene.Int(required=False), limit = graphene.Int(required=False), page = graphene.Int(required=False))
	the_password = graphene.Field(ThePasswordType, id = graphene.ID())

	def resolve_softwares(root, info, software_filter=None, offset=None, limit=None, page=None):
		# We can easily optimize query count in the resolve method
		user = info.context.user
		company = user.the_current_company
		total_count = 0
		softwares = Software.objects.filter(company=company, is_deleted=False)
		if software_filter:
			keyword = software_filter.get('keyword', '')
			starting_date_time = software_filter.get('starting_date_time')
			ending_date_time = software_filter.get('ending_date_time')
			if keyword:
				softwares = softwares.filter(Q(name__icontains=keyword) | Q(designation__icontains=keyword) | Q(bar_code__icontains=keyword))
			if starting_date_time:
				softwares = softwares.filter(created_at__gte=starting_date_time)
			if ending_date_time:
				softwares = softwares.filter(created_at__lte=ending_date_time)
		softwares = softwares.order_by('-created_at')
		total_count = softwares.count()
		if page:
			offset = limit * (page - 1)
		if offset is not None and limit is not None:
			softwares = softwares[offset:offset + limit]
		return SoftwareNodeType(nodes=softwares, total_count=total_count)

	def resolve_software(root, info, id):
		# We can easily optimize query count in the resolve method
		user = info.context.user
		company = user.the_current_company
		try:
			software = Software.objects.get(pk=id, company=company)
		except Software.DoesNotExist:
			software = None
		return software

	def resolve_the_backups(root, info, the_backup_filter=None, offset=None, limit=None, page=None):
		# We can easily optimize query count in the resolve method
		user = info.context.user
		company = user.the_current_company
		total_count = 0
		the_backups = TheBackup.objects.filter(company=company, is_deleted=False)
		if the_backup_filter:
			keyword = the_backup_filter.get('keyword', '')
			starting_date_time = the_backup_filter.get('starting_date_time')
			ending_date_time = the_backup_filter.get('ending_date_time')
			if keyword:
				the_backups = the_backups.filter(Q(name__icontains=keyword) | Q(designation__icontains=keyword) | Q(bar_code__icontains=keyword))
			if starting_date_time:
				the_backups = the_backups.filter(created_at__gte=starting_date_time)
			if ending_date_time:
				the_backups = the_backups.filter(created_at__lte=ending_date_time)
		the_backups = the_backups.order_by('-created_at')
		total_count = the_backups.count()
		if page:
			offset = limit * (page - 1)
		if offset is not None and limit is not None:
			the_backups = the_backups[offset:offset + limit]
		return TheBackupNodeType(nodes=the_backups, total_count=total_count)

	def resolve_the_backup(root, info, id):
		# We can easily optimize query count in the resolve method
		user = info.context.user
		company = user.the_current_company
		try:
			the_backup = TheBackup.objects.get(pk=id, company=company)
		except TheBackup.DoesNotExist:
			the_backup = None
		return the_backup

	def resolve_the_passwords(root, info, the_password_filter=None, offset=None, limit=None, page=None):
		# We can easily optimize query count in the resolve method
		user = info.context.user
		company = user.the_current_company
		total_count = 0
		the_passwords = ThePassword.objects.filter(company=company, is_deleted=False)
		if the_password_filter:
			keyword = the_password_filter.get('keyword', '')
			starting_date_time = the_password_filter.get('starting_date_time')
			ending_date_time = the_password_filter.get('ending_date_time')
			if keyword:
				the_passwords = the_passwords.filter(Q(name__icontains=keyword) | Q(designation__icontains=keyword) | Q(bar_code__icontains=keyword))
			if starting_date_time:
				the_passwords = the_passwords.filter(created_at__gte=starting_date_time)
			if ending_date_time:
				the_passwords = the_passwords.filter(created_at__lte=ending_date_time)
		the_passwords = the_passwords.order_by('-created_at')
		total_count = the_passwords.count()
		if page:
			offset = limit * (page - 1)
		if offset is not None and limit is not None:
			the_passwords = the_passwords[offset:offset + limit]
		return ThePasswordNodeType(nodes=the_passwords, total_count=total_count)

	def resolve_the_password(root, info, id):
		# We can easily optimize query count in the resolve method
		user = info.context.user
		company = user.the_current_company
		try:
			the_password = ThePassword.objects.get(pk=id, company=company)
		except ThePassword.DoesNotExist:
			the_password = None
		return the_password

#************************************************************************

class CreateSoftware(graphene.Mutation):
	class Arguments:
		software_data = SoftwareInput(required=True)
		image = Upload(required=False)

	software = graphene.Field(SoftwareType)

	def mutate(root, info, image=None, software_data=None):
		creator = info.context.user
		software = Software(**software_data)
		software.creator = creator
		software.company = creator.the_current_company
		if info.context.FILES:
			# file1 = info.context.FILES['1']
			if image and isinstance(image, UploadedFile):
				image_file = software.image
				if not image_file:
					image_file = File()
					image_file.creator = creator
				image_file.image = image
				image_file.save()
				software.image = image_file
		software.save()
		folder = Folder.objects.create(name=str(software.id)+'_'+software.name,creator=creator)
		software.folder = folder
		software.save()
		return CreateSoftware(software=software)

class UpdateSoftware(graphene.Mutation):
	class Arguments:
		id = graphene.ID()
		software_data = SoftwareInput(required=True)
		image = Upload(required=False)

	software = graphene.Field(SoftwareType)

	def mutate(root, info, id, image=None, software_data=None):
		creator = info.context.user
		try:
			software = Software.objects.get(pk=id, company=creator.the_current_company)
		except Software.DoesNotExist:
			raise e
		Software.objects.filter(pk=id).update(**software_data)
		software.refresh_from_db()
		if not software.folder or software.folder is None:
			folder = Folder.objects.create(name=str(software.id)+'_'+software.name,creator=creator)
			Software.objects.filter(pk=id).update(folder=folder)
		if not image and software.image:
			image_file = software.image
			image_file.delete()
		if info.context.FILES:
			# file1 = info.context.FILES['1']
			if image and isinstance(image, UploadedFile):
				image_file = software.image
				if not image_file:
					image_file = File()
					image_file.creator = creator
				image_file.image = image
				image_file.save()
				software.image = image_file
			software.save()
		return UpdateSoftware(software=software)
		
class UpdateSoftwareState(graphene.Mutation):
	class Arguments:
		id = graphene.ID()

	software = graphene.Field(SoftwareType)
	done = graphene.Boolean()
	success = graphene.Boolean()
	message = graphene.String()

	def mutate(root, info, id, software_fields=None):
		creator = info.context.user
		try:
			software = Software.objects.get(pk=id, company=creator.the_current_company)
		except Software.DoesNotExist:
			raise e
		done = True
		success = True
		message = ''
		try:
			Software.objects.filter(pk=id).update(is_active=not software.is_active)
			software.refresh_from_db()
		except Exception as e:
			done = False
			success = False
			software=None
			message = "Une erreur s'est produite."
		return UpdateSoftwareState(done=done, success=success, message=message,software=software)


class DeleteSoftware(graphene.Mutation):
	class Arguments:
		id = graphene.ID()

	software = graphene.Field(SoftwareType)
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
			software = Software.objects.get(pk=id, company=current_user.the_current_company)
		except Software.DoesNotExist:
			raise e
		if current_user.is_superuser:
			software = Software.objects.get(pk=id)
			software.delete()
			deleted = True
			success = True
		else:
			message = "Vous n'êtes pas un Superuser."
		return DeleteSoftware(deleted=deleted, success=success, message=message, id=id)

#*************************************************************************#
#************************************************************************

class CreateTheBackup(graphene.Mutation):
	class Arguments:
		the_backup_data = TheBackupInput(required=True)

	the_backup = graphene.Field(TheBackupType)

	def mutate(root, info, the_backup_data=None):
		creator = info.context.user
		the_backup = TheBackup(**the_backup_data)
		the_backup.creator = creator
		the_backup.company = creator.the_current_company
		the_backup.save()
		return CreateTheBackup(the_backup=the_backup)

class UpdateTheBackup(graphene.Mutation):
	class Arguments:
		id = graphene.ID()
		the_backup_data = TheBackupInput(required=True)

	the_backup = graphene.Field(TheBackupType)

	def mutate(root, info, id, the_backup_data=None):
		creator = info.context.user
		try:
			the_backup = TheBackup.objects.get(pk=id, company=creator.the_current_company)
		except TheBackup.DoesNotExist:
			raise e
		TheBackup.objects.filter(pk=id).update(**the_backup_data)
		the_backup.refresh_from_db()
		return UpdateTheBackup(the_backup=the_backup)
		
class UpdateTheBackupState(graphene.Mutation):
	class Arguments:
		id = graphene.ID()

	the_backup = graphene.Field(TheBackupType)
	done = graphene.Boolean()
	success = graphene.Boolean()
	message = graphene.String()

	def mutate(root, info, id, the_backup_fields=None):
		creator = info.context.user
		try:
			the_backup = TheBackup.objects.get(pk=id, company=creator.the_current_company)
		except TheBackup.DoesNotExist:
			raise e
		done = True
		success = True
		message = ''
		try:
			TheBackup.objects.filter(pk=id).update(is_active=not the_backup.is_active)
			the_backup.refresh_from_db()
		except Exception as e:
			done = False
			success = False
			the_backup=None
			message = "Une erreur s'est produite."
		return UpdateTheBackupState(done=done, success=success, message=message,the_backup=the_backup)


class DeleteTheBackup(graphene.Mutation):
	class Arguments:
		id = graphene.ID()

	the_backup = graphene.Field(TheBackupType)
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
			the_backup = TheBackup.objects.get(pk=id, company=current_user.the_current_company)
		except TheBackup.DoesNotExist:
			raise e
		if current_user.is_superuser:
			the_backup = TheBackup.objects.get(pk=id)
			the_backup.delete()
			deleted = True
			success = True
		else:
			message = "Vous n'êtes pas un Superuser."
		return DeleteTheBackup(deleted=deleted, success=success, message=message, id=id)

#*************************************************************************#
#************************************************************************

class CreateThePassword(graphene.Mutation):
	class Arguments:
		the_password_data = ThePasswordInput(required=True)

	the_password = graphene.Field(ThePasswordType)

	def mutate(root, info, the_password_data=None):
		creator = info.context.user
		the_password = ThePassword(**the_password_data)
		the_password.creator = creator
		the_password.company = creator.the_current_company
		the_password.save()
		return CreateThePassword(the_password=the_password)

class UpdateThePassword(graphene.Mutation):
	class Arguments:
		id = graphene.ID()
		the_password_data = ThePasswordInput(required=True)

	the_password = graphene.Field(ThePasswordType)

	def mutate(root, info, id, the_password_data=None):
		creator = info.context.user
		try:
			the_password = ThePassword.objects.get(pk=id, company=creator.the_current_company)
		except ThePassword.DoesNotExist:
			raise e
		ThePassword.objects.filter(pk=id).update(**the_password_data)
		the_password.refresh_from_db()
		return UpdateThePassword(the_password=the_password)
		
class UpdateThePasswordState(graphene.Mutation):
	class Arguments:
		id = graphene.ID()

	the_password = graphene.Field(ThePasswordType)
	done = graphene.Boolean()
	success = graphene.Boolean()
	message = graphene.String()

	def mutate(root, info, id, the_password_fields=None):
		creator = info.context.user
		try:
			the_password = ThePassword.objects.get(pk=id, company=creator.the_current_company)
		except ThePassword.DoesNotExist:
			raise e
		done = True
		success = True
		message = ''
		try:
			ThePassword.objects.filter(pk=id).update(is_active=not the_password.is_active)
			the_password.refresh_from_db()
		except Exception as e:
			done = False
			success = False
			the_password=None
			message = "Une erreur s'est produite."
		return UpdateThePasswordState(done=done, success=success, message=message,the_password=the_password)


class DeleteThePassword(graphene.Mutation):
	class Arguments:
		id = graphene.ID()

	the_password = graphene.Field(ThePasswordType)
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
			the_password = ThePassword.objects.get(pk=id, company=current_user.the_current_company)
		except ThePassword.DoesNotExist:
			raise e
		if current_user.is_superuser:
			the_password = ThePassword.objects.get(pk=id)
			the_password.delete()
			deleted = True
			success = True
		else:
			message = "Vous n'êtes pas un Superuser."
		return DeleteThePassword(deleted=deleted, success=success, message=message, id=id)

#*************************************************************************#

class ComputersMutation(graphene.ObjectType):
	create_software = CreateSoftware.Field()
	update_software = UpdateSoftware.Field()
	update_software_state = UpdateSoftwareState.Field()
	delete_software = DeleteSoftware.Field()

	create_the_backup = CreateTheBackup.Field()
	update_the_backup = UpdateTheBackup.Field()
	update_the_backup_state = UpdateTheBackupState.Field()
	delete_the_backup = DeleteTheBackup.Field()

	create_the_password = CreateThePassword.Field()
	update_the_password = UpdateThePassword.Field()
	update_the_password_state = UpdateThePasswordState.Field()
	delete_the_password = DeleteThePassword.Field()