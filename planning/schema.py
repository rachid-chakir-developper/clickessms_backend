import graphene
from graphene_django import DjangoObjectType
from django.core.files.uploadedfile import InMemoryUploadedFile, UploadedFile
from graphql_jwt.decorators import login_required
from graphene_file_upload.scalars import Upload

from django.db.models import Q

from planning.models import EmployeeAbsence, EmployeeAbsenceItem
from data_management.models import AbsenceReason
from medias.models import Folder, File
from human_ressources.models import Employee

class EmployeeAbsenceItemType(DjangoObjectType):
    class Meta:
        model = EmployeeAbsenceItem
        fields = "__all__"

class EmployeeAbsenceType(DjangoObjectType):
    class Meta:
        model = EmployeeAbsence
        fields = "__all__"
    employees = graphene.List(EmployeeAbsenceItemType)
    def resolve_employees( instance, info, **kwargs ):
        return instance.employeeabsenceitem_set.all()

class EmployeeAbsenceNodeType(graphene.ObjectType):
    nodes = graphene.List(EmployeeAbsenceType)
    total_count = graphene.Int()

class EmployeeAbsenceFilterInput(graphene.InputObjectType):
    keyword = graphene.String(required=False)
    starting_date_time = graphene.DateTime(required=False)
    ending_date_time = graphene.DateTime(required=False)
    employees = graphene.List(graphene.Int, required=False)

class EmployeeAbsenceInput(graphene.InputObjectType):
    id = graphene.ID(required=False)
    number = graphene.String(required=False)
    title = graphene.String(required=False)
    starting_date_time = graphene.DateTime(required=False)
    ending_date_time = graphene.DateTime(required=False)
    comment = graphene.String(required=False)
    observation = graphene.String(required=False)
    employee_id = graphene.Int(name="employee", required=False)
    employees = graphene.List(graphene.Int, required=False)
    reasons = graphene.List(graphene.Int, required=False)
    other_reasons = graphene.String(required=False)

class PlanningQuery(graphene.ObjectType):
    employee_absences = graphene.Field(EmployeeAbsenceNodeType, employee_absence_filter= EmployeeAbsenceFilterInput(required=False), offset = graphene.Int(required=False), limit = graphene.Int(required=False), page = graphene.Int(required=False))
    employee_absence = graphene.Field(EmployeeAbsenceType, id = graphene.ID())

    def resolve_employee_absences(root, info, employee_absence_filter=None, offset=None, limit=None, page=None):
        # We can easily optimize query count in the resolve method
        user = info.context.user
        company = user.current_company if user.current_company is not None else user.company
        total_count = 0
        employee_absences = EmployeeAbsence.objects.filter(company=company)
        if employee_absence_filter:
            keyword = employee_absence_filter.get('keyword', '')
            starting_date_time = employee_absence_filter.get('starting_date_time')
            ending_date_time = employee_absence_filter.get('ending_date_time')
            employees = employee_absence_filter.get('employees')
            if employees:
                employee_absences = employee_absences.filter(employeeabsenceitem__employee__id__in=employees)
            if keyword:
                employee_absences = employee_absences.filter(Q(title__icontains=keyword) | Q(description__icontains=keyword))
            if starting_date_time:
                employee_absences = employee_absences.filter(starting_date_time__gte=starting_date_time)
            if ending_date_time:
                employee_absences = employee_absences.filter(starting_date_time__lte=ending_date_time)

        employee_absences = employee_absences.order_by('-created_at')
        total_count = employee_absences.count()
        if page:
            offset = limit * (page - 1)
        if offset is not None and limit is not None:
            employee_absences = employee_absences[offset:offset + limit]
        return EmployeeAbsenceNodeType(nodes=employee_absences, total_count=total_count)

    def resolve_employee_absence(root, info, id):
        # We can easily optimize query count in the resolve method
        try:
            employee_absence = EmployeeAbsence.objects.get(pk=id)
        except EmployeeAbsence.DoesNotExist:
            employee_absence = None
        return employee_absence

#************************************************************************

#************************************************************************

