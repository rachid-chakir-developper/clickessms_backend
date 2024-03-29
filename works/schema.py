import graphene
from graphene_django import DjangoObjectType
from django.core.files.uploadedfile import InMemoryUploadedFile, UploadedFile
from graphql_jwt.decorators import login_required
from graphene_file_upload.scalars import Upload
from datetime import date, datetime, time

from django.db.models import Q

from works.models import Task, TaskWorker, TaskMaterial, TaskVehicle, TaskChecklistItem, TaskStep, STEP_TYPES_LABELS, STEP_TYPES_ALL, STATUS_All
from human_ressources.models import Employee
from vehicles.models import Vehicle
from stocks.models import Material
from medias.models import Folder, File
from feedbacks.models import Comment, Signature
from notifications.notificator import notify, push_notification_to_employees
from feedbacks.google_calendar import create_calendar_event_task, update_calendar_event_task, delete_calendar_event_task

from feedbacks.schema import SignatureInput

class TaskChecklistItemType(DjangoObjectType):
    class Meta:
        model = TaskChecklistItem
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
    image = graphene.String()
    task_checklist = graphene.List(TaskChecklistItemType)
    workers = graphene.List(TaskWorkerType)
    vehicles = graphene.List(TaskVehicleType)
    materials = graphene.List(TaskMaterialType)
    task_steps = graphene.List(TaskStepType)
    def resolve_image( instance, info, **kwargs ):
        return instance.image and info.context.build_absolute_uri(instance.image.image.url)
    def resolve_task_checklist( instance, info, **kwargs ):
        return instance.taskchecklistitem_set.all()
    def resolve_workers( instance, info, **kwargs ):
        return instance.taskworker_set.all()
    def resolve_vehicles( instance, info, **kwargs ):
        return instance.taskvehicle_set.all()
    def resolve_materials( instance, info, **kwargs ):
        return instance.taskmaterial_set.all()
    def resolve_task_steps( instance, info, **kwargs ):
        return instance.taskstep_set.all()

class TaskNodeType(graphene.ObjectType):
    nodes = graphene.List(TaskType)
    total_count = graphene.Int()

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
    name = graphene.String(required=True)
    starting_date_time = graphene.DateTime(required=False)
    ending_date_time = graphene.DateTime(required=False)
    estimated_budget = graphene.Float(required=False)
    latitude = graphene.String(required=False)
    longitude = graphene.String(required=False)
    city = graphene.String(required=False)
    country = graphene.String(required=False)
    zip_code = graphene.String(required=False)
    address = graphene.String(required=False)
    # client infos start
    client_name = graphene.String(required=False)
    client_task_number = graphene.String(required=False)
    email = graphene.String(required=False)
    mobile = graphene.String(required=False)
    fix = graphene.String(required=False)
    billing_address = graphene.String(required=False)
    site_owner_name = graphene.String(required=False)
    site_tenant_name = graphene.String(required=False)
    # ****************************
    # contractor infos start
    contractor_name = graphene.String(required=False)
    contractor_tel = graphene.String(required=False)
    contractor_email = graphene.String(required=False)
    # ****************************
    # receiver infos start
    receiver_name = graphene.String(required=False)
    receiver_tel = graphene.String(required=False)
    receiver_email = graphene.String(required=False)
    # ****************************
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
    total_price_ht = graphene.Float(required=False)
    tva = graphene.Float(required=False)
    discount = graphene.Float(required=False)
    total_price_ttc = graphene.Float(required=False)
    is_display_price = graphene.Boolean(required=False)
    is_from_quote = graphene.Boolean(required=False)
    is_active = graphene.Boolean(required=False)
    status = graphene.String(required=False)
    client_id = graphene.Int(name="client", required=False)
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

    def resolve_tasks(root, info, task_filter=None, offset=None, limit=None, page=None):
        # We can easily optimize query count in the resolve method
        total_count = 0
        tasks = Task.objects.all()
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

#************************************************************************

class CreateTask(graphene.Mutation):
    class Arguments:
        task_data = TaskInput(required=True)
        image = Upload(required=False)

    task = graphene.Field(TaskType)

    def mutate(root, info, image=None, task_data=None):
        creator = info.context.user
        worker_ids = task_data.pop("workers")
        vehicle_ids = task_data.pop("vehicles")
        material_ids = task_data.pop("materials")
        task_checklist = task_data.pop("task_checklist")
        task = Task(**task_data)
        task.creator = creator
        if info.context.FILES:
            # file1 = info.context.FILES['1']
            if image and isinstance(image, UploadedFile):
                image_file = task.image
                if not image_file:
                    image_file = File()
                    image_file.creator = creator
                image_file.image = image
                image_file.save()
                task.image = image_file
        task.calculer_total_ttc()
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
        image = Upload(required=False)

    task = graphene.Field(TaskType)

    def mutate(root, info, id, image=None, task_data=None):
        creator = info.context.user
        worker_ids = task_data.pop("workers")
        vehicle_ids = task_data.pop("vehicles")
        material_ids = task_data.pop("materials")
        task_checklist = task_data.pop("task_checklist")
        Task.objects.filter(pk=id).update(**task_data)
        task = Task.objects.get(pk=id)
        task.calculer_total_ttc()
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
        if not image and task.image:
            image_file = task.image
            image_file.delete()
        if info.context.FILES:
            # file1 = info.context.FILES['1']
            if image and isinstance(image, UploadedFile):
                image_file = task.image
                if not image_file:
                    image_file = File()
                    image_file.creator = creator
                image_file.image = image
                image_file.save()
                task.image = image_file
            task.save()
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
        task_fields = TaskFieldInput(required=False)

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
            Task.objects.filter(pk=id).update(**task_fields)
            task = Task.objects.get(pk=id)
        except Exception as e:
            done = False
            success = False
            message = "Une erreur s'est produite."
        return UpdateTaskFields(done=done, success=success, message=message,task=task)

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
class WorksMutation(graphene.ObjectType):
    create_task = CreateTask.Field()
    update_task = UpdateTask.Field()
    update_task_fields = UpdateTaskFields.Field()
    update_task_state = UpdateTaskState.Field()
    delete_task = DeleteTask.Field()
    update_task_step = UpdateTaskStep.Field()
    sign_task_summary = SignTaskSummary.Field()
    update_task_checklist_item_status = UpdateTaskChecklistItemStatus.Field()