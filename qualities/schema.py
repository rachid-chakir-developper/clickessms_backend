import graphene
from graphene_django import DjangoObjectType
from django.core.files.uploadedfile import InMemoryUploadedFile, UploadedFile
from graphql_jwt.decorators import login_required
from graphene_file_upload.scalars import Upload

from django.db.models import Q

from qualities.models import UndesirableEvent, UndesirableEventEstablishment, UndesirableEventEmployee, UndesirableEventBeneficiary, UndesirableEventNotifiedPerson, ActionPlanObjective, ActionPlanObjectiveAction
from medias.models import Folder, File
from companies.models import Establishment
from human_ressources.models import Employee, Beneficiary

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

class ActionPlanObjectiveActionType(DjangoObjectType):
    class Meta:
        model = ActionPlanObjectiveAction
        fields = "__all__"

class ActionPlanObjectiveType(DjangoObjectType):
    class Meta:
        model = ActionPlanObjective
        fields = "__all__"
    completion_percentage = graphene.Float()
    def resolve_completion_percentage(instance, info, **kwargs):
        return instance.completion_percentage

class ActionPlanObjectiveNodeType(graphene.ObjectType):
    nodes = graphene.List(ActionPlanObjectiveType)
    total_count = graphene.Int()

class ActionPlanObjectiveFilterInput(graphene.InputObjectType):
    keyword = graphene.String(required=False)
    starting_date_time = graphene.DateTime(required=False)
    ending_date_time = graphene.DateTime(required=False)
    establishments = graphene.List(graphene.Int, required=False)

class UndesirableEventType(DjangoObjectType):
    class Meta:
        model = UndesirableEvent
        fields = "__all__"
    image = graphene.String()
    def resolve_image( instance, info, **kwargs ):
        return instance.image and info.context.build_absolute_uri(instance.image.image.url)
    completion_percentage = graphene.Float()
    def resolve_completion_percentage(instance, info, **kwargs):
        return instance.completion_percentage

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

class ActionPlanObjectiveActionInput(graphene.InputObjectType):
    id = graphene.ID(required=False)
    action = graphene.String(required=False)
    due_date = graphene.DateTime(required=False)
    employees = graphene.List(graphene.Int, required=False)
    status = graphene.String(required=False)

class ActionPlanObjectiveInput(graphene.InputObjectType):
    id = graphene.ID(required=False)
    number = graphene.String(required=False)
    title = graphene.String(required=False)
    description = graphene.String(required=False)
    priority = graphene.String(required=False)
    status = graphene.String(required=False)
    employee_id = graphene.Int(name="employee", required=False)
    is_active = graphene.Boolean(required=False)
    undesirable_event_id = graphene.Int(name="undesirableEvent", required=False)
    establishments = graphene.List(graphene.Int, required=False)
    actions = graphene.List(ActionPlanObjectiveActionInput, required=False)

class UndesirableEventInput(graphene.InputObjectType):
    id = graphene.ID(required=False)
    number = graphene.String(required=False)
    title = graphene.String(required=True)
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
    status = graphene.String(required=False)
    normal_types = graphene.List(graphene.Int, required=False)
    serious_types = graphene.List(graphene.Int, required=False)
    frequency_id = graphene.Int(name="frequency", required=False)
    employee_id = graphene.Int(name="employee", required=False)
    establishments = graphene.List(graphene.Int, required=False)
    employees = graphene.List(graphene.Int, required=False)
    beneficiaries = graphene.List(graphene.Int, required=False)
    notified_persons = graphene.List(graphene.Int, required=False)

