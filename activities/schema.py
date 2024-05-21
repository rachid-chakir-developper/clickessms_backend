import graphene
from graphene_django import DjangoObjectType
from django.core.files.uploadedfile import InMemoryUploadedFile, UploadedFile
from graphql_jwt.decorators import login_required
from graphene_file_upload.scalars import Upload

from django.db.models import Q

from activities.models import Event, EventBeneficiary, BeneficiaryAbsence, BeneficiaryAbsenceItem
from data_management.models import AbsenceReason
from medias.models import Folder, File
from human_ressources.models import Beneficiary

class EventBeneficiaryType(DjangoObjectType):
    class Meta:
        model = EventBeneficiary
        fields = "__all__"

class BeneficiaryAbsenceItemType(DjangoObjectType):
    class Meta:
        model = BeneficiaryAbsenceItem
        fields = "__all__"

class BeneficiaryAbsenceType(DjangoObjectType):
    class Meta:
        model = BeneficiaryAbsence
        fields = "__all__"
    beneficiaries = graphene.List(BeneficiaryAbsenceItemType)
    def resolve_beneficiaries( instance, info, **kwargs ):
        return instance.beneficiaryabsenceitem_set.all()

class BeneficiaryAbsenceNodeType(graphene.ObjectType):
    nodes = graphene.List(BeneficiaryAbsenceType)
    total_count = graphene.Int()

class BeneficiaryAbsenceFilterInput(graphene.InputObjectType):
    keyword = graphene.String(required=False)
    starting_date_time = graphene.DateTime(required=False)
    ending_date_time = graphene.DateTime(required=False)

class EventType(DjangoObjectType):
    class Meta:
        model = Event
        fields = "__all__"
    image = graphene.String()
    beneficiaries = graphene.List(EventBeneficiaryType)
    def resolve_image( instance, info, **kwargs ):
        return instance.image and info.context.build_absolute_uri(instance.image.image.url)
    def resolve_beneficiaries( instance, info, **kwargs ):
        return instance.eventbeneficiary_set.all()

class EventNodeType(graphene.ObjectType):
    nodes = graphene.List(EventType)
    total_count = graphene.Int()

class EventFilterInput(graphene.InputObjectType):
    keyword = graphene.String(required=False)
    starting_date_time = graphene.DateTime(required=False)
    ending_date_time = graphene.DateTime(required=False)

class EventInput(graphene.InputObjectType):
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
    events = graphene.Field(EventNodeType, event_filter= EventFilterInput(required=False), offset = graphene.Int(required=False), limit = graphene.Int(required=False), page = graphene.Int(required=False))
    event = graphene.Field(EventType, id = graphene.ID())
    beneficiary_absences = graphene.Field(BeneficiaryAbsenceNodeType, beneficiary_absence_filter= BeneficiaryAbsenceFilterInput(required=False), offset = graphene.Int(required=False), limit = graphene.Int(required=False), page = graphene.Int(required=False))
    beneficiary_absence = graphene.Field(BeneficiaryAbsenceType, id = graphene.ID())
    def resolve_events(root, info, event_filter=None, offset=None, limit=None, page=None):
        # We can easily optimize query count in the resolve method
        user = info.context.user
        company = user.current_company if user.current_company is not None else user.company
        total_count = 0
        events = Event.objects.filter(company=company)
        if event_filter:
            keyword = event_filter.get('keyword', '')
            starting_date_time = event_filter.get('starting_date_time')
            ending_date_time = event_filter.get('ending_date_time')
            if keyword:
                events = events.filter(Q(title__icontains=keyword))
            if starting_date_time:
                events = events.filter(starting_date_time__gte=starting_date_time)
            if ending_date_time:
                events = events.filter(starting_date_time__lte=ending_date_time)
        events = events.order_by('-created_at')
        total_count = events.count()
        if page:
            offset = limit * (page - 1)
        if offset is not None and limit is not None:
            events = events[offset:offset + limit]
        return EventNodeType(nodes=events, total_count=total_count)

    def resolve_event(root, info, id):
        # We can easily optimize query count in the resolve method
        try:
            event = Event.objects.get(pk=id)
        except Event.DoesNotExist:
            event = None
        return event

    def resolve_beneficiary_absences(root, info, beneficiary_absence_filter=None, offset=None, limit=None, page=None):
        # We can easily optimize query count in the resolve method
        user = info.context.user
        company = user.current_company if user.current_company is not None else user.company
        total_count = 0
        beneficiary_absences = BeneficiaryAbsence.objects.filter(company=company)
        if beneficiary_absence_filter:
            keyword = beneficiary_absence_filter.get('keyword', '')
            starting_date_time = beneficiary_absence_filter.get('starting_date_time')
            ending_date_time = beneficiary_absence_filter.get('ending_date_time')
            if keyword:
                beneficiary_absences = beneficiary_absences.filter(Q(title__icontains=keyword))
            if starting_date_time:
                beneficiary_absences = beneficiary_absences.filter(starting_date_time__gte=starting_date_time)
            if ending_date_time:
                beneficiary_absences = beneficiary_absences.filter(starting_date_time__lte=ending_date_time)
        beneficiary_absences = beneficiary_absences.order_by('-created_at')
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

