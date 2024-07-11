import graphene
from graphene_django import DjangoObjectType
from django.core.files.uploadedfile import InMemoryUploadedFile, UploadedFile
from graphql_jwt.decorators import login_required
from graphene_file_upload.scalars import Upload

from django.db.models import Q

from activities.models import TransmissionEvent, TransmissionEventBeneficiary, BeneficiaryAbsence, BeneficiaryAbsenceItem
from data_management.models import AbsenceReason
from medias.models import Folder, File
from human_ressources.models import Beneficiary

class TransmissionEventBeneficiaryType(DjangoObjectType):
    class Meta:
        model = TransmissionEventBeneficiary
        fields = "__all__"

class BeneficiaryAbsenceItemType(DjangoObjectType):
    class Meta:
        model = BeneficiaryAbsenceItem
        fields = "__all__"

class BeneficiaryAbsenceType(DjangoObjectType):
    class Meta:
        model = BeneficiaryAbsence
        fields = "__all__"

class BeneficiaryAbsenceNodeType(graphene.ObjectType):
    nodes = graphene.List(BeneficiaryAbsenceType)
    total_count = graphene.Int()

class BeneficiaryAbsenceFilterInput(graphene.InputObjectType):
    keyword = graphene.String(required=False)
    starting_date_time = graphene.DateTime(required=False)
    ending_date_time = graphene.DateTime(required=False)
    beneficiaries = graphene.List(graphene.Int, required=False)

class TransmissionEventType(DjangoObjectType):
    class Meta:
        model = TransmissionEvent
        fields = "__all__"
    image = graphene.String()
    def resolve_image( instance, info, **kwargs ):
        return instance.image and info.context.build_absolute_uri(instance.image.image.url)

class TransmissionEventNodeType(graphene.ObjectType):
    nodes = graphene.List(TransmissionEventType)
    total_count = graphene.Int()

class TransmissionEventFilterInput(graphene.InputObjectType):
    keyword = graphene.String(required=False)
    starting_date_time = graphene.DateTime(required=False)
    ending_date_time = graphene.DateTime(required=False)
    beneficiaries = graphene.List(graphene.Int, required=False)

class TransmissionEventInput(graphene.InputObjectType):
    id = graphene.ID(required=False)
    number = graphene.String(required=False)
    title = graphene.String(required=True)
    starting_date_time = graphene.DateTime(required=False)
    ending_date_time = graphene.DateTime(required=False)
    description = graphene.String(required=False)
    observation = graphene.String(required=False)
    is_active = graphene.Boolean(required=False)
    employee_id = graphene.Int(name="employee", required=False)
    beneficiaries = graphene.List(graphene.Int, required=False)

class BeneficiaryAbsenceInput(graphene.InputObjectType):
    id = graphene.ID(required=False)
    number = graphene.String(required=False)
    title = graphene.String(required=False)
    starting_date_time = graphene.DateTime(required=False)
    ending_date_time = graphene.DateTime(required=False)
    comment = graphene.String(required=False)
    observation = graphene.String(required=False)
    employee_id = graphene.Int(name="employee", required=False)
    beneficiaries = graphene.List(graphene.Int, required=False)
    reasons = graphene.List(graphene.Int, required=False)
    other_reasons = graphene.String(required=False)

