import graphene
import channels_graphql_ws
from graphene_django import DjangoObjectType
from django.core.files.uploadedfile import InMemoryUploadedFile, UploadedFile
from graphql_jwt.decorators import login_required
from graphene_file_upload.scalars import Upload
from django.core.exceptions import PermissionDenied
from graphql import GraphQLError

from django.db.models import Q
from django.db import transaction

from qualities.models import UndesirableEvent, UndesirableEventEstablishment, UndesirableEventEmployee, UndesirableEventBeneficiary, UndesirableEventNotifiedPerson, BoxIdea
from qualities.broadcaster import broadcastUndesirableEventAdded, broadcastUndesirableEventUpdated, broadcastUndesirableEventDeleted
from works.broadcaster import broadcastTicketAdded

from medias.models import Folder, File
from medias.schema import MediaInput

from companies.models import Establishment
from human_ressources.models import Employee, Beneficiary

from works.models import Ticket
from works.schema import TicketType
from accounts.models import User

from notifications.notificator import notify_undesirable_event


class UndesirableEventEmployeeType(DjangoObjectType):
    class Meta:
        model = UndesirableEventEmployee
        fields = "__all__"

class UndesirableEventEstablishmentType(DjangoObjectType):
    class Meta:
        model = UndesirableEventEstablishment
        fields = "__all__"

class UndesirableEventBeneficiaryType(DjangoObjectType):
    class Meta:
        model = UndesirableEventBeneficiary
        fields = "__all__"

class UndesirableEventNotifiedPersonType(DjangoObjectType):
    class Meta:
        model = UndesirableEventNotifiedPerson
        fields = "__all__"

class UndesirableEventType(DjangoObjectType):
    class Meta:
        model = UndesirableEvent
        fields = "__all__"
    image = graphene.String()
    completion_percentage = graphene.Float()
    ticket = graphene.Field(TicketType)
    def resolve_image( instance, info, **kwargs ):
        return instance.image and info.context.build_absolute_uri(instance.image.image.url)
    def resolve_completion_percentage(instance, info, **kwargs):
        return instance.completion_percentage
    def resolve_ticket(instance, info, **kwargs):
        return instance.tickets.first()

class UndesirableEventNodeType(graphene.ObjectType):
    nodes = graphene.List(UndesirableEventType)
    total_count = graphene.Int()

class UndesirableEventFilterInput(graphene.InputObjectType):
    keyword = graphene.String(required=False)
    starting_date_time = graphene.DateTime(required=False)
    ending_date_time = graphene.DateTime(required=False)
    beneficiaries = graphene.List(graphene.Int, required=False)
    establishments = graphene.List(graphene.Int, required=False)
    employees = graphene.List(graphene.Int, required=False)
    list_type = graphene.String(required=False)
    order_by = graphene.String(required=False)

class UndesirableEventInput(graphene.InputObjectType):
    id = graphene.ID(required=False)
    number = graphene.String(required=False)
    title = graphene.String(required=False)
    undesirable_event_type = graphene.String(required=False)
    severity = graphene.String(required=False)
    starting_date_time = graphene.DateTime(required=False)
    ending_date_time = graphene.DateTime(required=False)
    actions_taken_text = graphene.String(required=False)
    course_facts_date_time = graphene.DateTime(required=False)
    course_facts_place = graphene.String(required=False)
    circumstance_event_text = graphene.String(required=False)
    description = graphene.String(required=False)
    observation = graphene.String(required=False)
    is_active = graphene.Boolean(required=False)
    other_notified_persons = graphene.String(required=False)
    concerned_families = graphene.String(required=False)
    status = graphene.String(required=False)
    other_types = graphene.String(required=False)
    normal_types = graphene.List(graphene.Int, required=False)
    serious_types = graphene.List(graphene.Int, required=False)
    frequency_id = graphene.Int(name="frequency", required=False)
    employee_id = graphene.Int(name="employee", required=False)
    declarants = graphene.List(graphene.Int, required=False)
    establishments = graphene.List(graphene.Int, required=False)
    employees = graphene.List(graphene.Int, required=False)
    beneficiaries = graphene.List(graphene.Int, required=False)
    notified_persons = graphene.List(graphene.Int, required=False)

class BoxIdeaType(DjangoObjectType):
    class Meta:
        model = BoxIdea
        fields = "__all__"

class BoxIdeaNodeType(graphene.ObjectType):
    nodes = graphene.List(BoxIdeaType)
    total_count = graphene.Int()