class QualitiesQuery(graphene.ObjectType):
    undesirable_events = graphene.Field(UndesirableEventNodeType, undesirable_event_filter= UndesirableEventFilterInput(required=False), offset = graphene.Int(required=False), limit = graphene.Int(required=False), page = graphene.Int(required=False))
    undesirable_event = graphene.Field(UndesirableEventType, id = graphene.ID())
    action_plan_objectives = graphene.Field(ActionPlanObjectiveNodeType, action_plan_objective_filter= ActionPlanObjectiveFilterInput(required=False), offset = graphene.Int(required=False), limit = graphene.Int(required=False), page = graphene.Int(required=False))
    action_plan_objective = graphene.Field(ActionPlanObjectiveType, id = graphene.ID())
    def resolve_undesirable_events(root, info, undesirable_event_filter=None, offset=None, limit=None, page=None):
        # We can easily optimize query count in the resolve method
        user = info.context.user
        company = user.current_company if user.current_company is not None else user.company
        total_count = 0
        undesirable_events = UndesirableEvent.objects.filter(company=company)
        if undesirable_event_filter:
            keyword = undesirable_event_filter.get('keyword', '')
            starting_date_time = undesirable_event_filter.get('starting_date_time')
            ending_date_time = undesirable_event_filter.get('ending_date_time')
            beneficiaries = undesirable_event_filter.get('beneficiaries')
            establishments = undesirable_event_filter.get('establishments')
            employees = undesirable_event_filter.get('employees')
            if beneficiaries:
                undesirable_events = undesirable_events.filter(undesirableeventbeneficiary__beneficiary__id__in=beneficiaries)
            if establishments:
                undesirable_events = undesirable_events.filter(undesirableeventestablishment__establishment__id__in=establishments)
            if employees:
                undesirable_events = undesirable_events.filter(undesirableeventemployee__employee__id__in=employees)
            if keyword:
                undesirable_events = undesirable_events.filter(Q(title__icontains=keyword))
            if starting_date_time:
                undesirable_events = undesirable_events.filter(starting_date_time__gte=starting_date_time)
            if ending_date_time:
                undesirable_events = undesirable_events.filter(starting_date_time__lte=ending_date_time)
        undesirable_events = undesirable_events.order_by('-created_at')
        total_count = undesirable_events.count()
        if page:
            offset = limit * (page - 1)
        if offset is not None and limit is not None:
            undesirable_events = undesirable_events[offset:offset + limit]
        return UndesirableEventNodeType(nodes=undesirable_events, total_count=total_count)

    def resolve_undesirable_event(root, info, id):
        # We can easily optimize query count in the resolve method
        try:
            undesirable_event = UndesirableEvent.objects.get(pk=id)
        except UndesirableEvent.DoesNotExist:
            undesirable_event = None
        return undesirable_event
    def resolve_action_plan_objectives(root, info, action_plan_objective_filter=None, offset=None, limit=None, page=None):
        # We can easily optimize query count in the resolve method
        user = info.context.user
        company = user.current_company if user.current_company is not None else user.company
        total_count = 0
        action_plan_objectives = ActionPlanObjective.objects.filter(company=company)
        if action_plan_objective_filter:
            keyword = action_plan_objective_filter.get('keyword', '')
            starting_date_time = action_plan_objective_filter.get('starting_date_time')
            ending_date_time = action_plan_objective_filter.get('ending_date_time')
            establishments = action_plan_objective_filter.get('establishments')
            if establishments:
                action_plan_objectives = action_plan_objectives.filter(undesirableeventestablishment__establishment__id__in=establishments)
            if keyword:
                action_plan_objectives = action_plan_objectives.filter(Q(title__icontains=keyword))
            if starting_date_time:
                action_plan_objectives = action_plan_objectives.filter(starting_date_time__gte=starting_date_time)
            if ending_date_time:
                action_plan_objectives = action_plan_objectives.filter(starting_date_time__lte=ending_date_time)
        action_plan_objectives = action_plan_objectives.order_by('-created_at')
        total_count = action_plan_objectives.count()
        if page:
            offset = limit * (page - 1)
        if offset is not None and limit is not None:
            action_plan_objectives = action_plan_objectives[offset:offset + limit]
        return ActionPlanObjectiveNodeType(nodes=action_plan_objectives, total_count=total_count)

    def resolve_action_plan_objective(root, info, id):
        # We can easily optimize query count in the resolve method
        try:
            action_plan_objective = ActionPlanObjective.objects.get(pk=id)
        except ActionPlanObjective.DoesNotExist:
            action_plan_objective = None
        return action_plan_objective

#************************************************************************

