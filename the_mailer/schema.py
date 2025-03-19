import graphene
from graphene_django import DjangoObjectType
from django.core.files.uploadedfile import InMemoryUploadedFile, UploadedFile
from graphql_jwt.decorators import login_required
from graphene_file_upload.scalars import Upload

from django.db.models import Q

from the_mailer.models import SentEmail
from medias.models import Folder, File
from medias.schema import MediaInput
from recruitment.models import JobCandidateApplication

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

class DefaultSentEmailFilterInput(graphene.InputObjectType):
	job_candidate_application = graphene.Int(required=False)

class TheMailerQuery(graphene.ObjectType):
	sent_emails = graphene.Field(SentEmailNodeType, sent_email_filter= SentEmailFilterInput(required=False), id_company = graphene.ID(required=False), offset = graphene.Int(required=False), limit = graphene.Int(required=False), page = graphene.Int(required=False))
	sent_email = graphene.Field(SentEmailType, id = graphene.ID())
	default_sent_email = graphene.Field(DefaultSentEmailType, default_sent_email_filter= DefaultSentEmailFilterInput(required=False))
	def resolve_sent_emails(root, info, sent_email_filter=None, id_company=None, offset=None, limit=None, page=None):
		# We can easily optimize query count in the resolve method
		user = info.context.user
		company = user.the_current_company
		total_count = 0
		sent_emails = SentEmail.objects.filter(company__id=id_company) if id_company else SentEmail.objects.filter(company=company)
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
		default_sent_email = DefaultSentEmailType(recipient='hhh', subject='', body='')

		if default_sent_email_filter:
			print('****************default_sent_email_filter**********')
			print(default_sent_email_filter)
			job_candidate_application_id = default_sent_email_filter.get('job_candidate_application')

			if job_candidate_application_id:
				print('****************job_candidate_application_id**********')
				print(job_candidate_application_id)
				try:
					job_candidate_application = JobCandidateApplication.objects.get(pk=job_candidate_application_id)
					recipient, subject, body = job_candidate_application.get_default_sent_email()

					print('****************heeerrrr11**********')
					# Mise à jour de l'email par défaut avec les valeurs récupérées
					default_sent_email.recipient = recipient
					default_sent_email.subject = subject
					default_sent_email.body = body

				except JobCandidateApplication.DoesNotExist:
					print(f'****************DoesNotExist********** ')

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
			sent = True
			success = True
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
		if current_user.is_superuser:
			sent_email = SentEmail.objects.get(pk=id)
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
	