class CreateEmployeeAbsence(graphene.Mutation):
    class Arguments:
        employee_absence_data = EmployeeAbsenceInput(required=True)

    employee_absence = graphene.Field(EmployeeAbsenceType)

    def mutate(root, info, employee_absence_data=None):
        creator = info.context.user
        employee_ids = employee_absence_data.pop("employees")
        reason_ids = employee_absence_data.pop("reasons")
        employee_absence = EmployeeAbsence(**employee_absence_data)
        employee_absence.creator = creator
        employee_absence.company = creator.current_company if creator.current_company is not None else creator.company
        folder = Folder.objects.create(name=str(employee_absence.id)+'_'+employee_absence.title,creator=creator)
        employee_absence.folder = folder
        employee_absence.save()
        if not employee_absence.employee:
            employee_absence.employee = creator.getEmployeeInCompany()
        if reason_ids and reason_ids is not None:
            reasons = AbsenceReason.objects.filter(id__in=reason_ids)
            employee_absence.reasons.set(reasons)
        employees = Employee.objects.filter(id__in=employee_ids)
        for employee in employees:
            try:
                employee_absence_items = EmployeeAbsenceItem.objects.get(employee__id=employee.id, employee_absence__id=employee_absence.id)
            except EmployeeAbsenceItem.DoesNotExist:
                EmployeeAbsenceItem.objects.create(
                        employee_absence=employee_absence,
                        employee=employee,
                        creator=creator
                    )
        employee_absence.save()
        return CreateEmployeeAbsence(employee_absence=employee_absence)

class UpdateEmployeeAbsence(graphene.Mutation):
    class Arguments:
        id = graphene.ID()
        employee_absence_data = EmployeeAbsenceInput(required=True)

    employee_absence = graphene.Field(EmployeeAbsenceType)

    def mutate(root, info, id, image=None, employee_absence_data=None):
        creator = info.context.user
        employee_ids = employee_absence_data.pop("employees")
        reason_ids = employee_absence_data.pop("reasons")
        EmployeeAbsence.objects.filter(pk=id).update(**employee_absence_data)
        employee_absence = EmployeeAbsence.objects.get(pk=id)
        if not employee_absence.folder or employee_absence.folder is None:
            folder = Folder.objects.create(name=str(employee_absence.id)+'_'+employee_absence.title,creator=creator)
            EmployeeAbsence.objects.filter(pk=id).update(folder=folder)
        if not employee_absence.employee:
            employee_absence.employee = creator.getEmployeeInCompany()
            employee_absence.save()

        if reason_ids and reason_ids is not None:
            reasons = AbsenceReason.objects.filter(id__in=reason_ids)
            employee_absence.reasons.set(reasons)

        EmployeeAbsenceItem.objects.filter(employee_absence=employee_absence).exclude(employee__id__in=employee_ids).delete()
        employees = Employee.objects.filter(id__in=employee_ids)
        for employee in employees:
            try:
                employee_absence_items = EmployeeAbsenceItem.objects.get(employee__id=employee.id, employee_absence__id=employee_absence.id)
            except EmployeeAbsenceItem.DoesNotExist:
                EmployeeAbsenceItem.objects.create(
                        employee_absence=employee_absence,
                        employee=employee,
                        creator=creator
                    )
        return UpdateEmployeeAbsence(employee_absence=employee_absence)

class DeleteEmployeeAbsence(graphene.Mutation):
    class Arguments:
        id = graphene.ID()

    employee_absence = graphene.Field(EmployeeAbsenceType)
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
            employee_absence = EmployeeAbsence.objects.get(pk=id)
            employee_absence.delete()
            deleted = True
            success = True
        else:
            message = "Vous n'êtes pas un Superuser."
        return DeleteEmployeeAbsence(deleted=deleted, success=success, message=message, id=id)
        
#*************************************************************************#
class PlanningMutation(graphene.ObjectType):
    create_employee_absence = CreateEmployeeAbsence.Field()
    update_employee_absence = UpdateEmployeeAbsence.Field()
    delete_employee_absence = DeleteEmployeeAbsence.Field()