class ActivitiesQuery(graphene.ObjectType):
    transmission_events = graphene.Field(TransmissionEventNodeType, transmission_event_filter= TransmissionEventFilterInput(required=False), offset = graphene.Int(required=False), limit = graphene.Int(required=False), page = graphene.Int(required=False))
    transmission_event = graphene.Field(TransmissionEventType, id = graphene.ID())
    beneficiary_absences = graphene.Field(BeneficiaryAbsenceNodeType, beneficiary_absence_filter= BeneficiaryAbsenceFilterInput(required=False), offset = graphene.Int(required=False), limit = graphene.Int(required=False), page = graphene.Int(required=False))
    beneficiary_absence = graphene.Field(BeneficiaryAbsenceType, id = graphene.ID())
    def resolve_transmission_events(root, info, transmission_event_filter=None, offset=None, limit=None, page=None):
        # We can easily optimize query count in the resolve method
        user = info.context.user
        company = user.current_company if user.current_company is not None else user.company
        total_count = 0
        transmission_events = TransmissionEvent.objects.filter(company=company)
        if not user.can_manage_activity():
            if user.is_manager():
                transmission_events = transmission_events.filter(Q(beneficiaries__beneficiary__beneficiary_entries__establishments__managers__employee=user.get_employee_in_company()) | Q(creator=user))
            else:
                transmission_events = transmission_events.filter(creator=user)
        if transmission_event_filter:
            keyword = transmission_event_filter.get('keyword', '')
            starting_date_time = transmission_event_filter.get('starting_date_time')
            ending_date_time = transmission_event_filter.get('ending_date_time')
            beneficiaries = transmission_event_filter.get('beneficiaries')
            if beneficiaries:
                transmission_events = transmission_events.filter(beneficiaries__beneficiary__id__in=beneficiaries)
            if keyword:
                transmission_events = transmission_events.filter(Q(title__icontains=keyword) | Q(description__icontains=keyword))
            if starting_date_time:
                transmission_events = transmission_events.filter(starting_date_time__gte=starting_date_time)
            if ending_date_time:
                transmission_events = transmission_events.filter(starting_date_time__lte=ending_date_time)
        transmission_events = transmission_events.order_by('-created_at').distinct()
        total_count = transmission_events.count()
        if page:
            offset = limit * (page - 1)
        if offset is not None and limit is not None:
            transmission_events = transmission_events[offset:offset + limit]
        return TransmissionEventNodeType(nodes=transmission_events, total_count=total_count)

    def resolve_transmission_event(root, info, id):
        # We can easily optimize query count in the resolve method
        try:
            transmission_event = TransmissionEvent.objects.get(pk=id)
        except TransmissionEvent.DoesNotExist:
            transmission_event = None
        return transmission_event

    def resolve_beneficiary_absences(root, info, beneficiary_absence_filter=None, offset=None, limit=None, page=None):
        # We can easily optimize query count in the resolve method
        user = info.context.user
        company = user.current_company if user.current_company is not None else user.company
        total_count = 0
        beneficiary_absences = BeneficiaryAbsence.objects.filter(company=company)
        if not user.can_manage_activity():
            if user.is_manager():
                beneficiary_absences = beneficiary_absences.filter(Q(beneficiaries__beneficiary__beneficiary_entries__establishments__managers__employee=user.get_employee_in_company()) | Q(creator=user))
            else:
                beneficiary_absences = beneficiary_absences.filter(creator=user)
        if beneficiary_absence_filter:
            keyword = beneficiary_absence_filter.get('keyword', '')
            starting_date_time = beneficiary_absence_filter.get('starting_date_time')
            ending_date_time = beneficiary_absence_filter.get('ending_date_time')
            beneficiaries = beneficiary_absence_filter.get('beneficiaries')
            if beneficiaries:
                beneficiary_absences = beneficiary_absences.filter(beneficiaries__beneficiary__id__in=beneficiaries)
            if keyword:
                beneficiary_absences = beneficiary_absences.filter(Q(title__icontains=keyword) | Q(description__icontains=keyword))
            if starting_date_time:
                beneficiary_absences = beneficiary_absences.filter(starting_date_time__gte=starting_date_time)
            if ending_date_time:
                beneficiary_absences = beneficiary_absences.filter(starting_date_time__lte=ending_date_time)

        beneficiary_absences = beneficiary_absences.order_by('-created_at').distinct()
        total_count = beneficiary_absences.count()
        if page:
            offset = limit * (page - 1)
        if offset is not None and limit is not None:
            beneficiary_absences = beneficiary_absences[offset:offset + limit]
        return BeneficiaryAbsenceNodeType(nodes=beneficiary_absences, total_count=total_count)

    def resolve_beneficiary_absence(root, info, id):
        # We can easily optimize query count in the resolve method
        try:
            beneficiary_absence = BeneficiaryAbsence.objects.get(pk=id)
        except BeneficiaryAbsence.DoesNotExist:
            beneficiary_absence = None
        return beneficiary_absence

