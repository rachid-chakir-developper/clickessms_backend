import graphene
from graphene_django import DjangoObjectType
from django.core.files.uploadedfile import InMemoryUploadedFile, UploadedFile
from graphql_jwt.decorators import login_required
from graphene_file_upload.scalars import Upload
from datetime import date, datetime, time

from django.db.models import Q

from works.models import Task, TaskEstablishment, TaskWorker, TaskMaterial, TaskVehicle, TaskChecklistItem, TaskStep, STEP_TYPES_LABELS, STEP_TYPES_ALL, STATUS_All, Ticket, TaskAction
from human_ressources.models import Employee
from companies.models import Establishment
from vehicles.models import Vehicle
from stocks.models import Material
from medias.models import Folder, File
from feedbacks.models import Comment, Signature
from notifications.notificator import notify, push_notification_to_employees
from feedbacks.google_calendar import create_calendar_event_task, update_calendar_event_task, delete_calendar_event_task

from feedbacks.schema import SignatureInput

class TaskActionType(DjangoObjectType):
    class Meta:
        model = TaskAction
        fields = "__all__"

class TaskActionNodeType(graphene.ObjectType):
    nodes = graphene.List(TaskActionType)
    total_count = graphene.Int()

class TaskActionFilterInput(graphene.InputObjectType):
    keyword = graphene.String(required=False)
    starting_date_time = graphene.DateTime(required=False)
    ending_date_time = graphene.DateTime(required=False)
    employees = graphene.List(graphene.Int, required=False)

class TicketType(DjangoObjectType):
    class Meta:
        model = Ticket
        fields = "__all__"
    completion_percentage = graphene.Float()
    def resolve_completion_percentage(instance, info, **kwargs):
        return instance.completion_percentage

class TicketNodeType(graphene.ObjectType):
    nodes = graphene.List(TicketType)
    total_count = graphene.Int()

class TicketFilterInput(graphene.InputObjectType):
    keyword = graphene.String(required=False)
    starting_date_time = graphene.DateTime(required=False)
    ending_date_time = graphene.DateTime(required=False)
    establishments = graphene.List(graphene.Int, required=False)

class TaskChecklistItemType(DjangoObjectType):
    class Meta:
        model = TaskChecklistItem
        fields = "__all__"

class TaskEstablishmentType(DjangoObjectType):
    class Meta:
        model = TaskEstablishment
        fields = "__all__"

class TaskWorkerType(DjangoObjectType):
    class Meta:
        model = TaskWorker
        fields = "__all__"

class TaskVehicleType(DjangoObjectType):
    class Meta:
        model = TaskVehicle
        fields = "__all__"

class TaskMaterialType(DjangoObjectType):
    class Meta:
        model = TaskMaterial
        fields = "__all__"

class TaskStepType(DjangoObjectType):
    class Meta:
        model = TaskStep
        fields = "__all__"

class TaskType(DjangoObjectType):
    class Meta:
        model = Task
        fields = "__all__"

class TaskNodeType(graphene.ObjectType):
    nodes = graphene.List(TaskType)
    total_count = graphene.Int()

class TaskActionInput(graphene.InputObjectType):
    id = graphene.ID(required=False)
    description = graphene.String(required=False)
    due_date = graphene.DateTime(required=False)
    employees = graphene.List(graphene.Int, required=False)
    status = graphene.String(required=False)

class TicketInput(graphene.InputObjectType):
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
    actions = graphene.List(TaskActionInput, required=False)

class TaskChecklistItemInput(graphene.InputObjectType):
    id = graphene.ID(required=False)
    number = graphene.String(required=False)
    name = graphene.String(required=False)
    localisation = graphene.String(required=False)
    comment = graphene.String(required=False)
    description = graphene.String(required=False)
    observation = graphene.String(required=False)
    status = graphene.String(required=False)
    is_active = graphene.Boolean(required=False)
    task_id = graphene.Int(name="task", required=False)

class TaskInput(graphene.InputObjectType):
    id = graphene.ID(required=False)
    number = graphene.String(required=False)
    name = graphene.String(required=False)
    starting_date_time = graphene.DateTime(required=False)
    ending_date_time = graphene.DateTime(required=False)
    estimated_budget = graphene.Float(required=False)
    latitude = graphene.String(required=False)
    longitude = graphene.String(required=False)
    city = graphene.String(required=False)
    country = graphene.String(required=False)
    zip_code = graphene.String(required=False)
    address = graphene.String(required=False)
    additional_address = graphene.String(required=False)
    # Intérvenant Véhicules matérails infos start
    workers_infos = graphene.String(required=False)
    vehicles_infos = graphene.String(required=False)
    materials_infos = graphene.String(required=False)
    # ****************************
    comment = graphene.String(required=False)
    description = graphene.String(required=False)
    observation = graphene.String(required=False)
    priority = graphene.String(required=False)
    work_level = graphene.String(required=False)
    is_active = graphene.Boolean(required=False)
    status = graphene.String(required=False)
    establishments = graphene.List(graphene.Int, required=False)
    workers = graphene.List(graphene.Int, required=False)
    vehicles = graphene.List(graphene.Int, required=False)
    materials = graphene.List(graphene.Int, required=False)
    task_checklist = graphene.List(TaskChecklistItemInput, required=False)