class BoxIdeaFilterInput(graphene.InputObjectType):
    keyword = graphene.String(required=False)
    starting_date_time = graphene.DateTime(required=False)
    ending_date_time = graphene.DateTime(required=False)

class BoxIdeaInput(graphene.InputObjectType):
    id = graphene.ID(required=False)
    number = graphene.String(required=False)
    title = graphene.String(required=True)
    link = graphene.String(required=True)
    description = graphene.String(required=False)
    observation = graphene.String(required=False)
    is_active = graphene.Boolean(required=False)

class QualitiesQuery(graphene.ObjectType):
    undesirable_events = graphene.Field(UndesirableEventNodeType, undesirable_event_filter= UndesirableEventFilterInput(required=False), offset = graphene.Int(required=False), limit = graphene.Int(required=False), page = graphene.Int(required=False))
    undesirable_event = graphene.Field(UndesirableEventType, id = graphene.ID())
    box_ideas = graphene.Field(BoxIdeaNodeType, box_idea_filter= BoxIdeaFilterInput(required=False), offset = graphene.Int(required=False), limit = graphene.Int(required=False), page = graphene.Int(required=False))
    box_idea = graphene.Field(BoxIdeaType, id = graphene.ID())
    def resolve_undesirable_events(root, info, undesirable_event_filter=None, offset=None, limit=None, page=None):
        # We can easily optimize query count in the resolve method
        user = info.context.user
        company = user.the_current_company
        employee = user.get_employee_in_company()
        total_count = 0
        undesirable_events = UndesirableEvent.objects.filter(company=company, is_deleted=False)
        if not user.can_manage_quality():
            if user.is_manager():
                undesirable_events = undesirable_events.filter(Q(establishments__establishment__managers__employee=employee) | Q(creator=user)).exclude(Q(status='DRAFT') & ~Q(creator=user))
            else:
                if employee:
                    employee_current_estabs = []
                    if employee.current_contract:
                        employee_current_estabs = employee.current_contract.establishments.values_list('establishment', flat=True)
                    undesirable_events = undesirable_events.filter(
                        Q(establishments__establishment__in=employee.establishments.all()) |
                        Q(establishments__establishment__in=employee_current_estabs) |
                        Q(employee=employee) |
                        Q(creator=user)
                        ).exclude(Q(status='DRAFT') & ~Q(creator=user))
        else:
            undesirable_events = undesirable_events.exclude(Q(status='DRAFT') & ~Q(creator=user))
        the_order_by = '-created_at'
        if undesirable_event_filter:
            keyword = undesirable_event_filter.get('keyword', '')
            starting_date_time = undesirable_event_filter.get('starting_date_time')
            ending_date_time = undesirable_event_filter.get('ending_date_time')
            beneficiaries = undesirable_event_filter.get('beneficiaries')
            establishments = undesirable_event_filter.get('establishments')
            employees = undesirable_event_filter.get('employees')
            list_type = undesirable_event_filter.get('list_type') # ALL_EI_REQUESTS / MY_EIS / MY_EI_REQUESTS / ALL
            order_by = undesirable_event_filter.get('order_by')
            if beneficiaries:
                undesirable_events = undesirable_events.filter(beneficiaries__beneficiary__id__in=beneficiaries)
            if establishments:
                undesirable_events = undesirable_events.filter(establishments__establishment__id__in=establishments)
            if employees:
                undesirable_events = undesirable_events.filter(employees__employee__id__in=employees)
            if list_type:
                if list_type == 'MY_EIS':
                    undesirable_events = undesirable_events.filter(Q(employee=employee) | Q(creator=user))
                elif list_type == 'ALL':
                    pass
            if keyword:
                undesirable_events = undesirable_events.filter(Q(title__icontains=keyword))
            if starting_date_time:
                undesirable_events = undesirable_events.filter(starting_date_time__date__gte=starting_date_time.date())
            if ending_date_time:
                undesirable_events = undesirable_events.filter(starting_date_time__date__lte=ending_date_time.date())
            if order_by:
                the_order_by = order_by
        undesirable_events = undesirable_events.order_by(the_order_by).distinct()
        total_count = undesirable_events.count()
        if page:
            offset = limit * (page - 1)
        if offset is not None and limit is not None:
            undesirable_events = undesirable_events[offset:offset + limit]
        return UndesirableEventNodeType(nodes=undesirable_events, total_count=total_count)

    def resolve_undesirable_event(root, info, id):
        # We can easily optimize query count in the resolve method
        user = info.context.user
        company = user.the_current_company
        try:
            undesirable_event = UndesirableEvent.objects.get(pk=id, company=company)
        except UndesirableEvent.DoesNotExist:
            undesirable_event = None
        return undesirable_event

    def resolve_box_ideas(root, info, box_idea_filter=None, offset=None, limit=None, page=None):
        # We can easily optimize query count in the resolve method
        user = info.context.user
        company = user.the_current_company
        total_count = 0
        box_ideas = BoxIdea.objects.filter(company=company, is_deleted=False)
        if box_idea_filter:
            keyword = box_idea_filter.get('keyword', '')
            starting_date_time = box_idea_filter.get('starting_date_time')
            ending_date_time = box_idea_filter.get('ending_date_time')
            if keyword:
                box_ideas = box_ideas.filter(Q(name__icontains=keyword) | Q(designation__icontains=keyword) | Q(bar_code__icontains=keyword))
            if starting_date_time:
                box_ideas = box_ideas.filter(created_at__gte=starting_date_time)
            if ending_date_time:
                box_ideas = box_ideas.filter(created_at__lte=ending_date_time)
        box_ideas = box_ideas.order_by('-created_at')
        total_count = box_ideas.count()
        if page:
            offset = limit * (page - 1)
        if offset is not None and limit is not None:
            box_ideas = box_ideas[offset:offset + limit]
        return BoxIdeaNodeType(nodes=box_ideas, total_count=total_count)

    def resolve_box_idea(root, info, id):
        # We can easily optimize query count in the resolve method
        user = info.context.user
        company = user.the_current_company
        try:
            box_idea = BoxIdea.objects.get(pk=id, company=company)
        except BoxIdea.DoesNotExist:
            box_idea = None
        return box_idea