#************************************************************************

class CreateTransmissionEvent(graphene.Mutation):
    class Arguments:
        transmission_event_data = TransmissionEventInput(required=True)
        image = Upload(required=False)

    transmission_event = graphene.Field(TransmissionEventType)

    def mutate(root, info, image=None, transmission_event_data=None):
        creator = info.context.user
        beneficiary_ids = transmission_event_data.pop("beneficiaries")
        transmission_event = TransmissionEvent(**transmission_event_data)
        transmission_event.creator = creator
        transmission_event.company = creator.current_company if creator.current_company is not None else creator.company
        if info.context.FILES:
            # file1 = info.context.FILES['1']
            if image and isinstance(image, UploadedFile):
                image_file = transmission_event.image
                if not image_file:
                    image_file = File()
                    image_file.creator = creator
                image_file.image = image
                image_file.save()
                transmission_event.image = image_file
        transmission_event.save()
        if not transmission_event.employee:
            transmission_event.employee = creator.get_employee_in_company()
        folder = Folder.objects.create(name=str(transmission_event.id)+'_'+transmission_event.title,creator=creator)
        transmission_event.folder = folder
        beneficiaries = Beneficiary.objects.filter(id__in=beneficiary_ids)
        for beneficiary in beneficiaries:
            try:
                transmission_event_beneficiary = TransmissionEventBeneficiary.objects.get(beneficiary__id=beneficiary.id, transmission_event__id=transmission_event.id)
            except TransmissionEventBeneficiary.DoesNotExist:
                TransmissionEventBeneficiary.objects.create(
                        transmission_event=transmission_event,
                        beneficiary=beneficiary,
                        creator=creator
                    )
        transmission_event.save()
        return CreateTransmissionEvent(transmission_event=transmission_event)

class UpdateTransmissionEvent(graphene.Mutation):
    class Arguments:
        id = graphene.ID()
        transmission_event_data = TransmissionEventInput(required=True)
        image = Upload(required=False)

    transmission_event = graphene.Field(TransmissionEventType)

    def mutate(root, info, id, image=None, transmission_event_data=None):
        creator = info.context.user
        beneficiary_ids = transmission_event_data.pop("beneficiaries")
        TransmissionEvent.objects.filter(pk=id).update(**transmission_event_data)
        transmission_event = TransmissionEvent.objects.get(pk=id)
        if not transmission_event.folder or transmission_event.folder is None:
            folder = Folder.objects.create(name=str(transmission_event.id)+'_'+transmission_event.title,creator=creator)
            TransmissionEvent.objects.filter(pk=id).update(folder=folder)
        if not image and transmission_event.image:
            image_file = transmission_event.image
            image_file.delete()
        if info.context.FILES:
            # file1 = info.context.FILES['1']
            if image and isinstance(image, UploadedFile):
                image_file = transmission_event.image
                if not image_file:
                    image_file = File()
                    image_file.creator = creator
                image_file.image = image
                image_file.save()
                transmission_event.image = image_file
            transmission_event.save()
        if not transmission_event.employee:
            transmission_event.employee = creator.get_employee_in_company()
            transmission_event.save()
        TransmissionEventBeneficiary.objects.filter(transmission_event=transmission_event).exclude(beneficiary__id__in=beneficiary_ids).delete()
        beneficiaries = Beneficiary.objects.filter(id__in=beneficiary_ids)
        for beneficiary in beneficiaries:
            try:
                transmission_event_beneficiary = TransmissionEventBeneficiary.objects.get(beneficiary__id=beneficiary.id, transmission_event__id=transmission_event.id)
            except TransmissionEventBeneficiary.DoesNotExist:
                TransmissionEventBeneficiary.objects.create(
                        transmission_event=transmission_event,
                        beneficiary=beneficiary,
                        creator=creator
                    )
        return UpdateTransmissionEvent(transmission_event=transmission_event)