class TaskFilterInput(graphene.InputObjectType):
    keyword = graphene.String(required=False)
    starting_date_time = graphene.DateTime(required=False)
    ending_date_time = graphene.DateTime(required=False)
    statuses = graphene.List(graphene.String, required=False)

class TaskFieldInput(graphene.InputObjectType):
    id = graphene.ID(required=False)
    observation = graphene.String(required=False)
    priority = graphene.String(required=False)
    work_level = graphene.String(required=False)
    is_active = graphene.Boolean(required=False)
    status = graphene.String(required=False)

class TaskStepMediaInput(graphene.InputObjectType):
    id = graphene.ID(required=False)
    image = Upload(required=False)
    video = Upload(required=False)
    media = Upload(required=False)
    caption = graphene.String(required=False)

class TaskStepInput(graphene.InputObjectType):
    id = graphene.ID(required=False)
    name = graphene.String(required=False)
    step_type = graphene.String(required=False)
    task_id = graphene.Int(name="task", required=False)

class WorksQuery(graphene.ObjectType):
    tasks = graphene.Field(TaskNodeType, task_filter= TaskFilterInput(required=False), offset = graphene.Int(required=False), limit = graphene.Int(required=False), page = graphene.Int(required=False))
    my_tasks = graphene.Field(TaskNodeType, task_filter= TaskFilterInput(required=False), offset = graphene.Int(required=False), limit = graphene.Int(required=False), page = graphene.Int(required=False))
    task = graphene.Field(TaskType, id = graphene.ID())
    task_step = graphene.Field(TaskStepType, task_id = graphene.ID(), step_type = graphene.String())
    tickets = graphene.Field(TicketNodeType, ticket_filter= TicketFilterInput(required=False), offset = graphene.Int(required=False), limit = graphene.Int(required=False), page = graphene.Int(required=False))
    ticket = graphene.Field(TicketType, id = graphene.ID())
    task_actions = graphene.Field(TaskActionNodeType, task_action_filter= TaskActionFilterInput(required=False), offset = graphene.Int(required=False), limit = graphene.Int(required=False), page = graphene.Int(required=False))
    task_action = graphene.Field(TaskActionType, id = graphene.ID())

    def resolve_tasks(root, info, task_filter=None, offset=None, limit=None, page=None):
        # We can easily optimize query count in the resolve method
        user = info.context.user
        company = user.current_company if user.current_company is not None else user.company
        total_count = 0
        tasks = Task.objects.filter(company=company)
        if task_filter:
            keyword = task_filter.get('keyword', '')
            starting_date_time = task_filter.get('starting_date_time')
            ending_date_time = task_filter.get('ending_date_time')
            statuses = task_filter.get('statuses')
            if keyword:
                tasks = tasks.filter(Q(number__icontains=keyword) | Q(name__icontains=keyword))
            if starting_date_time:
                tasks = tasks.filter(starting_date_time__gte=starting_date_time)
            if ending_date_time:
                tasks = tasks.filter(starting_date_time__lte=ending_date_time)
            if statuses:
                tasks = tasks.filter(status__in=statuses)
        tasks = tasks.order_by('-created_at')
        total_count = tasks.count()
        if page:
            offset = limit * (page - 1)
        if offset is not None and limit is not None:
            tasks = tasks[offset:offset + limit]
        return TaskNodeType(nodes=tasks, total_count=total_count)

    def resolve_my_tasks(root, info, task_filter=None, offset=None, limit=None, page=None):
        # We can easily optimize query count in the resolve method
        user = info.context.user
        total_count = 0
        my_tasks = Task.objects.filter(taskworker__employee__employee_user__id=user.id)
        # Définir les variables de date à None par défaut
        starting_date_time = None
        ending_date_time = None
        if task_filter:
            keyword = task_filter.get('keyword', '')
            starting_date_time = task_filter.get('starting_date_time')
            ending_date_time = task_filter.get('ending_date_time')
            if keyword:
                my_tasks = my_tasks.filter(name__icontains=keyword)
            if starting_date_time:
                my_tasks = my_tasks.filter(starting_date_time__gte=starting_date_time)
            if ending_date_time:
                my_tasks = my_tasks.filter(starting_date_time__lte=ending_date_time)
        # Si aucune date de début n'est fournie dans le filtre, filtrez par défaut pour les tâches d'aujourd'hui
        if not starting_date_time and not ending_date_time:
            today_start = datetime.combine(date.today(), time.min)
            today_end = datetime.combine(date.today(), time.max)
            my_tasks = my_tasks.filter(starting_date_time__range=(today_start, today_end))
        my_tasks = my_tasks.order_by('starting_date_time')
        total_count = my_tasks.count()
        if page:
            offset = limit * (page - 1)
        if offset is not None and limit is not None:
            my_tasks = my_tasks[offset:offset + limit]
        return TaskNodeType(nodes=my_tasks, total_count=total_count)

    def resolve_task(root, info, id):
        # We can easily optimize query count in the resolve method
        try:
            task = Task.objects.get(pk=id)
        except Task.DoesNotExist:
            task = None
        return task

    def resolve_task_step(root, info, task_id, step_type):
        # We can easily optimize query count in the resolve method
        creator = info.context.user
        try:
            task_step = TaskStep.objects.get(task__id=task_id, step_type=step_type)
            if task_step.task.status != STATUS_All['STARTED']:
                task = Task.objects.get(pk=task_id)
                if not task.started_at or task.started_at is None:
                    Task.objects.filter(pk=task_id).update(status=STATUS_All['STARTED'], started_at=datetime.now())
                    if task_step.step_type == STEP_TYPES_ALL['BEFORE']:
                        notification_data = {
                            "sender": creator,
                            "recipient": task.creator,
                            "notification_type": "TASK_STARTED",
                            "title": "Une tâche commencée",
                            "message": "Une tâche vient d'être commencée.",
                            "task": task,
                        }
                        notify(notification_data)
            if task_step.status != STATUS_All['STARTED']:
                TaskStep.objects.filter(pk=task_step.id).update(status=STATUS_All['STARTED'])
            try:
                if task_step.step_type != STEP_TYPES_ALL['IN_PROGRESS']:
                    TaskStep.objects.filter(task__id=task_id, step_type=STEP_TYPES_ALL['BEFORE']).update(status=STATUS_All['FINISHED'])
                elif task_step.step_type != STEP_TYPES_ALL['AFTER']:
                    TaskStep.objects.filter(task__id=task_id, step_type=STEP_TYPES_ALL['BEFORE']).update(status=STATUS_All['FINISHED'])
                    TaskStep.objects.filter(task__id=task_id, step_type=STEP_TYPES_ALL['IN_PROGRESS']).update(status=STATUS_All['FINISHED'])
            except Exception as e:
                raise e
        except TaskStep.DoesNotExist:
            task_step = None
        return task_step
        
    def resolve_tickets(root, info, ticket_filter=None, offset=None, limit=None, page=None):
        # We can easily optimize query count in the resolve method
        user = info.context.user
        company = user.current_company if user.current_company is not None else user.company
        total_count = 0
        tickets = Ticket.objects.filter(company=company)
        if ticket_filter:
            keyword = ticket_filter.get('keyword', '')
            starting_date_time = ticket_filter.get('starting_date_time')
            ending_date_time = ticket_filter.get('ending_date_time')
            establishments = ticket_filter.get('establishments')
            if establishments:
                tickets = tickets.filter(undesirableeventestablishment__establishment__id__in=establishments)
            if keyword:
                tickets = tickets.filter(Q(title__icontains=keyword))
            if starting_date_time:
                tickets = tickets.filter(starting_date_time__gte=starting_date_time)
            if ending_date_time:
                tickets = tickets.filter(starting_date_time__lte=ending_date_time)
        tickets = tickets.order_by('-created_at')
        total_count = tickets.count()
        if page:
            offset = limit * (page - 1)
        if offset is not None and limit is not None:
            tickets = tickets[offset:offset + limit]
        return TicketNodeType(nodes=tickets, total_count=total_count)

    def resolve_ticket(root, info, id):
        # We can easily optimize query count in the resolve method
        try:
            ticket = Ticket.objects.get(pk=id)
        except Ticket.DoesNotExist:
            ticket = None
        return ticket
    def resolve_task_actions(root, info, task_action_filter=None, offset=None, limit=None, page=None):
        # We can easily optimize query count in the resolve method
        user = info.context.user
        company = user.current_company if user.current_company is not None else user.company
        total_count = 0
        task_actions = TaskAction.objects.filter(company=company, employees=user.get_employee_in_company())
        if task_action_filter:
            keyword = task_action_filter.get('keyword', '')
            starting_date_time = task_action_filter.get('starting_date_time')
            ending_date_time = task_action_filter.get('ending_date_time')
            employees = task_action_filter.get('employees')
            if employees:
                task_actions = task_actions.filter(employees__id__in=employees)
            if keyword:
                task_actions = task_actions.filter(Q(title__icontains=keyword))
            if starting_date_time:
                task_actions = task_actions.filter(starting_date_time__gte=starting_date_time)
            if ending_date_time:
                task_actions = task_actions.filter(starting_date_time__lte=ending_date_time)
        task_actions = task_actions.order_by('-due_date')
        total_count = task_actions.count()
        if page:
            offset = limit * (page - 1)
        if offset is not None and limit is not None:
            task_actions = task_actions[offset:offset + limit]
        return TaskActionNodeType(nodes=task_actions, total_count=total_count)

    def resolve_task_action(root, info, id):
        # We can easily optimize query count in the resolve method
        try:
            task_action = TaskAction.objects.get(pk=id)
        except TaskAction.DoesNotExist:
            task_action = None
        return task_action