#************************************************************************

class CreateUndesirableEvent(graphene.Mutation):
    class Arguments:
        undesirable_event_data = UndesirableEventInput(required=True)
        image = Upload(required=False)
        files = graphene.List(MediaInput, required=False)

    undesirable_event = graphene.Field(UndesirableEventType)

    def mutate(root, info, image=None, files=None, undesirable_event_data=None):
        creator = info.context.user
        declarant_ids = undesirable_event_data.pop("declarants")
        establishment_ids = undesirable_event_data.pop("establishments")
        beneficiary_ids = undesirable_event_data.pop("beneficiaries")
        employee_ids = undesirable_event_data.pop("employees")
        notified_person_ids = undesirable_event_data.pop("notified_persons")
        normal_type_ids = undesirable_event_data.pop("normal_types")
        serious_type_ids = undesirable_event_data.pop("serious_types")
        undesirable_event = UndesirableEvent(**undesirable_event_data)
        undesirable_event.creator = creator
        undesirable_event.company = creator.the_current_company
        if info.context.FILES:
            # file1 = info.context.FILES['1']
            if image and isinstance(image, UploadedFile):
                image_file = undesirable_event.image
                if not image_file:
                    image_file = File()
                    image_file.creator = creator
                image_file.image = image
                image_file.save()
                undesirable_event.image = image_file
        undesirable_event.save()
        if not undesirable_event.employee:
            undesirable_event.employee = creator.get_employee_in_company()
        if declarant_ids and declarant_ids is not None:
            undesirable_event.declarants.set(declarant_ids)
        folder = Folder.objects.create(name=str(undesirable_event.id)+'_'+undesirable_event.title,creator=creator)
        undesirable_event.folder = folder
        if not files:
            files = []
        for file_media in files:
            file = file_media.file
            caption = file_media.caption
            if id in file_media  or 'id' in file_media:
                file_file = File.objects.get(pk=file_media.id)
            else:
                file_file = File()
                file_file.creator = creator
                file_file.folder = folder
            if info.context.FILES and file and isinstance(file, UploadedFile):
                file_file.file = file
            file_file.caption = caption
            file_file.save()
            undesirable_event.files.add(file_file)
        if normal_type_ids and normal_type_ids is not None:
            undesirable_event.normal_types.set(normal_type_ids)

        if serious_type_ids and serious_type_ids is not None:
            undesirable_event.serious_types.set(serious_type_ids)

        establishments = Establishment.objects.filter(id__in=establishment_ids)
        for establishment in establishments:
            try:
                undesirable_event_establishment = UndesirableEventEstablishment.objects.get(establishment__id=establishment.id, undesirable_event__id=undesirable_event.id)
            except UndesirableEventEstablishment.DoesNotExist:
                UndesirableEventEstablishment.objects.create(
                        undesirable_event=undesirable_event,
                        establishment=establishment,
                        creator=creator
                    )

        employees = Employee.objects.filter(id__in=employee_ids)
        for employee in employees:
            try:
                undesirable_event_employee = UndesirableEventEmployee.objects.get(employee__id=employee.id, undesirable_event__id=undesirable_event.id)
            except UndesirableEventEmployee.DoesNotExist:
                UndesirableEventEmployee.objects.create(
                        undesirable_event=undesirable_event,
                        employee=employee,
                        creator=creator
                    )
        beneficiaries = Beneficiary.objects.filter(id__in=beneficiary_ids)
        for beneficiary in beneficiaries:
            try:
                undesirable_event_beneficiary = UndesirableEventBeneficiary.objects.get(beneficiary__id=beneficiary.id, undesirable_event__id=undesirable_event.id)
            except UndesirableEventBeneficiary.DoesNotExist:
                UndesirableEventBeneficiary.objects.create(
                        undesirable_event=undesirable_event,
                        beneficiary=beneficiary,
                        creator=creator
                    )
        notified_persons = Employee.objects.filter(id__in=notified_person_ids)
        for notified_person in notified_persons:
            try:
                undesirable_event_notified_person = UndesirableEventNotifiedPerson.objects.get(employee__id=notified_person.id, undesirable_event__id=undesirable_event.id)
            except UndesirableEventNotifiedPerson.DoesNotExist:
                UndesirableEventNotifiedPerson.objects.create(
                        undesirable_event=undesirable_event,
                        employee=notified_person,
                        creator=creator
                    )
        undesirable_event.save()
        broadcastUndesirableEventAdded(undesirable_event=undesirable_event)
        return CreateUndesirableEvent(undesirable_event=undesirable_event)