class CreateEvent(graphene.Mutation):
    class Arguments:
        event_data = EventInput(required=True)
        image = Upload(required=False)

    event = graphene.Field(EventType)

    def mutate(root, info, image=None, event_data=None):
        creator = info.context.user
        beneficiary_ids = event_data.pop("beneficiaries")
        event = Event(**event_data)
        event.creator = creator
        event.company = creator.current_company if creator.current_company is not None else creator.company
        if info.context.FILES:
            # file1 = info.context.FILES['1']
            if image and isinstance(image, UploadedFile):
                image_file = event.image
                if not image_file:
                    image_file = File()
                    image_file.creator = creator
                image_file.image = image
                image_file.save()
                event.image = image_file
        event.save()
        if not event.employee:
            event.employee = creator.getEmployeeInCompany()
        folder = Folder.objects.create(name=str(event.id)+'_'+event.title,creator=creator)
        event.folder = folder
        beneficiaries = Beneficiary.objects.filter(id__in=beneficiary_ids)
        for beneficiary in beneficiaries:
            try:
                event_beneficiary = EventBeneficiary.objects.get(beneficiary__id=beneficiary.id, event__id=event.id)
            except EventBeneficiary.DoesNotExist:
                EventBeneficiary.objects.create(
                        event=event,
                        beneficiary=beneficiary,
                        creator=creator
                    )
        event.save()
        return CreateEvent(event=event)

class UpdateEvent(graphene.Mutation):
    class Arguments:
        id = graphene.ID()
        event_data = EventInput(required=True)
        image = Upload(required=False)

    event = graphene.Field(EventType)

    def mutate(root, info, id, image=None, event_data=None):
        creator = info.context.user
        beneficiary_ids = event_data.pop("beneficiaries")
        Event.objects.filter(pk=id).update(**event_data)
        event = Event.objects.get(pk=id)
        if not event.folder or event.folder is None:
            folder = Folder.objects.create(name=str(event.id)+'_'+event.title,creator=creator)
            Event.objects.filter(pk=id).update(folder=folder)
        if not image and event.image:
            image_file = event.image
            image_file.delete()
        if info.context.FILES:
            # file1 = info.context.FILES['1']
            if image and isinstance(image, UploadedFile):
                image_file = event.image
                if not image_file:
                    image_file = File()
                    image_file.creator = creator
                image_file.image = image
                image_file.save()
                event.image = image_file
            event.save()
        if not event.employee:
            event.employee = creator.getEmployeeInCompany()
            event.save()
        EventBeneficiary.objects.filter(event=event).exclude(beneficiary__id__in=beneficiary_ids).delete()
        beneficiaries = Beneficiary.objects.filter(id__in=beneficiary_ids)
        for beneficiary in beneficiaries:
            try:
                event_beneficiary = EventBeneficiary.objects.get(beneficiary__id=beneficiary.id, event__id=event.id)
            except EventBeneficiary.DoesNotExist:
                EventBeneficiary.objects.create(
                        event=event,
                        beneficiary=beneficiary,
                        creator=creator
                    )
        return UpdateEvent(event=event)

class UpdateEventState(graphene.Mutation):
    class Arguments:
        id = graphene.ID()

    event = graphene.Field(EventType)
    done = graphene.Boolean()
    success = graphene.Boolean()
    message = graphene.String()

    def mutate(root, info, id, event_fields=None):
        creator = info.context.user
        done = True
        success = True
        event = None
        message = ''
        try:
            event = Event.objects.get(pk=id)
            Event.objects.filter(pk=id).update(is_active=not event.is_active)
            event.refresh_from_db()
        except Exception as e:
            done = False
            success = False
            event=None
            message = "Une erreur s'est produite."
        return UpdateEventState(done=done, success=success, message=message,event=event)


class DeleteEvent(graphene.Mutation):
    class Arguments:
        id = graphene.ID()

    event = graphene.Field(EventType)
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
            event = Event.objects.get(pk=id)
            event.delete()
            deleted = True
            success = True
        else:
            message = "Vous n'êtes pas un Superuser."
        return DeleteEvent(deleted=deleted, success=success, message=message, id=id)

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
            beneficiary_absence.employee = creator.getEmployeeInCompany()
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
            beneficiary_absence.employee = creator.getEmployeeInCompany()
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
        if current_user.is_superuser:
            beneficiary_absence = BeneficiaryAbsence.objects.get(pk=id)
            beneficiary_absence.delete()
            deleted = True
            success = True
        else:
            message = "Vous n'êtes pas un Superuser."
        return DeleteBeneficiaryAbsence(deleted=deleted, success=success, message=message, id=id)
        
#*************************************************************************#
class ActivitiesMutation(graphene.ObjectType):
    create_event = CreateEvent.Field()
    update_event = UpdateEvent.Field()
    update_event_state = UpdateEventState.Field()
    delete_event = DeleteEvent.Field()

    create_beneficiary_absence = CreateBeneficiaryAbsence.Field()
    update_beneficiary_absence = UpdateBeneficiaryAbsence.Field()
    delete_beneficiary_absence = DeleteBeneficiaryAbsence.Field()