#************************************************************************

class CreateTask(graphene.Mutation):
    class Arguments:
        task_data = TaskInput(required=True)

    task = graphene.Field(TaskType)

    def mutate(root, info, task_data=None):
        creator = info.context.user
        establishment_ids = task_data.pop("establishments")
        worker_ids = task_data.pop("workers")
        vehicle_ids = task_data.pop("vehicles")
        material_ids = task_data.pop("materials")
        task_checklist = task_data.pop("task_checklist")
        task = Task(**task_data)
        task.creator = creator
        task.company = creator.current_company if creator.current_company is not None else creator.company
        task.save()
        folder = Folder.objects.create(name=str(task.id)+'_'+task.name,creator=creator)
        task.folder = folder
        task.save()
        employees = Employee.objects.filter(id__in=worker_ids)
        for employee in employees:
            try:
                task_worker = TaskWorker.objects.get(employee__id=employee.id, task__id=task.id)
            except TaskWorker.DoesNotExist:
                TaskWorker.objects.create(
                        task=task,
                        employee=employee,
                        creator=creator
                    )
                notification_data = {
                    "sender": creator,
                    "recipient": employee.employee_user.all().first(),
                    "notification_type": "ADDED_TO_TASK",
                    "title": "Nouvelle tâche assignée",
                    "message": "Vous avez une nouvelle tâche assignée.",
                    "task": task,
                }
                notify(notification_data)
        push_notification_data = {
            "title": "Nouvelle tâche assignée",
            "message": "Vous avez une nouvelle tâche assignée."
        }
        push_notification_to_employees(notification=push_notification_data, employees=employees)
        establishments = Establishment.objects.filter(id__in=establishment_ids)
        for establishment in establishments:
            try:
                task_establishment = TaskEstablishment.objects.get(establishment__id=establishment.id, task__id=task.id)
            except TaskEstablishment.DoesNotExist:
                TaskEstablishment.objects.create(
                        task=task,
                        establishment=establishment,
                        creator=creator
                    )
        vehicles = Vehicle.objects.filter(id__in=vehicle_ids)
        for vehicle in vehicles:
            try:
                task_vehicle = TaskVehicle.objects.get(vehicle__id=vehicle.id, task__id=task.id)
            except TaskVehicle.DoesNotExist:
                TaskVehicle.objects.create(
                        task=task,
                        vehicle=vehicle,
                        creator=creator
                    )
        materials = Material.objects.filter(id__in=material_ids)
        for material in materials:
            try:
                task_material = TaskMaterial.objects.get(material__id=material.id, task__id=task.id)
            except TaskMaterial.DoesNotExist:
                TaskMaterial.objects.create(
                        task=task,
                        material=material,
                        creator=creator
                    )
        for item in task_checklist:
            task_checklist_item = TaskChecklistItem(**item)
            task_checklist_item.task = task
            task_checklist_item.save()
        # Créez trois TaskStep pour chaque type
        for step_type in STEP_TYPES_LABELS:
            try:
                task_step = TaskStep.objects.get(step_type=step_type, task__id=task.id)
            except TaskStep.DoesNotExist:
                TaskStep.objects.create(
                    name=f"{step_type} Step",
                    task=task,
                    step_type=step_type,
                    creator=creator
                )
        # create_calendar_event_task(task=task)
        return CreateTask(task=task)

