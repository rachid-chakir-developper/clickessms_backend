import graphene
from graphene_django import DjangoObjectType
from django.core.files.uploadedfile import InMemoryUploadedFile, UploadedFile
from graphql_jwt.decorators import login_required
from graphene_file_upload.scalars import Upload

from django.db.models import Q

from the_mailer.models import SentEmail
from medias.models import Folder, File
from medias.schema import MediaInput
from accounts.models import User
from human_ressources.models import Employee
from recruitment.models import JobCandidateApplication

from the_mailer.services.mail_services import send_this_email

class SentEmailType(DjangoObjectType):
	class Meta:
		model = SentEmail
		fields = "__all__"

	image = graphene.String()

	def resolve_image(instance, info, **kwargs):
		return instance.image and info.context.build_absolute_uri(
			instance.image.image.url
		)

class SentEmailNodeType(graphene.ObjectType):
	nodes = graphene.List(SentEmailType)
	total_count = graphene.Int()

class SentEmailFilterInput(graphene.InputObjectType):
	keyword = graphene.String(required=False)
	starting_date_time = graphene.DateTime(required=False)
	ending_date_time = graphene.DateTime(required=False)

class SentEmailInput(graphene.InputObjectType):
	id = graphene.ID(required=False)
	recipient = graphene.String(required=False)
	subject = graphene.String(required=False)
	body = graphene.String(required=False)

class DefaultSentEmailType(graphene.ObjectType):
	recipient = graphene.String(required=False)
	subject = graphene.String(required=False)
	body = graphene.String(required=False)

class emailUserInfosInput(graphene.InputObjectType):
	user = graphene.Int(required=False)
	employee = graphene.Int(required=False)
	default_password = graphene.String(required=False)

class DefaultSentEmailFilterInput(graphene.InputObjectType):
	job_candidate_application = graphene.Int(required=False)
	email_user_infos = graphene.Field(emailUserInfosInput, required=False)

class TheMailerQuery(graphene.ObjectType):
	sent_emails = graphene.Field(SentEmailNodeType, sent_email_filter= SentEmailFilterInput(required=False), id_company = graphene.ID(required=False), offset = graphene.Int(required=False), limit = graphene.Int(required=False), page = graphene.Int(required=False))
	sent_email = graphene.Field(SentEmailType, id = graphene.ID())
	default_sent_email = graphene.Field(DefaultSentEmailType, default_sent_email_filter= DefaultSentEmailFilterInput(required=False))
	def resolve_sent_emails(root, info, sent_email_filter=None, id_company=None, offset=None, limit=None, page=None):
		# We can easily optimize query count in the resolve method
		user = info.context.user
		company = user.the_current_company
		total_count = 0
		sent_emails = SentEmail.objects.filter(company=company, is_deleted=False)
		if sent_email_filter:
			keyword = sent_email_filter.get('keyword', '')
			starting_date_time = sent_email_filter.get('starting_date_time')
			ending_date_time = sent_email_filter.get('ending_date_time')
			if keyword:
				sent_emails = sent_emails.filter(Q(subject__icontains=keyword))
			if starting_date_time:
				sent_emails = sent_emails.filter(created_at__gte=starting_date_time)
			if ending_date_time:
				sent_emails = sent_emails.filter(created_at__lte=ending_date_time)
		sent_emails = sent_emails.order_by('-created_at')
		total_count = sent_emails.count()
		if page:
			offset = limit * (page - 1)
		if offset is not None and limit is not None:
			sent_emails = sent_emails[offset:offset + limit]
		return SentEmailNodeType(nodes=sent_emails, total_count=total_count)

	def resolve_sent_email(root, info, id):
		# We can easily optimize query count in the resolve method
		try:
			sent_email = SentEmail.objects.get(pk=id)
		except SentEmail.DoesNotExist:
			sent_email = None
		return sent_email

	def resolve_default_sent_email(root, info, default_sent_email_filter=None):
		"""Récupère l'email par défaut à envoyer en fonction du statut de la candidature."""
		
		# Initialisation d'un email vide
		default_sent_email = DefaultSentEmailType(recipient='', subject='', body='')

		if default_sent_email_filter:
			job_candidate_application_id = default_sent_email_filter.get('job_candidate_application', None)
			email_user_infos = default_sent_email_filter.get('email_user_infos', None)

			if job_candidate_application_id:
				try:
					job_candidate_application = JobCandidateApplication.objects.get(pk=job_candidate_application_id)
					recipient, subject, body = job_candidate_application.get_default_sent_email()

					# Mise à jour de l'email par défaut avec les valeurs récupérées
					default_sent_email.recipient = recipient
					default_sent_email.subject = subject
					default_sent_email.body = body

				except JobCandidateApplication.DoesNotExist:
					pass
			elif email_user_infos:
				user_id = email_user_infos.get('user', None)
				employee_id = email_user_infos.get('employee', None)
				default_password = email_user_infos.get('default_password', None)
				user=None
				if employee_id:
					try:
						employee = Employee.objects.get(pk=employee_id)
						user= employee.user

					except User.DoesNotExist:
						pass
				elif user_id:
					try:
						user = User.objects.get(pk=user_id)
					except User.DoesNotExist:
						pass
				if user:
					recipient, subject, body = user.get_default_sent_email(default_password)

					# Mise à jour de l'email par défaut avec les valeurs récupérées
					default_sent_email.recipient = recipient
					default_sent_email.subject = subject
					default_sent_email.body = body

		return default_sent_email