class UpdateUndesirableEvent(graphene.Mutation):
    class Arguments:
        id = graphene.ID()
        undesirable_event_data = UndesirableEventInput(required=True)
        image = Upload(required=False)
        files = graphene.List(MediaInput, required=False)

    undesirable_event = graphene.Field(UndesirableEventType)

    def mutate(root, info, id, image=None, files=None, undesirable_event_data=None):
        creator = info.context.user
        try:
            undesirable_event = UndesirableEvent.objects.get(pk=id, company=creator.the_current_company)
        except UndesirableEvent.DoesNotExist:
            raise e
        if not creator.can_manage_quality() and not creator.is_manager() and undesirable_event.employee!=creator.get_employee_in_company() and undesirable_event.creator!=creator:
            raise PermissionDenied("Impossible de modifier : vous n'avez pas les droits nécessaires.")
        declarant_ids = undesirable_event_data.pop("declarants")
        establishment_ids = undesirable_event_data.pop("establishments")
        beneficiary_ids = undesirable_event_data.pop("beneficiaries")
        employee_ids = undesirable_event_data.pop("employees")
        notified_person_ids = undesirable_event_data.pop("notified_persons")
        normal_type_ids = undesirable_event_data.pop("normal_types")
        serious_type_ids = undesirable_event_data.pop("serious_types")
        is_draft = True if undesirable_event.status == 'DRAFT' else False
        UndesirableEvent.objects.filter(pk=id).update(**undesirable_event_data)
        if declarant_ids and declarant_ids is not None:
            undesirable_event.declarants.set(declarant_ids)
        undesirable_event.refresh_from_db()
        if not undesirable_event.folder or undesirable_event.folder is None:
            folder = Folder.objects.create(name=str(undesirable_event.id)+'_'+undesirable_event.title,creator=creator)
            UndesirableEvent.objects.filter(pk=id).update(folder=folder)
        if not image and undesirable_event.image:
            image_file = undesirable_event.image
            image_file.delete()
        if info.context.FILES:
            # file1 = info.context.FILES['1']
            if image and isinstance(image, UploadedFile):
                image_file = undesirable_event.image
                if not image_file:
                    image_file = File()
                    image_file.creator = creator
                image_file.image = image
                image_file.save()
                undesirable_event.image = image_file
            undesirable_event.save()
        if not files:
            files = []
        else:
            file_ids = [item.id for item in files if item.id is not None]
            File.objects.filter(file_undesirable_events=undesirable_event).exclude(id__in=file_ids).delete()
        for file_media in files:
            file = file_media.file
            caption = file_media.caption
            if id in file_media  or 'id' in file_media:
                file_file = File.objects.get(pk=file_media.id)
            else:
                file_file = File()
                file_file.creator = creator
                file_file.folder = undesirable_event.folder
            if info.context.FILES and file and isinstance(file, UploadedFile):
                file_file.file = file
            file_file.caption = caption
            file_file.save()
            undesirable_event.files.add(file_file)
        if not undesirable_event.employee:
            undesirable_event.employee = creator.get_employee_in_company()
            undesirable_event.save()

        if normal_type_ids and normal_type_ids is not None:
            undesirable_event.normal_types.set(normal_type_ids)

        if serious_type_ids and serious_type_ids is not None:
            undesirable_event.serious_types.set(serious_type_ids)

        UndesirableEventEstablishment.objects.filter(undesirable_event=undesirable_event).exclude(establishment__id__in=establishment_ids).delete()
        establishments = Establishment.objects.filter(id__in=establishment_ids)
        for establishment in establishments:
            try:
                undesirable_event_establishment = UndesirableEventEstablishment.objects.get(establishment__id=establishment.id, undesirable_event__id=undesirable_event.id)
            except UndesirableEventEstablishment.DoesNotExist:
                UndesirableEventEstablishment.objects.create(
                        undesirable_event=undesirable_event,
                        establishment=establishment,
                        creator=creator
                    )

        if is_draft and undesirable_event.frequency:
            UndesirableEvent.objects.filter(pk=id).update(status='NEW')
            undesirable_event.refresh_from_db()
            undesirable_event_establishments = undesirable_event.establishments.all()
            for undesirable_event_establishment in undesirable_event_establishments:
                managers = undesirable_event_establishment.establishment.managers.all()
                for manager in managers:
                    employee_user = manager.employee.user
                    if employee_user:
                        notify_undesirable_event(sender=creator, recipient=employee_user, undesirable_event=undesirable_event, action='ADDED')
            quality_managers = User.get_quality_managers_in_user_company(user=creator)
            for quality_manager in quality_managers:
                notify_undesirable_event(sender=creator, recipient=quality_manager, undesirable_event=undesirable_event, action='ADDED')

        UndesirableEventEmployee.objects.filter(undesirable_event=undesirable_event).exclude(employee__id__in=employee_ids).delete()
        employees = Employee.objects.filter(id__in=employee_ids)
        for employee in employees:
            try:
                undesirable_event_employee = UndesirableEventEmployee.objects.get(employee__id=employee.id, undesirable_event__id=undesirable_event.id)
            except UndesirableEventEmployee.DoesNotExist:
                UndesirableEventEmployee.objects.create(
                        undesirable_event=undesirable_event,
                        employee=employee,
                        creator=creator
                    )
        UndesirableEventBeneficiary.objects.filter(undesirable_event=undesirable_event).exclude(beneficiary__id__in=beneficiary_ids).delete()
        beneficiaries = Beneficiary.objects.filter(id__in=beneficiary_ids)
        for beneficiary in beneficiaries:
            try:
                undesirable_event_beneficiary = UndesirableEventBeneficiary.objects.get(beneficiary__id=beneficiary.id, undesirable_event__id=undesirable_event.id)
            except UndesirableEventBeneficiary.DoesNotExist:
                UndesirableEventBeneficiary.objects.create(
                        undesirable_event=undesirable_event,
                        beneficiary=beneficiary,
                        creator=creator
                    )

        UndesirableEventNotifiedPerson.objects.filter(undesirable_event=undesirable_event).exclude(employee__id__in=notified_person_ids).delete()
        notified_persons = Employee.objects.filter(id__in=notified_person_ids)
        for notified_person in notified_persons:
            try:
                undesirable_event_notified_person = UndesirableEventNotifiedPerson.objects.get(employee__id=notified_person.id, undesirable_event__id=undesirable_event.id)
            except UndesirableEventNotifiedPerson.DoesNotExist:
                UndesirableEventNotifiedPerson.objects.create(
                        undesirable_event=undesirable_event,
                        employee=notified_person,
                        creator=creator
                    )
        broadcastUndesirableEventUpdated(undesirable_event=undesirable_event)
        return UpdateUndesirableEvent(undesirable_event=undesirable_event)