class UpdateTask(graphene.Mutation):
    class Arguments:
        id = graphene.ID()
        task_data = TaskInput(required=True)

    task = graphene.Field(TaskType)

    def mutate(root, info, id, task_data=None):
        creator = info.context.user
        establishment_ids = task_data.pop("establishments")
        worker_ids = task_data.pop("workers")
        vehicle_ids = task_data.pop("vehicles")
        material_ids = task_data.pop("materials")
        task_checklist = task_data.pop("task_checklist")
        Task.objects.filter(pk=id).update(**task_data)
        task = Task.objects.get(pk=id)
        task.save()
        if not task.folder or task.folder is None:
            folder = Folder.objects.create(name=str(task.id)+'_'+task.name,creator=creator)
            Task.objects.filter(pk=id).update(folder=folder)
        TaskWorker.objects.filter(task=task).exclude(employee__id__in=worker_ids).delete()
        employees = Employee.objects.filter(id__in=worker_ids)
        employees_to_notify = []
        for employee in employees:
            try:
                task_worker = TaskWorker.objects.get(employee__id=employee.id, task__id=task.id)
            except TaskWorker.DoesNotExist:
                TaskWorker.objects.create(
                        task=task,
                        employee=employee,
                        creator=creator
                    )
                notification_data = {
                    "sender": creator,
                    "recipient": employee.employee_user.all().first(),
                    "notification_type": "ADDED_TO_TASK",
                    "title": "Nouvelle tâche assignée",
                    "message": "Vous avez une nouvelle tâche assignée.",
                    "task": task,
                }
                notify(notification_data)
                employees_to_notify.append(employee)
        
        push_notification_data = {
            "title": "Nouvelle tâche assignée",
            "message": "Vous avez une nouvelle tâche assignée."
        }
        push_notification_to_employees(notification=push_notification_data, employees=employees_to_notify)
        TaskEstablishment.objects.filter(task=task).exclude(establishment__id__in=establishment_ids).delete()
        establishments = Establishment.objects.filter(id__in=establishment_ids)
        for establishment in establishments:
            try:
                task_establishment = TaskEstablishment.objects.get(establishment__id=establishment.id, task__id=task.id)
            except TaskEstablishment.DoesNotExist:
                TaskEstablishment.objects.create(
                        task=task,
                        establishment=establishment,
                        creator=creator
                    )
        TaskVehicle.objects.filter(task=task).exclude(vehicle__id__in=vehicle_ids).delete()
        vehicles = Vehicle.objects.filter(id__in=vehicle_ids)
        for vehicle in vehicles:
            try:
                task_vehicle = TaskVehicle.objects.get(vehicle__id=vehicle.id, task__id=task.id)
            except TaskVehicle.DoesNotExist:
                TaskVehicle.objects.create(
                        task=task,
                        vehicle=vehicle,
                        creator=creator
                    )
        TaskMaterial.objects.filter(task=task).exclude(material__id__in=material_ids).delete()
        materials = Material.objects.filter(id__in=material_ids)
        for material in materials:
            try:
                task_material = TaskMaterial.objects.get(material__id=material.id, task__id=task.id)
            except TaskMaterial.DoesNotExist:
                TaskMaterial.objects.create(
                        task=task,
                        material=material,
                        creator=creator
                    )
        for item in task_checklist:
            if id in item or 'id' in item:
                TaskChecklistItem.objects.filter(pk=item.id).update(**item)
            else:
                task_checklist_item = TaskChecklistItem(**item)
                task_checklist_item.task = task
                task_checklist_item.save()
        # Créez trois TaskStep pour chaque type
        for step_type in STEP_TYPES_LABELS:
            try:
                task_step = TaskStep.objects.get(step_type=step_type, task__id=task.id)
            except TaskStep.DoesNotExist:
                TaskStep.objects.create(
                    name=f"{step_type} Step",
                    task=task,
                    step_type=step_type,
                    creator=creator
                )
        # update_calendar_event_task(task=task)
        return UpdateTask(task=task)

