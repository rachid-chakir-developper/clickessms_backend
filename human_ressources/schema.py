import graphene
from graphene_django import DjangoObjectType
from django.core.files.uploadedfile import InMemoryUploadedFile, UploadedFile
from graphql_jwt.decorators import login_required
from graphene_file_upload.scalars import Upload

from django.db.models import Q

from human_ressources.models import Employee, EmployeeGroup, EmployeeGroupItem, Beneficiary, BeneficiaryGroup, BeneficiaryGroupItem
from medias.models import Folder, File

class EmployeeType(DjangoObjectType):
    class Meta:
        model = Employee
        fields = "__all__"
    photo = graphene.String()
    cover_image = graphene.String()
    def resolve_photo( instance, info, **kwargs ):
        return instance.photo and info.context.build_absolute_uri(instance.photo.image.url)
    def resolve_cover_image( instance, info, **kwargs ):
        return instance.cover_image and info.context.build_absolute_uri(instance.cover_image.image.url)

class EmployeeNodeType(graphene.ObjectType):
    nodes = graphene.List(EmployeeType)
    total_count = graphene.Int()

class EmployeeFilterInput(graphene.InputObjectType):
    keyword = graphene.String(required=False)
    starting_date_time = graphene.DateTime(required=False)
    ending_date_time = graphene.DateTime(required=False)


class EmployeeGroupItemType(DjangoObjectType):
    class Meta:
        model = EmployeeGroupItem
        fields = "__all__"

class EmployeeGroupType(DjangoObjectType):
    class Meta:
        model = EmployeeGroup
        fields = "__all__"
    image = graphene.String()
    employees = graphene.List(EmployeeGroupItemType)
    def resolve_image( instance, info, **kwargs ):
        return instance.image and info.context.build_absolute_uri(instance.image.image.url)
    def resolve_employees( instance, info, **kwargs ):
        return instance.employee_group_items.all()

class EmployeeGroupNodeType(graphene.ObjectType):
    nodes = graphene.List(EmployeeGroupType)
    total_count = graphene.Int()

class EmployeeGroupFilterInput(graphene.InputObjectType):
    keyword = graphene.String(required=False)
    starting_date_time = graphene.DateTime(required=False)
    ending_date_time = graphene.DateTime(required=False)

class BeneficiaryType(DjangoObjectType):
    class Meta:
        model = Beneficiary
        fields = "__all__"
    photo = graphene.String()
    cover_image = graphene.String()
    def resolve_photo( instance, info, **kwargs ):
        return instance.photo and info.context.build_absolute_uri(instance.photo.image.url)
    def resolve_cover_image( instance, info, **kwargs ):
        return instance.cover_image and info.context.build_absolute_uri(instance.cover_image.image.url)

class BeneficiaryNodeType(graphene.ObjectType):
    nodes = graphene.List(BeneficiaryType)
    total_count = graphene.Int()

class BeneficiaryFilterInput(graphene.InputObjectType):
    keyword = graphene.String(required=False)
    starting_date_time = graphene.DateTime(required=False)
    ending_date_time = graphene.DateTime(required=False)

class BeneficiaryGroupItemType(DjangoObjectType):
    class Meta:
        model = BeneficiaryGroupItem
        fields = "__all__"

class BeneficiaryGroupType(DjangoObjectType):
    class Meta:
        model = BeneficiaryGroup
        fields = "__all__"
    image = graphene.String()
    beneficiaries = graphene.List(BeneficiaryGroupItemType)
    def resolve_image( instance, info, **kwargs ):
        return instance.image and info.context.build_absolute_uri(instance.image.image.url)
    def resolve_beneficiaries( instance, info, **kwargs ):
        return instance.beneficiary_group_items.all()

class BeneficiaryGroupNodeType(graphene.ObjectType):
    nodes = graphene.List(BeneficiaryGroupType)
    total_count = graphene.Int()

class BeneficiaryGroupFilterInput(graphene.InputObjectType):
    keyword = graphene.String(required=False)
    starting_date_time = graphene.DateTime(required=False)
    ending_date_time = graphene.DateTime(required=False)