class UpdateUndesirableEventFields(graphene.Mutation):
    class Arguments:
        id = graphene.ID()
        undesirable_event_data = UndesirableEventInput(required=True)

    undesirable_event = graphene.Field(UndesirableEventType)
    done = graphene.Boolean()
    success = graphene.Boolean()
    message = graphene.String()

    def mutate(root, info, id, undesirable_event_data=None):
        creator = info.context.user
        try:
            undesirable_event = UndesirableEvent.objects.get(pk=id, company=creator.the_current_company)
        except UndesirableEvent.DoesNotExist:
            raise e
        done = True
        success = True
        message = ''
        try:
            UndesirableEvent.objects.filter(pk=id).update(**undesirable_event_data)
            undesirable_event.refresh_from_db()
            if 'status' in undesirable_event_data and (creator.can_manage_quality() or creator.is_manager()):
                employee_user = undesirable_event.employee.user if undesirable_event.employee else undesirable_event.creator
                if employee_user:
                    notify_undesirable_event(sender=creator, recipient=employee_user, undesirable_event=undesirable_event)
            undesirable_event.refresh_from_db()
            broadcastUndesirableEventUpdated(undesirable_event=undesirable_event)
        except Exception as e:
            done = False
            success = False
            undesirable_event=None
            message = "Une erreur s'est produite."
        return UpdateUndesirableEventFields(done=done, success=success, message=message, undesirable_event=undesirable_event)