class UpdateTaskFields(graphene.Mutation):
    class Arguments:
        id = graphene.ID()
        task_data = TaskInput(required=True)

    task = graphene.Field(TaskType)
    done = graphene.Boolean()
    success = graphene.Boolean()
    message = graphene.String()

    def mutate(root, info, id, task_data=None):
        creator = info.context.user
        done = True
        success = True
        task = None
        message = ''
        try:
            task = Task.objects.get(pk=id)
            Task.objects.filter(pk=id).update(**task_data)
            task.refresh_from_db()
        except Exception as e:
            done = False
            success = False
            task=None
            message = "Une erreur s'est produite."
        return UpdateTaskFields(done=done, success=success, message=message, task=task)

class UpdateTaskState(graphene.Mutation):
    class Arguments:
        id = graphene.ID()

    task = graphene.Field(TaskType)
    done = graphene.Boolean()
    success = graphene.Boolean()
    message = graphene.String()

    def mutate(root, info, id, task_fields=None):
        creator = info.context.user
        done = True
        success = True
        task = None
        message = ''
        try:
            task = Task.objects.get(pk=id)
            Task.objects.filter(pk=id).update(is_active=not task.is_active)
            task.refresh_from_db()
        except Exception as e:
            done = False
            success = False
            task=None
            message = "Une erreur s'est produite."
        return UpdateTaskState(done=done, success=success, message=message,task=task)