class EmployeeInput(graphene.InputObjectType):
    id = graphene.ID(required=False)
    number = graphene.String(required=False)
    first_name = graphene.String(required=True)
    last_name = graphene.String(required=True)
    email = graphene.String(required=True)
    birth_date = graphene.DateTime(required=False)
    hiring_date = graphene.DateTime(required=False)
    probation_end_date = graphene.DateTime(required=False)
    work_end_date = graphene.DateTime(required=False)
    starting_salary = graphene.Float(required=True)
    latitude = graphene.String(required=False)
    longitude = graphene.String(required=False)
    city = graphene.String(required=False)
    country = graphene.String(required=False)
    zip_code = graphene.String(required=False)
    address = graphene.String(required=False)
    mobile = graphene.String(required=False)
    fix = graphene.String(required=False)
    fax = graphene.String(required=False)
    position = graphene.String(required=False)
    web_site = graphene.String(required=False)
    other_contacts = graphene.String(required=False)
    iban = graphene.String(required=False)
    bic = graphene.String(required=False)
    bank_name = graphene.String(required=False)
    is_active = graphene.Boolean(required=False)
    description = graphene.String(required=False)
    observation = graphene.String(required=False)

class EmployeeGroupInput(graphene.InputObjectType):
    id = graphene.ID(required=False)
    number = graphene.String(required=False)
    name = graphene.String(required=True)
    is_active = graphene.Boolean(required=False)
    description = graphene.String(required=False)
    observation = graphene.String(required=False)
    employees = graphene.List(graphene.Int, required=False)

class BeneficiaryInput(graphene.InputObjectType):
    id = graphene.ID(required=False)
    number = graphene.String(required=False)
    first_name = graphene.String(required=True)
    last_name = graphene.String(required=True)
    email = graphene.String(required=True)
    birth_date = graphene.DateTime(required=False)
    latitude = graphene.String(required=False)
    longitude = graphene.String(required=False)
    city = graphene.String(required=False)
    country = graphene.String(required=False)
    zip_code = graphene.String(required=False)
    address = graphene.String(required=False)
    mobile = graphene.String(required=False)
    fix = graphene.String(required=False)
    fax = graphene.String(required=False)
    web_site = graphene.String(required=False)
    other_contacts = graphene.String(required=False)
    iban = graphene.String(required=False)
    bic = graphene.String(required=False)
    bank_name = graphene.String(required=False)
    is_active = graphene.Boolean(required=False)
    description = graphene.String(required=False)
    observation = graphene.String(required=False)

class BeneficiaryGroupInput(graphene.InputObjectType):
    id = graphene.ID(required=False)
    number = graphene.String(required=False)
    name = graphene.String(required=True)
    is_active = graphene.Boolean(required=False)
    description = graphene.String(required=False)
    observation = graphene.String(required=False)
    beneficiaries = graphene.List(graphene.Int, required=False)