class UpdateUndesirableEventState(graphene.Mutation):
    class Arguments:
        id = graphene.ID()

    undesirable_event = graphene.Field(UndesirableEventType)
    done = graphene.Boolean()
    success = graphene.Boolean()
    message = graphene.String()

    def mutate(root, info, id, undesirable_event_fields=None):
        creator = info.context.user
        try:
            undesirable_event = UndesirableEvent.objects.get(pk=id, company=creator.the_current_company)
        except UndesirableEvent.DoesNotExist:
            raise e
        done = True
        success = True
        message = ''
        try:
            UndesirableEvent.objects.filter(pk=id).update(is_active=not undesirable_event.is_active)
            undesirable_event.refresh_from_db()
            broadcastUndesirableEventUpdated(undesirable_event=undesirable_event)
        except Exception as e:
            done = False
            success = False
            undesirable_event=None
            message = "Une erreur s'est produite."
        return UpdateUndesirableEventState(done=done, success=success, message=message, undesirable_event=undesirable_event)


class CreateUndesirableEventTicket(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)

    undesirable_event = graphene.Field(UndesirableEventType)
    done = graphene.Boolean()
    success = graphene.Boolean()
    message = graphene.String()

    def mutate(root, info, id):
        creator = info.context.user
        try:
            undesirable_event = UndesirableEvent.objects.get(pk=id, company=creator.the_current_company)
        except UndesirableEvent.DoesNotExist:
            raise e
        success = True
        message = ''
        ticket = None
        if not creator.can_manage_quality() and not creator.is_manager():
            raise PermissionDenied("Impossible d'analyser : vous n'avez pas les droits nécessaires.")
        try:
            undesirable_event.refresh_from_db()
            if undesirable_event.status == 'DRAFT':
                raise GraphQLError("Impossible d'analyser un événement indésirable en brouillon.")
            if Ticket.objects.filter(undesirable_event=undesirable_event).exists():
                ticket = Ticket.objects.filter(undesirable_event=undesirable_event).first()
                message = "Un ticket pour cet événement indésirable existe déjà."
            else:
                with transaction.atomic():
                    ticket = Ticket.objects.create(
                        title=f'{undesirable_event.title}',
                        ticket_type="PLAN_ACTION",
                        description='',
                        employee=creator.get_employee_in_company(),
                        undesirable_event=undesirable_event,
                        is_have_efc_report=True if undesirable_event.undesirable_event_type == 'SERIOUS' else False,
                        company=creator.the_current_company,
                        creator=creator,
                    )
                    establishments = UndesirableEventEstablishment.objects.filter(undesirable_event=undesirable_event)
                    for ue_establishment in establishments:
                        if ue_establishment.establishment:
                            ticket.establishments.add(ue_establishment.establishment)
                    UndesirableEvent.objects.filter(pk=id).update(status='IN_PROGRESS')
                    ticket.refresh_from_db()
                    broadcastTicketAdded(ticket=ticket)
                    undesirable_event.refresh_from_db()
                    broadcastUndesirableEventUpdated(undesirable_event=undesirable_event)
                    message = 'Ticket créé avec succès avec les établissements associés.'
            employee_user = undesirable_event.employee.user if undesirable_event.employee else undesirable_event.creator
            if employee_user:
                notify_undesirable_event(sender=creator, recipient=employee_user, undesirable_event=undesirable_event)

        except UndesirableEvent.DoesNotExist:
            success = False
            message = "Événement indésirable non trouvé."

        except Exception as e:
            success = False
            message = f"Une erreur s'est produite: {str(e)}"

        return CreateUndesirableEventTicket(
            undesirable_event=undesirable_event if success else None,
            done=success,
            success=success,
            message=message
        )