class CreateUndesirableEvent(graphene.Mutation):
    class Arguments:
        undesirable_event_data = UndesirableEventInput(required=True)
        image = Upload(required=False)

    undesirable_event = graphene.Field(UndesirableEventType)

    def mutate(root, info, image=None, undesirable_event_data=None):
        creator = info.context.user
        establishment_ids = undesirable_event_data.pop("establishments")
        beneficiary_ids = undesirable_event_data.pop("beneficiaries")
        employee_ids = undesirable_event_data.pop("employees")
        notified_person_ids = undesirable_event_data.pop("notified_persons")
        normal_type_ids = undesirable_event_data.pop("normal_types")
        serious_type_ids = undesirable_event_data.pop("serious_types")
        undesirable_event = UndesirableEvent(**undesirable_event_data)
        undesirable_event.creator = creator
        undesirable_event.company = creator.current_company if creator.current_company is not None else creator.company
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
            undesirable_event.employee = creator.getEmployeeInCompany()
        folder = Folder.objects.create(name=str(undesirable_event.id)+'_'+undesirable_event.title,creator=creator)
        undesirable_event.folder = folder
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
        return CreateUndesirableEvent(undesirable_event=undesirable_event)

class UpdateUndesirableEvent(graphene.Mutation):
    class Arguments:
        id = graphene.ID()
        undesirable_event_data = UndesirableEventInput(required=True)
        image = Upload(required=False)

    undesirable_event = graphene.Field(UndesirableEventType)

    def mutate(root, info, id, image=None, undesirable_event_data=None):
        creator = info.context.user
        establishment_ids = undesirable_event_data.pop("establishments")
        beneficiary_ids = undesirable_event_data.pop("beneficiaries")
        employee_ids = undesirable_event_data.pop("employees")
        notified_person_ids = undesirable_event_data.pop("notified_persons")
        normal_type_ids = undesirable_event_data.pop("normal_types")
        serious_type_ids = undesirable_event_data.pop("serious_types")
        UndesirableEvent.objects.filter(pk=id).update(**undesirable_event_data)
        undesirable_event = UndesirableEvent.objects.get(pk=id)
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
        if not undesirable_event.employee:
            undesirable_event.employee = creator.getEmployeeInCompany()
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
        return UpdateUndesirableEvent(undesirable_event=undesirable_event)

class UpdateUndesirableEventState(graphene.Mutation):
    class Arguments:
        id = graphene.ID()

    undesirable_event = graphene.Field(UndesirableEventType)
    done = graphene.Boolean()
    success = graphene.Boolean()
    message = graphene.String()

    def mutate(root, info, id, undesirable_event_fields=None):
        creator = info.context.user
        done = True
        success = True
        undesirable_event = None
        message = ''
        try:
            undesirable_event = UndesirableEvent.objects.get(pk=id)
            UndesirableEvent.objects.filter(pk=id).update(is_active=not undesirable_event.is_active)
            undesirable_event.refresh_from_db()
        except Exception as e:
            done = False
            success = False
            undesirable_event=None
            message = "Une erreur s'est produite."
        return UpdateUndesirableEventState(done=done, success=success, message=message,undesirable_event=undesirable_event)


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
        if current_user.is_superuser:
            undesirable_event = UndesirableEvent.objects.get(pk=id)
            undesirable_event.delete()
            deleted = True
            success = True
        else:
            message = "Vous n'êtes pas un Superuser."
        return DeleteUndesirableEvent(deleted=deleted, success=success, message=message, id=id)
        
#*************************************************************************#  
#*************************************************************************#
#************************************************************************