class UpdateTaskStep(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)
        task_step_data = TaskStepInput(required=False)
        images = graphene.List(TaskStepMediaInput, required=False)
        videos = graphene.List(TaskStepMediaInput, required=False)

    task_step = graphene.Field(TaskStepType)

    def mutate(root, info, id, images=None, videos=None, task_step_data=None):
        creator = info.context.user
        if task_step_data and task_step_data is not None:
            TaskStep.objects.filter(pk=id).update(**task_step_data)
        try:
            task_step = TaskStep.objects.get(pk=id)
        except TaskStep.DoesNotExist:
            raise ValueError("L'étape d'intervention spécifiée n'existe pas.")
        if not images:
            images = []
        for image_media in images:
            image = image_media.image
            caption = image_media.caption
            if id in image_media or 'id' in image_media:
                image_file = File.objects.get(pk=image_media.id)
            else:
                image_file = File()
                image_file.creator = creator
            if info.context.FILES and image and isinstance(image, UploadedFile):
                image_file.image = image
            image_file.caption = caption
            image_file.save()
            task_step.images.add(image_file)
        if not videos:
            videos = []
        for video_media in videos:
            video = video_media.video
            caption = video_media.caption
            if id in video_media  or 'id' in video_media:
                video_file = File.objects.get(pk=video_media.id)
            else:
                video_file = File()
                video_file.creator = creator
            if info.context.FILES and video and isinstance(video, UploadedFile):
                video_file.video = video
            video_file.caption = caption
            video_file.save()
            task_step.videos.add(video_file)
        task_step.save()
        return UpdateTaskStep(task_step=task_step)

class SignTaskSummary(graphene.Mutation):
    class Arguments:
        id = graphene.ID()
        signature_data = SignatureInput(required=True)
        signature_for = graphene.String()

    done = graphene.Boolean()
    success = graphene.Boolean()
    message = graphene.String()

    def mutate(root, info, id, signature_for, signature_data):
        creator = info.context.user
        done = True
        success = True
        message = ''
        try:
            task = Task.objects.get(pk=id)
            client_signature = task.client_signature
            employee_signature = task.employee_signature
            if client_signature and client_signature is not None and signature_for == "CLIENT":
                Signature.objects.filter(pk=client_signature.id).update(**signature_data)
                if not task.finished_at or task.finished_at is None:
                    Task.objects.filter(pk=id).update(status=STATUS_All['FINISHED'], finished_at=datetime.now())
                notification_data = {
                    "sender": creator,
                    "recipient": task.creator,
                    "notification_type": "TASK_FINISHED",
                    "title": "Une tâche finie",
                    "message": "Une tâche vient d'être finie.",
                    "task": task,
                }
                notify(notification_data)
            elif employee_signature and employee_signature is not None and signature_for == "EMPLOYEE":
                Signature.objects.filter(pk=employee_signature.id).update(**signature_data)
                Task.objects.filter(pk=id).update(status=STATUS_All['FINISHED'])
            else:
                signature = Signature(**signature_data)
                signature.creator = creator
                signature.save()
                if signature_for == "CLIENT":
                    if not task.finished_at or task.finished_at is None:
                        Task.objects.filter(pk=id).update(finished_at=datetime.now())
                    Task.objects.filter(pk=id).update(client_signature=signature, status=STATUS_All['FINISHED'])
                    notification_data = {
                        "sender": creator,
                        "recipient": task.creator,
                        "notification_type": "TASK_FINISHED",
                        "title": "Une tâche finie",
                        "message": "Une tâche vient d'être finie.",
                        "task": task,
                    }
                    notify(notification_data)
                elif signature_for == "EMPLOYEE":
                    Task.objects.filter(pk=id).update(employee_signature=signature, status=STATUS_All['FINISHED'])
        except Exception as e:
            done = False
            success = False
            message = "Une erreur s'est produite."
        return SignTaskSummary(done=done, success=success, message=message)

class DeleteTask(graphene.Mutation):
    class Arguments:
        id = graphene.ID()

    task = graphene.Field(TaskType)
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
            task = Task.objects.get(pk=id)
            # delete_calendar_event_task(task=task)
            task.delete()
            deleted = True
            success = True
        else:
            message = "Vous n'êtes pas un Superuser."
        return DeleteTask(deleted=deleted, success=success, message=message, id=id)