#***************************************************************************

class SendTheEmail(graphene.Mutation):
	class Arguments:
		sent_email_data = SentEmailInput(required=True)
		image = Upload(required=False)
		files = graphene.List(MediaInput, required=False)

	sent_email = graphene.Field(DefaultSentEmailType)
	sent = graphene.Boolean()
	success = graphene.Boolean()
	message = graphene.String()

	def mutate(root, info, image=None, files=None, sent_email_data=None):
		creator = info.context.user
		sent_email=None
		sent = False
		success = False
		message = ''
		try:
			subject = sent_email_data.get('subject', '')
			body = sent_email_data.get('body', '')
			recipient= sent_email_data.get('recipient', '')
			company = creator.the_current_company
			employee = creator.get_employee_in_company()
			reply_to_email = employee.email if employee.email else creator.email
			success = send_this_email(
				subject=subject,
				html_content=body,
				from_name=company.name,
				from_email=company.email if company.email else reply_to_email,
				to_email=[recipient],
				reply_to_email=[reply_to_email]
			)
			sent = success
		except Exception as e:
			message = "Une erreur est survenue lors de l'envoi."
		return SendTheEmail(sent=sent, success=success, message=message, sent_email=sent_email)

class CreateSentEmail(graphene.Mutation):
	class Arguments:
		sent_email_data = SentEmailInput(required=True)
		image = Upload(required=False)
		files = graphene.List(MediaInput, required=False)

	sent_email = graphene.Field(SentEmailType)

	def mutate(root, info, image=None, files=None, sent_email_data=None):
		creator = info.context.user
		sent_email = SentEmail(**sent_email_data)
		sent_email.creator = creator
		sent_email.company = creator.the_current_company
		sent_email.save()
		return CreateSentEmail(sent_email=sent_email)

class UpdateSentEmail(graphene.Mutation):
	class Arguments:
		id = graphene.ID()
		sent_email_data = SentEmailInput(required=True)
		image = Upload(required=False)
		files = graphene.List(MediaInput, required=False)

	sent_email = graphene.Field(SentEmailType)

	def mutate(root, info, id, sent_email_data=None):
		creator = info.context.user
		SentEmail.objects.filter(pk=id).update(**sent_email_data)
		sent_email = SentEmail.objects.get(pk=id)
		return UpdateSentEmail(sent_email=sent_email)

class DeleteSentEmail(graphene.Mutation):
	class Arguments:
		id = graphene.ID()

	sent_email = graphene.Field(SentEmailType)
	id = graphene.ID()
	deleted = graphene.Boolean()
	success = graphene.Boolean()
	message = graphene.String()

	def mutate(root, info, id):
		deleted = False
		success = False
		message = ''
		current_user = info.context.user
		sent_email = SentEmail.objects.get(pk=id)
		if current_user.is_superuser or sent_email.creator==current_user:
			sent_email.delete()
			deleted = True
			success = True
		else:
			message = "Vous n'êtes pas un Superuser."
		return DeleteSentEmail(deleted=deleted, success=success, message=message, id=id)

#************************************************************************

#*******************************************************************************************************************************

class TheMailerMutation(graphene.ObjectType):
	send_the_email = SendTheEmail.Field()
	create_sent_email = CreateSentEmail.Field()
	update_sent_email = UpdateSentEmail.Field()
	delete_sent_email = DeleteSentEmail.Field()
	