class HumanRessourcesQuery(graphene.ObjectType):
    employees = graphene.Field(EmployeeNodeType, employee_filter= EmployeeFilterInput(required=False), id_company = graphene.ID(required=False), offset = graphene.Int(required=False), limit = graphene.Int(required=False), page = graphene.Int(required=False))
    employee = graphene.Field(EmployeeType, id = graphene.ID())
    employee_groups = graphene.Field(EmployeeGroupNodeType, employee_group_filter= EmployeeGroupFilterInput(required=False), offset = graphene.Int(required=False), limit = graphene.Int(required=False), page = graphene.Int(required=False))
    employee_group = graphene.Field(EmployeeGroupType, id = graphene.ID())
    beneficiaries = graphene.Field(BeneficiaryNodeType, beneficiary_filter= BeneficiaryFilterInput(required=False), id_company = graphene.ID(required=False), offset = graphene.Int(required=False), limit = graphene.Int(required=False), page = graphene.Int(required=False))
    beneficiary = graphene.Field(BeneficiaryType, id = graphene.ID())
    beneficiary_groups = graphene.Field(BeneficiaryGroupNodeType, beneficiary_group_filter= BeneficiaryGroupFilterInput(required=False), offset = graphene.Int(required=False), limit = graphene.Int(required=False), page = graphene.Int(required=False))
    beneficiary_group = graphene.Field(BeneficiaryGroupType, id = graphene.ID())
    def resolve_employees(root, info, employee_filter=None, id_company=None, offset=None, limit=None, page=None):
        # We can easily optimize query count in the resolve method
        total_count = 0
        employees = Employee.objects.filter(company__id=id_company) if id_company else Employee.objects.all()
        if employee_filter:
            keyword = employee_filter.get('keyword', '')
            starting_date_time = employee_filter.get('starting_date_time')
            ending_date_time = employee_filter.get('ending_date_time')
            if keyword:
                employees = employees.filter(Q(first_name__icontains=keyword) | Q(last_name__icontains=keyword) | Q(email__icontains=keyword))
            if starting_date_time:
                employees = employees.filter(created_at__gte=starting_date_time)
            if ending_date_time:
                employees = employees.filter(created_at__lte=ending_date_time)
        employees = employees.order_by('-created_at')
        total_count = employees.count()
        if page:
            offset = limit * (page - 1)
        if offset is not None and limit is not None:
            employees = employees[offset:offset + limit]
        return EmployeeNodeType(nodes=employees, total_count=total_count)

    def resolve_employee(root, info, id):
        # We can easily optimize query count in the resolve method
        try:
            employee = Employee.objects.get(pk=id)
        except Employee.DoesNotExist:
            employee = None
        return employee

    def resolve_employee_groups(root, info, employee_group_filter=None, offset=None, limit=None, page=None):
        # We can easily optimize query count in the resolve method
        total_count = 0
        employee_groups = EmployeeGroup.objects.all()
        if employee_group_filter:
            keyword = employee_group_filter.get('keyword', '')
            starting_date_time = employee_group_filter.get('starting_date_time')
            ending_date_time = employee_group_filter.get('ending_date_time')
            if keyword:
                employee_groups = employee_groups.filter(Q(title__icontains=keyword))
            if starting_date_time:
                employee_groups = employee_groups.filter(created_at__gte=starting_date_time)
            if ending_date_time:
                employee_groups = employee_groups.filter(created_at__lte=ending_date_time)
        employee_groups = employee_groups.order_by('-created_at')
        total_count = employee_groups.count()
        if page:
            offset = limit * (page - 1)
        if offset is not None and limit is not None:
            employee_groups = employee_groups[offset:offset + limit]
        return EmployeeGroupNodeType(nodes=employee_groups, total_count=total_count)

    def resolve_employee_group(root, info, id):
        # We can easily optimize query count in the resolve method
        try:
            employee_group = EmployeeGroup.objects.get(pk=id)
        except EmployeeGroup.DoesNotExist:
            employee_group = None
        return employee_group

    def resolve_beneficiaries(root, info, beneficiary_filter=None, id_company=None, offset=None, limit=None, page=None):
        # We can easily optimize query count in the resolve method
        total_count = 0
        beneficiaries = Beneficiary.objects.filter(company__id=id_company) if id_company else Beneficiary.objects.all()
        if beneficiary_filter:
            keyword = beneficiary_filter.get('keyword', '')
            starting_date_time = beneficiary_filter.get('starting_date_time')
            ending_date_time = beneficiary_filter.get('ending_date_time')
            if keyword:
                beneficiaries = beneficiaries.filter(Q(first_name__icontains=keyword) | Q(last_name__icontains=keyword) | Q(email__icontains=keyword))
            if starting_date_time:
                beneficiaries = beneficiaries.filter(created_at__gte=starting_date_time)
            if ending_date_time:
                beneficiaries = beneficiaries.filter(created_at__lte=ending_date_time)
        beneficiaries = beneficiaries.order_by('-created_at')
        total_count = beneficiaries.count()
        if page:
            offset = limit * (page - 1)
        if offset is not None and limit is not None:
            beneficiaries = beneficiaries[offset:offset + limit]
        return BeneficiaryNodeType(nodes=beneficiaries, total_count=total_count)

    def resolve_beneficiary(root, info, id):
        # We can easily optimize query count in the resolve method
        try:
            beneficiary = Beneficiary.objects.get(pk=id)
        except Beneficiary.DoesNotExist:
            beneficiary = None
        return beneficiary

    def resolve_beneficiary_groups(root, info, beneficiary_group_filter=None, offset=None, limit=None, page=None):
        # We can easily optimize query count in the resolve method
        total_count = 0
        beneficiary_groups = BeneficiaryGroup.objects.all()
        if beneficiary_group_filter:
            keyword = beneficiary_group_filter.get('keyword', '')
            starting_date_time = beneficiary_group_filter.get('starting_date_time')
            ending_date_time = beneficiary_group_filter.get('ending_date_time')
            if keyword:
                beneficiary_groups = beneficiary_groups.filter(Q(title__icontains=keyword))
            if starting_date_time:
                beneficiary_groups = beneficiary_groups.filter(created_at__gte=starting_date_time)
            if ending_date_time:
                beneficiary_groups = beneficiary_groups.filter(created_at__lte=ending_date_time)
        beneficiary_groups = beneficiary_groups.order_by('-created_at')
        total_count = beneficiary_groups.count()
        if page:
            offset = limit * (page - 1)
        if offset is not None and limit is not None:
            beneficiary_groups = beneficiary_groups[offset:offset + limit]
        return BeneficiaryGroupNodeType(nodes=beneficiary_groups, total_count=total_count)

    def resolve_beneficiary_group(root, info, id):
        # We can easily optimize query count in the resolve method
        try:
            beneficiary_group = BeneficiaryGroup.objects.get(pk=id)
        except BeneficiaryGroup.DoesNotExist:
            beneficiary_group = None
        return beneficiary_group