#*************************************************************************#

class UpdateTaskChecklistItemStatus(graphene.Mutation):
    class Arguments:
        id = graphene.ID()
        status = graphene.String(required=False)

    task_checklist = graphene.Field(TaskChecklistItemType)
    done = graphene.Boolean()
    success = graphene.Boolean()
    message = graphene.String()

    def mutate(root, info, id, status=None):
        creator = info.context.user
        done = True
        success = True
        task_checklist = None
        message = ''
        try:
            if status and status is not None:
                TaskChecklistItem.objects.filter(pk=id).update(status=status)
            else:
                task_checklist = TaskChecklistItem.objects.get(pk=id)
                task_checklist.status = STATUS_All['NEW'] if task_checklist.status == STATUS_All['FINISHED'] else STATUS_All['FINISHED']
                task_checklist.save()
            task_checklist = TaskChecklistItem.objects.get(pk=id)
        except Exception as e:
            done = False
            success = False
            message = "Une erreur s'est produite."
        return UpdateTaskChecklistItemStatus(done=done, success=success, message=message, task_checklist=task_checklist)
#*************************************************************************#
#************************************************************************

class CreateTicket(graphene.Mutation):
    class Arguments:
        ticket_data = TicketInput(required=True)

    ticket = graphene.Field(TicketType)

    def mutate(root, info, ticket_data=None):
        creator = info.context.user
        establishment_ids = ticket_data.pop("establishments") if "establishments" in ticket_data else None
        task_actions = ticket_data.pop("actions")
        ticket = Ticket(**ticket_data)
        ticket.creator = creator
        ticket.company = creator.current_company if creator.current_company is not None else creator.company
        ticket.save()
        if establishment_ids and establishment_ids is not None:
            ticket.establishments.set(establishment_ids)
        folder = Folder.objects.create(name=str(ticket.id)+'_'+ticket.title,creator=creator)
        ticket.folder = folder
        if not ticket.employee:
            ticket.employee = creator.get_employee_in_company()
        for item in task_actions:
            employees_ids = item.pop("employees") if "employees" in item else None
            task_action = TaskAction(**item)
            task_action.ticket = ticket
            task_action.creator = creator
            task_action.company = ticket.company
            task_action.save()
            if employees_ids and employees_ids is not None:
                task_action.employees.set(employees_ids)

        ticket.save()
        return CreateTicket(ticket=ticket)

class UpdateTicket(graphene.Mutation):
    class Arguments:
        id = graphene.ID()
        ticket_data = TicketInput(required=True)

    ticket = graphene.Field(TicketType)

    def mutate(root, info, id, image=None, ticket_data=None):
        creator = info.context.user
        establishment_ids = ticket_data.pop("establishments") if "establishments" in ticket_data else None
        task_actions = ticket_data.pop("actions")
        Ticket.objects.filter(pk=id).update(**ticket_data)
        ticket = Ticket.objects.get(pk=id)
        if establishment_ids and establishment_ids is not None:
            ticket.establishments.set(establishment_ids)
        if not ticket.folder or ticket.folder is None:
            folder = Folder.objects.create(name=str(ticket.id)+'_'+ticket.title,creator=creator)
            Ticket.objects.filter(pk=id).update(folder=folder)
        if not ticket.employee:
            ticket.employee = creator.get_employee_in_company()
            ticket.save()
        task_action_ids = [item.id for item in task_actions if item.id is not None]
        TaskAction.objects.filter(ticket=ticket).exclude(id__in=task_action_ids).delete()
        for item in task_actions:
            employees_ids = item.pop("employees") if "employees" in item else None
            if id in item or 'id' in item:
                TaskAction.objects.filter(pk=item.id).update(**item)
                task_action = TaskAction.objects.get(pk=item.id)
            else:
                task_action = TaskAction(**item)
                task_action.ticket = ticket
                task_action.creator = creator
                task_action.company = ticket.company
                task_action.save()
            if employees_ids and employees_ids is not None:
                task_action.employees.set(employees_ids)

        return UpdateTicket(ticket=ticket)

class UpdateTicketFields(graphene.Mutation):
    class Arguments:
        id = graphene.ID()
        ticket_data = TicketInput(required=True)

    ticket = graphene.Field(TicketType)
    done = graphene.Boolean()
    success = graphene.Boolean()
    message = graphene.String()

    def mutate(root, info, id, ticket_data=None):
        creator = info.context.user
        done = True
        success = True
        ticket = None
        message = ''
        try:
            ticket = Ticket.objects.get(pk=id)
            Ticket.objects.filter(pk=id).update(**ticket_data)
            ticket.refresh_from_db()
        except Exception as e:
            done = False
            success = False
            ticket=None
            message = "Une erreur s'est produite."
        return UpdateTicketFields(done=done, success=success, message=message, ticket=ticket)