class DeleteUndesirableEvent(graphene.Mutation):
    class Arguments:
        id = graphene.ID()

    undesirable_event = graphene.Field(UndesirableEventType)
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
            undesirable_event = UndesirableEvent.objects.get(pk=id, company=current_user.the_current_company)
        except UndesirableEvent.DoesNotExist:
            raise e
        if current_user.can_manage_quality() or current_user.is_manager() or (undesirable_event.creator == current_user and not undesirable_event.tickets.first()):
            # undesirable_event = UndesirableEvent.objects.get(pk=id)
            # undesirable_event.delete()
            UndesirableEvent.objects.filter(pk=id).update(is_deleted=True)
            deleted = True
            success = True
            broadcastUndesirableEventDeleted(undesirable_event=undesirable_event)
        else:
            deleted = False
            success = False
            message = "Impossible de supprimer : vous n'avez pas les droits nécessaires."
        return DeleteUndesirableEvent(deleted=deleted, success=success, message=message, id=id)
#****************************************************************************************
#************************************************************************

class CreateBoxIdea(graphene.Mutation):
    class Arguments:
        box_idea_data = BoxIdeaInput(required=True)

    box_idea = graphene.Field(BoxIdeaType)

    def mutate(root, info, box_idea_data=None):
        creator = info.context.user
        box_idea = BoxIdea(**box_idea_data)
        box_idea.creator = creator
        box_idea.company = creator.the_current_company
        if not box_idea.employee:
            box_idea.employee = creator.get_employee_in_company()
        box_idea.save()
        return CreateBoxIdea(box_idea=box_idea)

class UpdateBoxIdea(graphene.Mutation):
    class Arguments:
        id = graphene.ID()
        box_idea_data = BoxIdeaInput(required=True)

    box_idea = graphene.Field(BoxIdeaType)

    def mutate(root, info, id, box_idea_data=None):
        creator = info.context.user
        try:
            box_idea = BoxIdea.objects.get(pk=id, company=creator.the_current_company)
        except BoxIdea.DoesNotExist:
            raise e
        BoxIdea.objects.filter(pk=id).update(**box_idea_data)
        box_idea.refresh_from_db()
        if not box_idea.employee:
            box_idea.employee = creator.get_employee_in_company()
            box_idea.save()
        return UpdateBoxIdea(box_idea=box_idea)
        
class UpdateBoxIdeaState(graphene.Mutation):
    class Arguments:
        id = graphene.ID()

    box_idea = graphene.Field(BoxIdeaType)
    done = graphene.Boolean()
    success = graphene.Boolean()
    message = graphene.String()

    def mutate(root, info, id, box_idea_fields=None):
        creator = info.context.user
        try:
            box_idea = BoxIdea.objects.get(pk=id, company=creator.the_current_company)
        except BoxIdea.DoesNotExist:
            raise e
        done = True
        success = True
        message = ''
        try:
            BoxIdea.objects.filter(pk=id).update(is_active=not box_idea.is_active)
            box_idea.refresh_from_db()
        except Exception as e:
            done = False
            success = False
            box_idea=None
            message = "Une erreur s'est produite."
        return UpdateBoxIdeaState(done=done, success=success, message=message,box_idea=box_idea)


class DeleteBoxIdea(graphene.Mutation):
    class Arguments:
        id = graphene.ID()

    box_idea = graphene.Field(BoxIdeaType)
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
            box_idea = BoxIdea.objects.get(pk=id, company=current_user.the_current_company)
        except BoxIdea.DoesNotExist:
            raise e
        if current_user.is_superuser or box_idea.creator==current_user:
            box_idea = BoxIdea.objects.get(pk=id)
            box_idea.delete()
            deleted = True
            success = True
        else:
            message = "Oups ! Vous n'avez pas les droits pour supprimer cet élément."
        return DeleteBoxIdea(deleted=deleted, success=success, message=message, id=id)

        