class CreateEmployee(graphene.Mutation):
    class Arguments:
        employee_data = EmployeeInput(required=True)
        photo = Upload(required=False)
        cover_image = Upload(required=False)

    employee = graphene.Field(EmployeeType)

    def mutate(root, info, photo=None, cover_image=None,  employee_data=None):
        creator = info.context.user
        employee = Employee(**employee_data)
        employee.creator = creator
        employee.company = creator.company
        if info.context.FILES:
            # file1 = info.context.FILES['1']
            if photo and isinstance(photo, UploadedFile):
                photo_file = employee.photo
                if not photo_file:
                    photo_file = File()
                    photo_file.creator = creator
                photo_file.image = photo
                photo_file.save()
                employee.photo = photo_file
            # file2 = info.context.FILES['2']
            if cover_image and isinstance(cover_image, UploadedFile):
                cover_image_file = employee.cover_image
                if not cover_image_file:
                    cover_image_file = File()
                    cover_image_file.creator = creator
                cover_image_file.image = cover_image
                cover_image_file.save()
                employee.cover_image = cover_image_file
        employee.save()
        folder = Folder.objects.create(name=str(employee.id)+'_'+employee.first_name+'-'+employee.last_name,creator=creator)
        employee.folder = folder
        employee.save()
        return CreateEmployee(employee=employee)

class UpdateEmployee(graphene.Mutation):
    class Arguments:
        id = graphene.ID()
        employee_data = EmployeeInput(required=True)
        photo = Upload(required=False)
        cover_image = Upload(required=False)

    employee = graphene.Field(EmployeeType)

    def mutate(root, info, id, photo=None, cover_image=None,  employee_data=None):
        creator = info.context.user
        Employee.objects.filter(pk=id).update(**employee_data)
        employee = Employee.objects.get(pk=id)
        if not employee.folder or employee.folder is None:
            folder = Folder.objects.create(name=str(employee.id)+'_'+employee.first_name+'-'+employee.last_name,creator=creator)
            Employee.objects.filter(pk=id).update(folder=folder)
        if not photo and employee.photo:
            photo_file = employee.photo
            photo_file.delete()
        if not cover_image and employee.cover_image:
            cover_image_file = employee.cover_image
            cover_image_file.delete()
        if info.context.FILES:
            # file1 = info.context.FILES['1']
            if photo and isinstance(photo, UploadedFile):
                photo_file = employee.photo
                if not photo_file:
                    photo_file = File()
                    photo_file.creator = creator
                photo_file.image = photo
                photo_file.save()
                employee.photo = photo_file
            # file2 = info.context.FILES['2']
            if cover_image and isinstance(cover_image, UploadedFile):
                cover_image_file = employee.cover_image
                if not cover_image_file:
                    cover_image_file = File()
                    cover_image_file.creator = creator
                cover_image_file.image = cover_image
                cover_image_file.save()
                employee.cover_image = cover_image_file
            employee.save()
        employee = Employee.objects.get(pk=id)
        return UpdateEmployee(employee=employee)