class UpdateTransmissionEventState(graphene.Mutation):
    class Arguments:
        id = graphene.ID()

    transmission_event = graphene.Field(TransmissionEventType)
    done = graphene.Boolean()
    success = graphene.Boolean()
    message = graphene.String()

    def mutate(root, info, id, transmission_event_fields=None):
        creator = info.context.user
        done = True
        success = True
        transmission_event = None
        message = ''
        try:
            transmission_event = TransmissionEvent.objects.get(pk=id)
            TransmissionEvent.objects.filter(pk=id).update(is_active=not transmission_event.is_active)
            transmission_event.refresh_from_db()
        except Exception as e:
            done = False
            success = False
            transmission_event=None
            message = "Une erreur s'est produite."
        return UpdateTransmissionEventState(done=done, success=success, message=message,transmission_event=transmission_event)


class DeleteTransmissionEvent(graphene.Mutation):
    class Arguments:
        id = graphene.ID()

    transmission_event = graphene.Field(TransmissionEventType)
    id = graphene.ID()
    deleted = graphene.Boolean()
    success = graphene.Boolean()
    message = graphene.String()

    def mutate(root, info, id):
        deleted = False
        success = False
        message = ''
        current_user = info.context.user
        transmission_event = TransmissionEvent.objects.get(pk=id)
        if current_user.can_manage_activity() or current_user.is_manager() or transmission_event.creator == current_user:
            # transmission_event = TransmissionEvent.objects.get(pk=id)
            # transmission_event.delete()
            TransmissionEvent.objects.filter(pk=id).update(is_deleted=True)
            deleted = True
            success = True
        else:
            message = "Impossible de supprimer : vous n'avez pas les droits nécessaires."
        return DeleteTransmissionEvent(deleted=deleted, success=success, message=message, id=id)

#************************************************************************

class CreateBeneficiaryAbsence(graphene.Mutation):
    class Arguments:
        beneficiary_absence_data = BeneficiaryAbsenceInput(required=True)

    beneficiary_absence = graphene.Field(BeneficiaryAbsenceType)

    def mutate(root, info, beneficiary_absence_data=None):
        creator = info.context.user
        beneficiary_ids = beneficiary_absence_data.pop("beneficiaries")
        reason_ids = beneficiary_absence_data.pop("reasons")
        beneficiary_absence = BeneficiaryAbsence(**beneficiary_absence_data)
        beneficiary_absence.creator = creator
        beneficiary_absence.company = creator.current_company if creator.current_company is not None else creator.company
        folder = Folder.objects.create(name=str(beneficiary_absence.id)+'_'+beneficiary_absence.title,creator=creator)
        beneficiary_absence.folder = folder
        beneficiary_absence.save()
        if not beneficiary_absence.employee:
            beneficiary_absence.employee = creator.get_employee_in_company()
        if reason_ids and reason_ids is not None:
            reasons = AbsenceReason.objects.filter(id__in=reason_ids)
            beneficiary_absence.reasons.set(reasons)
        beneficiaries = Beneficiary.objects.filter(id__in=beneficiary_ids)
        for beneficiary in beneficiaries:
            try:
                beneficiary_absence_items = BeneficiaryAbsenceItem.objects.get(beneficiary__id=beneficiary.id, beneficiary_absence__id=beneficiary_absence.id)
            except BeneficiaryAbsenceItem.DoesNotExist:
                BeneficiaryAbsenceItem.objects.create(
                        beneficiary_absence=beneficiary_absence,
                        beneficiary=beneficiary,
                        creator=creator
                    )
        beneficiary_absence.save()
        return CreateBeneficiaryAbsence(beneficiary_absence=beneficiary_absence)