#*********************************************************************************************************************#

class QualitiesMutation(graphene.ObjectType):
    create_undesirable_event = CreateUndesirableEvent.Field()
    update_undesirable_event = UpdateUndesirableEvent.Field()
    update_undesirable_event_fields = UpdateUndesirableEventFields.Field()
    update_undesirable_event_state = UpdateUndesirableEventState.Field()
    create_undesirable_event_ticket = CreateUndesirableEventTicket.Field()
    delete_undesirable_event = DeleteUndesirableEvent.Field()

    create_box_idea = CreateBoxIdea.Field()
    update_box_idea = UpdateBoxIdea.Field()
    delete_box_idea = DeleteBoxIdea.Field()




#*********************************Subscription****************************************#


class OnUndesirableEventAdded(channels_graphql_ws.Subscription):
    """Simple GraphQL subscription."""

    # Leave only latest 64 messages in the server queue.
    notification_queue_limit = 64

    # Subscription payload.
    undesirable_event = graphene.Field(UndesirableEventType)

    class Arguments:
        """That is how subscription arguments are defined."""

    @staticmethod
    def subscribe(root, info):
        """Called when user subscribes."""

        # Return the list of subscription group names.
        return ["ON_EI_ADDED"]

    @staticmethod
    def publish(payload, info):
        """Called to notify the client."""

        # Here `payload` contains the `payload` from the `broadcast()`
        # invocation (see below). You can return `MySubscription.SKIP`
        # if you wish to suppress the notification to a particular
        # client. For example, this allows to avoid notifications for
        # the actions made by this particular client.
        user = info.context.user
        if str(user.the_current_company.id) != str(payload.company.id) and not user.can_manage_quality():
            return OnUndesirableEventAdded.SKIP
        return OnUndesirableEventAdded(undesirable_event=payload)

class OnUndesirableEventUpdated(channels_graphql_ws.Subscription):
    """Simple GraphQL subscription."""

    # Leave only latest 64 messages in the server queue.
    notification_queue_limit = 64

    # Subscription payload.
    undesirable_event = graphene.Field(UndesirableEventType)

    class Arguments:
        """That is how subscription arguments are defined."""

    @staticmethod
    def subscribe(root, info):
        """Called when user subscribes."""

        # Return the list of subscription group names.
        return ["ON_EI_UPDATED"]

    @staticmethod
    def publish(payload, info):
        """Called to notify the client."""

        # Here `payload` contains the `payload` from the `broadcast()`
        # invocation (see below). You can return `MySubscription.SKIP`
        # if you wish to suppress the notification to a particular
        # client. For example, this allows to avoid notifications for
        # the actions made by this particular client.
        user = info.context.user
        if str(user.the_current_company.id) != str(payload.company.id):
            return OnUndesirableEventUpdated.SKIP
        return OnUndesirableEventUpdated(undesirable_event=payload)

class OnUndesirableEventDeleted(channels_graphql_ws.Subscription):
    """Simple GraphQL subscription."""

    # Leave only latest 64 messages in the server queue.
    notification_queue_limit = 64

    # Subscription payload.
    undesirable_event = graphene.Field(UndesirableEventType)

    class Arguments:
        """That is how subscription arguments are defined."""

    @staticmethod
    def subscribe(root, info):
        """Called when user subscribes."""

        # Return the list of subscription group names.
        return ["ON_EI_DELETED"]

    @staticmethod
    def publish(payload, info):
        """Called to notify the client."""

        # Here `payload` contains the `payload` from the `broadcast()`
        # invocation (see below). You can return `MySubscription.SKIP`
        # if you wish to suppress the notification to a particular
        # client. For example, this allows to avoid notifications for
        # the actions made by this particular client.
        user = info.context.user
        if str(user.the_current_company.id) != str(payload.company.id):
            return OnUndesirableEventDeleted.SKIP
        return OnUndesirableEventDeleted(undesirable_event=payload)

#*************************************************************************#
class QualitiesSubscription(graphene.ObjectType):
    on_undesirable_event_added = OnUndesirableEventAdded.Field()
    on_undesirable_event_updated = OnUndesirableEventUpdated.Field()
    on_undesirable_event_deleted = OnUndesirableEventDeleted.Field()