class UpdateEmployeeState(graphene.Mutation):
    class Arguments:
        id = graphene.ID()

    employee = graphene.Field(EmployeeType)
    done = graphene.Boolean()
    success = graphene.Boolean()
    message = graphene.String()

    def mutate(root, info, id, employee_fields=None):
        creator = info.context.user
        done = True
        success = True
        employee = None
        message = ''
        try:
            employee = Employee.objects.get(pk=id)
            Employee.objects.filter(pk=id).update(is_active=not employee.is_active)
            employee.refresh_from_db()
        except Exception as e:
            done = False
            success = False
            employee=None
            message = "Une erreur s'est produite."
        return UpdateEmployeeState(done=done, success=success, message=message,employee=employee)

class DeleteEmployee(graphene.Mutation):
    class Arguments:
        id = graphene.ID()

    employee = graphene.Field(EmployeeType)
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
            employee = Employee.objects.get(pk=id)
            employee.delete()
            deleted = True
            success = True
        else:
            message = "Vous n'êtes pas un Superuser."
        return DeleteEmployee(deleted=deleted, success=success, message=message, id=id)

#************************************************************************

class CreateEmployeeGroup(graphene.Mutation):
    class Arguments:
        employee_group_data = EmployeeGroupInput(required=True)
        image = Upload(required=False)

    employee_group = graphene.Field(EmployeeGroupType)

    def mutate(root, info, image=None, employee_group_data=None):
        creator = info.context.user
        employee_ids = employee_group_data.pop("employees")
        employee_group = EmployeeGroup(**employee_group_data)
        employee_group.creator = creator
        if info.context.FILES:
            # file1 = info.context.FILES['1']
            if image and isinstance(image, UploadedFile):
                image_file = employee_group.image
                if not image_file:
                    image_file = File()
                    image_file.creator = creator
                image_file.image = image
                image_file.save()
                employee_group.image = image_file
        employee_group.save()
        folder = Folder.objects.create(name=str(employee_group.id)+'_'+employee_group.name,creator=creator)
        employee_group.folder = folder
        employees = Employee.objects.filter(id__in=employee_ids)
        for employee in employees:
            try:
                employee_group_item = EmployeeGroupItem.objects.get(employee__id=employee.id, employee_group__id=employee_group.id)
            except EmployeeGroupItem.DoesNotExist:
                EmployeeGroupItem.objects.create(
                        employee_group=employee_group,
                        employee=employee,
                        creator=creator
                    )
        employee_group.save()
        return CreateEmployeeGroup(employee_group=employee_group)

class UpdateEmployeeGroup(graphene.Mutation):
    class Arguments:
        id = graphene.ID()
        employee_group_data = EmployeeGroupInput(required=True)
        image = Upload(required=False)

    employee_group = graphene.Field(EmployeeGroupType)

    def mutate(root, info, id, image=None, employee_group_data=None):
        creator = info.context.user
        employee_ids = employee_group_data.pop("employees")
        EmployeeGroup.objects.filter(pk=id).update(**employee_group_data)
        employee_group = EmployeeGroup.objects.get(pk=id)
        if not employee_group.folder or employee_group.folder is None:
            folder = Folder.objects.create(name=str(employee_group.id)+'_'+employee_group.name,creator=creator)
            EmployeeGroup.objects.filter(pk=id).update(folder=folder)
        if not image and employee_group.image:
            image_file = employee_group.image
            image_file.delete()
        if info.context.FILES:
            # file1 = info.context.FILES['1']
            if image and isinstance(image, UploadedFile):
                image_file = employee_group.image
                if not image_file:
                    image_file = File()
                    image_file.creator = creator
                image_file.image = image
                image_file.save()
                employee_group.image = image_file
            employee_group.save()
        EmployeeGroupItem.objects.filter(employee_group=employee_group).exclude(employee__id__in=employee_ids).delete()
        employees = Employee.objects.filter(id__in=employee_ids)
        for employee in employees:
            try:
                employee_group_item = EmployeeGroupItem.objects.get(employee__id=employee.id, employee_group__id=employee_group.id)
            except EmployeeGroupItem.DoesNotExist:
                EmployeeGroupItem.objects.create(
                        employee_group=employee_group,
                        employee=employee,
                        creator=creator
                    )
        return UpdateEmployeeGroup(employee_group=employee_group)