class CreateActionPlanObjective(graphene.Mutation):
    class Arguments:
        action_plan_objective_data = ActionPlanObjectiveInput(required=True)

    action_plan_objective = graphene.Field(ActionPlanObjectiveType)

    def mutate(root, info, action_plan_objective_data=None):
        creator = info.context.user
        establishment_ids = action_plan_objective_data.pop("establishments") if "establishments" in action_plan_objective_data else None
        action_plan_objective_actions = action_plan_objective_data.pop("actions")
        action_plan_objective = ActionPlanObjective(**action_plan_objective_data)
        action_plan_objective.creator = creator
        action_plan_objective.company = creator.current_company if creator.current_company is not None else creator.company
        action_plan_objective.save()
        if establishment_ids and establishment_ids is not None:
            action_plan_objective.establishments.set(establishment_ids)
        folder = Folder.objects.create(name=str(action_plan_objective.id)+'_'+action_plan_objective.title,creator=creator)
        action_plan_objective.folder = folder
        if not action_plan_objective.employee:
            action_plan_objective.employee = creator.getEmployeeInCompany()
        for item in action_plan_objective_actions:
            employees_ids = item.pop("employees") if "employees" in item else None
            action_plan_objective_action = ActionPlanObjectiveAction(**item)
            action_plan_objective_action.action_plan_objective = action_plan_objective
            action_plan_objective_action.save()
            if employees_ids and employees_ids is not None:
                action_plan_objective_action.employees.set(employees_ids)

        action_plan_objective.save()
        return CreateActionPlanObjective(action_plan_objective=action_plan_objective)

class UpdateActionPlanObjective(graphene.Mutation):
    class Arguments:
        id = graphene.ID()
        action_plan_objective_data = ActionPlanObjectiveInput(required=True)

    action_plan_objective = graphene.Field(ActionPlanObjectiveType)

    def mutate(root, info, id, image=None, action_plan_objective_data=None):
        creator = info.context.user
        establishment_ids = action_plan_objective_data.pop("establishments") if "establishments" in action_plan_objective_data else None
        action_plan_objective_actions = action_plan_objective_data.pop("actions")
        ActionPlanObjective.objects.filter(pk=id).update(**action_plan_objective_data)
        action_plan_objective = ActionPlanObjective.objects.get(pk=id)
        if establishment_ids and establishment_ids is not None:
            action_plan_objective.establishments.set(establishment_ids)
        if not action_plan_objective.folder or action_plan_objective.folder is None:
            folder = Folder.objects.create(name=str(action_plan_objective.id)+'_'+action_plan_objective.title,creator=creator)
            ActionPlanObjective.objects.filter(pk=id).update(folder=folder)
        if not action_plan_objective.employee:
            action_plan_objective.employee = creator.getEmployeeInCompany()
            action_plan_objective.save()
        action_plan_objective_action_ids = [item.id for item in action_plan_objective_actions if item.id is not None]
        ActionPlanObjectiveAction.objects.filter(action_plan_objective=action_plan_objective).exclude(id__in=action_plan_objective_action_ids).delete()
        for item in action_plan_objective_actions:
            employees_ids = item.pop("employees") if "employees" in item else None
            if id in item or 'id' in item:
                ActionPlanObjectiveAction.objects.filter(pk=item.id).update(**item)
                action_plan_objective_action = ActionPlanObjectiveAction.objects.get(pk=item.id)
            else:
                action_plan_objective_action = ActionPlanObjectiveAction(**item)
                action_plan_objective_action.action_plan_objective = action_plan_objective
                action_plan_objective_action.save()
            if employees_ids and employees_ids is not None:
                action_plan_objective_action.employees.set(employees_ids)

        return UpdateActionPlanObjective(action_plan_objective=action_plan_objective)

class DeleteActionPlanObjective(graphene.Mutation):
    class Arguments:
        id = graphene.ID()

    action_plan_objective = graphene.Field(ActionPlanObjectiveType)
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
            action_plan_objective = ActionPlanObjective.objects.get(pk=id)
            action_plan_objective.delete()
            deleted = True
            success = True
        else:
            message = "Vous n'êtes pas un Superuser."
        return DeleteActionPlanObjective(deleted=deleted, success=success, message=message, id=id)

#************************************************************************

#*************************************************************************#
class QualitiesMutation(graphene.ObjectType):
    create_undesirable_event = CreateUndesirableEvent.Field()
    update_undesirable_event = UpdateUndesirableEvent.Field()
    update_undesirable_event_state = UpdateUndesirableEventState.Field()
    delete_undesirable_event = DeleteUndesirableEvent.Field()

    create_action_plan_objective = CreateActionPlanObjective.Field()
    update_action_plan_objective = UpdateActionPlanObjective.Field()
    delete_action_plan_objective = DeleteActionPlanObjective.Field()