class UpdateBeneficiaryAbsence(graphene.Mutation):
    class Arguments:
        id = graphene.ID()
        beneficiary_absence_data = BeneficiaryAbsenceInput(required=True)

    beneficiary_absence = graphene.Field(BeneficiaryAbsenceType)

    def mutate(root, info, id, image=None, beneficiary_absence_data=None):
        creator = info.context.user
        beneficiary_ids = beneficiary_absence_data.pop("beneficiaries")
        reason_ids = beneficiary_absence_data.pop("reasons")
        BeneficiaryAbsence.objects.filter(pk=id).update(**beneficiary_absence_data)
        beneficiary_absence = BeneficiaryAbsence.objects.get(pk=id)
        if not beneficiary_absence.folder or beneficiary_absence.folder is None:
            folder = Folder.objects.create(name=str(beneficiary_absence.id)+'_'+beneficiary_absence.title,creator=creator)
            BeneficiaryAbsence.objects.filter(pk=id).update(folder=folder)
        if not beneficiary_absence.employee:
            beneficiary_absence.employee = creator.get_employee_in_company()
            beneficiary_absence.save()

        if reason_ids and reason_ids is not None:
            reasons = AbsenceReason.objects.filter(id__in=reason_ids)
            beneficiary_absence.reasons.set(reasons)

        BeneficiaryAbsenceItem.objects.filter(beneficiary_absence=beneficiary_absence).exclude(beneficiary__id__in=beneficiary_ids).delete()
        beneficiaries = Beneficiary.objects.filter(id__in=beneficiary_ids)
        for beneficiary in beneficiaries:
            try:
                beneficiary_absence_items = BeneficiaryAbsenceItem.objects.get(beneficiary__id=beneficiary.id, beneficiary_absence__id=beneficiary_absence.id)
            except BeneficiaryAbsenceItem.DoesNotExist:
                BeneficiaryAbsenceItem.objects.create(
                        beneficiary_absence=beneficiary_absence,
                        beneficiary=beneficiary,
                        creator=creator
                    )
        return UpdateBeneficiaryAbsence(beneficiary_absence=beneficiary_absence)

class DeleteBeneficiaryAbsence(graphene.Mutation):
    class Arguments:
        id = graphene.ID()

    beneficiary_absence = graphene.Field(BeneficiaryAbsenceType)
    id = graphene.ID()
    deleted = graphene.Boolean()
    success = graphene.Boolean()
    message = graphene.String()

    def mutate(root, info, id):
        deleted = False
        success = False
        message = ''
        current_user = info.context.user
        beneficiary_absence = BeneficiaryAbsence.objects.get(pk=id)
        if current_user.can_manage_activity() or current_user.is_manager() or beneficiary_absence.creator == current_user:
            # beneficiary_absence = BeneficiaryAbsence.objects.get(pk=id)
            # beneficiary_absence.delete()
            BeneficiaryAbsence.objects.filter(pk=id).update(is_deleted=True)
            deleted = True
            success = True
        else:
            message = "Impossible de supprimer : vous n'avez pas les droits nécessaires."
        return DeleteBeneficiaryAbsence(deleted=deleted, success=success, message=message, id=id)
        
#*************************************************************************#
class ActivitiesMutation(graphene.ObjectType):
    create_transmission_event = CreateTransmissionEvent.Field()
    update_transmission_event = UpdateTransmissionEvent.Field()
    update_transmission_event_state = UpdateTransmissionEventState.Field()
    delete_transmission_event = DeleteTransmissionEvent.Field()

    create_beneficiary_absence = CreateBeneficiaryAbsence.Field()
    update_beneficiary_absence = UpdateBeneficiaryAbsence.Field()
    delete_beneficiary_absence = DeleteBeneficiaryAbsence.Field()