class UpdateEmployeeGroupState(graphene.Mutation):
    class Arguments:
        id = graphene.ID()

    employee_group = graphene.Field(EmployeeGroupType)
    done = graphene.Boolean()
    success = graphene.Boolean()
    message = graphene.String()

    def mutate(root, info, id, employee_group_fields=None):
        creator = info.context.user
        done = True
        success = True
        employee_group = None
        message = ''
        try:
            employee_group = EmployeeGroup.objects.get(pk=id)
            EmployeeGroup.objects.filter(pk=id).update(is_active=not employee_group.is_active)
            employee_group.refresh_from_db()
        except Exception as e:
            done = False
            success = False
            employee_group=None
            message = "Une erreur s'est produite."
        return UpdateEmployeeGroupState(done=done, success=success, message=message,employee_group=employee_group)


class DeleteEmployeeGroup(graphene.Mutation):
    class Arguments:
        id = graphene.ID()

    employee_group = graphene.Field(EmployeeGroupType)
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
            employee_group = EmployeeGroup.objects.get(pk=id)
            employee_group.delete()
            deleted = True
            success = True
        else:
            message = "Vous n'êtes pas un Superuser."
        return DeleteEmployeeGroup(deleted=deleted, success=success, message=message, id=id)

#************************************************************************
#********************************************************************************************************

class CreateBeneficiary(graphene.Mutation):
    class Arguments:
        beneficiary_data = BeneficiaryInput(required=True)
        photo = Upload(required=False)
        cover_image = Upload(required=False)

    beneficiary = graphene.Field(BeneficiaryType)

    def mutate(root, info, photo=None, cover_image=None,  beneficiary_data=None):
        creator = info.context.user
        beneficiary = Beneficiary(**beneficiary_data)
        beneficiary.creator = creator
        beneficiary.company = creator.company
        if info.context.FILES:
            # file1 = info.context.FILES['1']
            if photo and isinstance(photo, UploadedFile):
                photo_file = beneficiary.photo
                if not photo_file:
                    photo_file = File()
                    photo_file.creator = creator
                photo_file.image = photo
                photo_file.save()
                beneficiary.photo = photo_file
            # file2 = info.context.FILES['2']
            if cover_image and isinstance(cover_image, UploadedFile):
                cover_image_file = beneficiary.cover_image
                if not cover_image_file:
                    cover_image_file = File()
                    cover_image_file.creator = creator
                cover_image_file.image = cover_image
                cover_image_file.save()
                beneficiary.cover_image = cover_image_file
        beneficiary.save()
        folder = Folder.objects.create(name=str(beneficiary.id)+'_'+beneficiary.first_name+'-'+beneficiary.last_name,creator=creator)
        beneficiary.folder = folder
        beneficiary.save()
        return CreateBeneficiary(beneficiary=beneficiary)

class UpdateBeneficiary(graphene.Mutation):
    class Arguments:
        id = graphene.ID()
        beneficiary_data = BeneficiaryInput(required=True)
        photo = Upload(required=False)
        cover_image = Upload(required=False)

    beneficiary = graphene.Field(BeneficiaryType)

    def mutate(root, info, id, photo=None, cover_image=None,  beneficiary_data=None):
        creator = info.context.user
        Beneficiary.objects.filter(pk=id).update(**beneficiary_data)
        beneficiary = Beneficiary.objects.get(pk=id)
        if not beneficiary.folder or beneficiary.folder is None:
            folder = Folder.objects.create(name=str(beneficiary.id)+'_'+beneficiary.first_name+'-'+beneficiary.last_name,creator=creator)
            Beneficiary.objects.filter(pk=id).update(folder=folder)
        if not photo and beneficiary.photo:
            photo_file = beneficiary.photo
            photo_file.delete()
        if not cover_image and beneficiary.cover_image:
            cover_image_file = beneficiary.cover_image
            cover_image_file.delete()
        if info.context.FILES:
            # file1 = info.context.FILES['1']
            if photo and isinstance(photo, UploadedFile):
                photo_file = beneficiary.photo
                if not photo_file:
                    photo_file = File()
                    photo_file.creator = creator
                photo_file.image = photo
                photo_file.save()
                beneficiary.photo = photo_file
            # file2 = info.context.FILES['2']
            if cover_image and isinstance(cover_image, UploadedFile):
                cover_image_file = beneficiary.cover_image
                if not cover_image_file:
                    cover_image_file = File()
                    cover_image_file.creator = creator
                cover_image_file.image = cover_image
                cover_image_file.save()
                beneficiary.cover_image = cover_image_file
            beneficiary.save()
        beneficiary = Beneficiary.objects.get(pk=id)
        return UpdateBeneficiary(beneficiary=beneficiary)