class DeleteTicket(graphene.Mutation):
    class Arguments:
        id = graphene.ID()

    ticket = graphene.Field(TicketType)
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
            ticket = Ticket.objects.get(pk=id)
            ticket.delete()
            deleted = True
            success = True
        else:
            message = "Vous n'êtes pas un Superuser."
        return DeleteTicket(deleted=deleted, success=success, message=message, id=id)

#************************************************************************

# ************************************************************************


class CreateTaskAction(graphene.Mutation):
    class Arguments:
        task_action_data = TaskActionInput(required=True)
        document = Upload(required=False)

    task_action = graphene.Field(TaskActionType)

    def mutate(root, info, document=None, task_action_data=None):
        creator = info.context.user
        employees_ids = task_action_data.pop("employees") if "employees" in task_action_data else None
        task_action = TaskAction(**task_action_data)
        task_action.creator = creator
        task_action.company = (
            creator.current_company
            if creator.current_company is not None
            else creator.company
        )
        if info.context.FILES:
            # file1 = info.context.FILES['1']
            if document and isinstance(document, UploadedFile):
                document_file = task_action.document
                if not document_file:
                    document_file = File()
                    document_file.creator = creator
                document_file.file = document
                document_file.save()
                task_action.document = document_file
        task_action.save()
        folder = Folder.objects.create(
            name=str(task_action.id) + "_", creator=creator
        )
        task_action.folder = folder
        task_action.save()
        if employees_ids and employees_ids is not None:
            task_action.employees.set(employees_ids)
        return CreateTaskAction(task_action=task_action)


class UpdateTaskAction(graphene.Mutation):
    class Arguments:
        id = graphene.ID()
        task_action_data = TaskActionInput(required=True)
        document = Upload(required=False)

    task_action = graphene.Field(TaskActionType)

    def mutate(root, info, id, document=None, task_action_data=None):
        creator = info.context.user
        employees_ids = task_action_data.pop("employees") if "employees" in task_action_data else None
        TaskAction.objects.filter(pk=id).update(**task_action_data)
        task_action = TaskAction.objects.get(pk=id)
        if not task_action.folder or task_action.folder is None:
            folder = Folder.objects.create(
                name=str(task_action.id) + "_", creator=creator
            )
            TaskAction.objects.filter(pk=id).update(folder=folder)
        if not document and task_action.document:
            document_file = task_action.document
            document_file.delete()
        if info.context.FILES:
            # file1 = info.context.FILES['1']
            if document and isinstance(document, UploadedFile):
                document_file = task_action.document
                if not document_file:
                    document_file = File()
                    document_file.creator = creator
                document_file.file = document
                document_file.save()
                task_action.document = document_file
            task_action.save()
        if employees_ids and employees_ids is not None:
            task_action.employees.set(employees_ids)
        return UpdateTaskAction(task_action=task_action)


class DeleteTaskAction(graphene.Mutation):
    class Arguments:
        id = graphene.ID()

    task_action = graphene.Field(TaskActionType)
    id = graphene.ID()
    deleted = graphene.Boolean()
    success = graphene.Boolean()
    message = graphene.String()

    def mutate(root, info, id):
        deleted = False
        success = False
        message = ""
        current_user = info.context.user
        if current_user.is_superuser:
            task_action = TaskAction.objects.get(pk=id)
            task_action.delete()
            deleted = True
            success = True
        else:
            message = "Vous n'êtes pas un Superuser."
        return DeleteTaskAction(deleted=deleted, success=success, message=message, id=id)


# *************************************************************************#

#*************************************************************************#
class WorksMutation(graphene.ObjectType):
    create_task = CreateTask.Field()
    update_task = UpdateTask.Field()
    update_task_fields = UpdateTaskFields.Field()
    update_task_state = UpdateTaskState.Field()
    delete_task = DeleteTask.Field()
    update_task_step = UpdateTaskStep.Field()
    sign_task_summary = SignTaskSummary.Field()
    update_task_checklist_item_status = UpdateTaskChecklistItemStatus.Field()

    create_ticket = CreateTicket.Field()
    update_ticket = UpdateTicket.Field()
    update_ticket_fields = UpdateTicketFields.Field()
    delete_ticket = DeleteTicket.Field()

    create_task_action = CreateTaskAction.Field()
    update_task_action = UpdateTaskAction.Field()
    delete_task_action = DeleteTaskAction.Field()