class UpdateBeneficiaryState(graphene.Mutation):
    class Arguments:
        id = graphene.ID()

    beneficiary = graphene.Field(BeneficiaryType)
    done = graphene.Boolean()
    success = graphene.Boolean()
    message = graphene.String()

    def mutate(root, info, id, beneficiary_fields=None):
        creator = info.context.user
        done = True
        success = True
        beneficiary = None
        message = ''
        try:
            beneficiary = Beneficiary.objects.get(pk=id)
            Beneficiary.objects.filter(pk=id).update(is_active=not beneficiary.is_active)
            beneficiary.refresh_from_db()
        except Exception as e:
            done = False
            success = False
            beneficiary=None
            message = "Une erreur s'est produite."
        return UpdateBeneficiaryState(done=done, success=success, message=message,beneficiary=beneficiary)

class DeleteBeneficiary(graphene.Mutation):
    class Arguments:
        id = graphene.ID()

    beneficiary = graphene.Field(BeneficiaryType)
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
            beneficiary = Beneficiary.objects.get(pk=id)
            beneficiary.delete()
            deleted = True
            success = True
        else:
            message = "Vous n'êtes pas un Superuser."
        return DeleteBeneficiary(deleted=deleted, success=success, message=message, id=id)

#************************************************************************

class CreateBeneficiaryGroup(graphene.Mutation):
    class Arguments:
        beneficiary_group_data = BeneficiaryGroupInput(required=True)
        image = Upload(required=False)

    beneficiary_group = graphene.Field(BeneficiaryGroupType)

    def mutate(root, info, image=None, beneficiary_group_data=None):
        creator = info.context.user
        beneficiary_ids = beneficiary_group_data.pop("beneficiaries")
        beneficiary_group = BeneficiaryGroup(**beneficiary_group_data)
        beneficiary_group.creator = creator
        if info.context.FILES:
            # file1 = info.context.FILES['1']
            if image and isinstance(image, UploadedFile):
                image_file = beneficiary_group.image
                if not image_file:
                    image_file = File()
                    image_file.creator = creator
                image_file.image = image
                image_file.save()
                beneficiary_group.image = image_file
        beneficiary_group.save()
        folder = Folder.objects.create(name=str(beneficiary_group.id)+'_'+beneficiary_group.name,creator=creator)
        beneficiary_group.folder = folder
        beneficiaries = Beneficiary.objects.filter(id__in=beneficiary_ids)
        for beneficiary in beneficiaries:
            try:
                beneficiary_group_item = BeneficiaryGroupItem.objects.get(beneficiary__id=beneficiary.id, beneficiary_group__id=beneficiary_group.id)
            except BeneficiaryGroupItem.DoesNotExist:
                BeneficiaryGroupItem.objects.create(
                        beneficiary_group=beneficiary_group,
                        beneficiary=beneficiary,
                        creator=creator
                    )
        beneficiary_group.save()
        return CreateBeneficiaryGroup(beneficiary_group=beneficiary_group)

class UpdateBeneficiaryGroup(graphene.Mutation):
    class Arguments:
        id = graphene.ID()
        beneficiary_group_data = BeneficiaryGroupInput(required=True)
        image = Upload(required=False)

    beneficiary_group = graphene.Field(BeneficiaryGroupType)

    def mutate(root, info, id, image=None, beneficiary_group_data=None):
        creator = info.context.user
        beneficiary_ids = beneficiary_group_data.pop("beneficiaries")
        BeneficiaryGroup.objects.filter(pk=id).update(**beneficiary_group_data)
        beneficiary_group = BeneficiaryGroup.objects.get(pk=id)
        if not beneficiary_group.folder or beneficiary_group.folder is None:
            folder = Folder.objects.create(name=str(beneficiary_group.id)+'_'+beneficiary_group.name,creator=creator)
            BeneficiaryGroup.objects.filter(pk=id).update(folder=folder)
        if not image and beneficiary_group.image:
            image_file = beneficiary_group.image
            image_file.delete()
        if info.context.FILES:
            # file1 = info.context.FILES['1']
            if image and isinstance(image, UploadedFile):
                image_file = beneficiary_group.image
                if not image_file:
                    image_file = File()
                    image_file.creator = creator
                image_file.image = image
                image_file.save()
                beneficiary_group.image = image_file
            beneficiary_group.save()
        BeneficiaryGroupItem.objects.filter(beneficiary_group=beneficiary_group).exclude(beneficiary__id__in=beneficiary_ids).delete()
        beneficiaries = Beneficiary.objects.filter(id__in=beneficiary_ids)
        for beneficiary in beneficiaries:
            try:
                beneficiary_group_item = BeneficiaryGroupItem.objects.get(beneficiary__id=beneficiary.id, beneficiary_group__id=beneficiary_group.id)
            except BeneficiaryGroupItem.DoesNotExist:
                BeneficiaryGroupItem.objects.create(
                        beneficiary_group=beneficiary_group,
                        beneficiary=beneficiary,
                        creator=creator
                    )
        return UpdateBeneficiaryGroup(beneficiary_group=beneficiary_group)

class UpdateBeneficiaryGroupState(graphene.Mutation):
    class Arguments:
        id = graphene.ID()

    beneficiary_group = graphene.Field(BeneficiaryGroupType)
    done = graphene.Boolean()
    success = graphene.Boolean()
    message = graphene.String()

    def mutate(root, info, id, beneficiary_group_fields=None):
        creator = info.context.user
        done = True
        success = True
        beneficiary_group = None
        message = ''
        try:
            beneficiary_group = BeneficiaryGroup.objects.get(pk=id)
            BeneficiaryGroup.objects.filter(pk=id).update(is_active=not beneficiary_group.is_active)
            beneficiary_group.refresh_from_db()
        except Exception as e:
            done = False
            success = False
            beneficiary_group=None
            message = "Une erreur s'est produite."
        return UpdateBeneficiaryGroupState(done=done, success=success, message=message,beneficiary_group=beneficiary_group)


class DeleteBeneficiaryGroup(graphene.Mutation):
    class Arguments:
        id = graphene.ID()

    beneficiary_group = graphene.Field(BeneficiaryGroupType)
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
            beneficiary_group = BeneficiaryGroup.objects.get(pk=id)
            beneficiary_group.delete()
            deleted = True
            success = True
        else:
            message = "Vous n'êtes pas un Superuser."
        return DeleteBeneficiaryGroup(deleted=deleted, success=success, message=message, id=id)

#************************************************************************
#*******************************************************************************************************************************

class HumanRessourcesMutation(graphene.ObjectType):
    create_employee = CreateEmployee.Field()
    update_employee = UpdateEmployee.Field()
    update_employee_state = UpdateEmployeeState.Field()
    delete_employee = DeleteEmployee.Field()

    create_employee_group = CreateEmployeeGroup.Field()
    update_employee_group = UpdateEmployeeGroup.Field()
    update_employee_group_state = UpdateEmployeeGroupState.Field()
    delete_employee_group = DeleteEmployeeGroup.Field()

    create_beneficiary = CreateBeneficiary.Field()
    update_beneficiary = UpdateBeneficiary.Field()
    update_beneficiary_state = UpdateBeneficiaryState.Field()
    delete_beneficiary = DeleteBeneficiary.Field()

    create_beneficiary_group = CreateBeneficiaryGroup.Field()
    update_beneficiary_group = UpdateBeneficiaryGroup.Field()
    update_beneficiary_group_state = UpdateBeneficiaryGroupState.Field()
    delete_beneficiary_group = DeleteBeneficiaryGroup.Field()