import graphene
from graphene_django import DjangoObjectType
from django.core.files.uploadedfile import InMemoryUploadedFile, UploadedFile
from graphql_jwt.decorators import login_required
from graphene_file_upload.scalars import Upload

from django.db.models import Q

from stocks.models import Material, MaterialAssignment
from medias.models import Folder, File

class MaterialType(DjangoObjectType):
    class Meta:
        model = Material
        fields = "__all__"
    image = graphene.String()
    def resolve_image( instance, info, **kwargs ):
        return instance.image and info.context.build_absolute_uri(instance.image.image.url)

class MaterialNodeType(graphene.ObjectType):
    nodes = graphene.List(MaterialType)
    total_count = graphene.Int()

class MaterialFilterInput(graphene.InputObjectType):
    keyword = graphene.String(required=False)
    starting_date_time = graphene.DateTime(required=False)
    ending_date_time = graphene.DateTime(required=False)

class MaterialInput(graphene.InputObjectType):
    id = graphene.ID(required=False)
    number = graphene.String(required=False)
    name = graphene.String(required=True)
    bar_code = graphene.String(required=False)
    is_blocked = graphene.Boolean(required=False)
    is_stock_auto = graphene.Boolean(required=False)
    designation = graphene.String(required=False)
    buying_price_ht = graphene.Float(required=False)
    tva = graphene.Float(required=False)
    quantity = graphene.Int(required=False)
    description = graphene.String(required=False)
    observation = graphene.String(required=False)
    is_active = graphene.Boolean(required=False)

class MaterialAssignmentType(DjangoObjectType):
    class Meta:
        model = MaterialAssignment
        fields = "__all__"

    document = graphene.String()

    def resolve_document(instance, info, **kwargs):
        return instance.document and info.context.build_absolute_uri(
            instance.document.file.url
        )


class MaterialAssignmentNodeType(graphene.ObjectType):
    nodes = graphene.List(MaterialAssignmentType)
    total_count = graphene.Int()


class MaterialAssignmentFilterInput(graphene.InputObjectType):
    keyword = graphene.String(required=False)
    starting_date_time = graphene.DateTime(required=False)
    ending_date_time = graphene.DateTime(required=False)
    cash_registers = graphene.List(graphene.Int, required=False)

class MaterialAssignmentInput(graphene.InputObjectType):
    id = graphene.ID(required=False)
    number = graphene.String(required=False)
    label = graphene.String(required=False)
    comment = graphene.String(required=False)
    description = graphene.String(required=False)
    date = graphene.DateTime(required=False)
    amount = graphene.Decimal(required=False)
    transaction_type = graphene.String(required=False)
    cash_register_id = graphene.Int(name="cashRegister", required=True)

class StocksQuery(graphene.ObjectType):
    materials = graphene.Field(MaterialNodeType, material_filter= MaterialFilterInput(required=False), offset = graphene.Int(required=False), limit = graphene.Int(required=False), page = graphene.Int(required=False))
    material = graphene.Field(MaterialType, id = graphene.ID())
    material_assignments = graphene.Field(
        MaterialAssignmentNodeType,
        material_assignment_filter=MaterialAssignmentFilterInput(required=False),
        offset=graphene.Int(required=False),
        limit=graphene.Int(required=False),
        page=graphene.Int(required=False),
    )
    material_assignment = graphene.Field(MaterialAssignmentType, id=graphene.ID())

    def resolve_materials(root, info, material_filter=None, offset=None, limit=None, page=None):
        # We can easily optimize query count in the resolve method
        user = info.context.user
        company = user.the_current_company
        total_count = 0
        materials = Material.objects.filter(company=company, is_deleted=False)
        if material_filter:
            keyword = material_filter.get('keyword', '')
            starting_date_time = material_filter.get('starting_date_time')
            ending_date_time = material_filter.get('ending_date_time')
            if keyword:
                materials = materials.filter(Q(name__icontains=keyword) | Q(designation__icontains=keyword) | Q(bar_code__icontains=keyword))
            if starting_date_time:
                materials = materials.filter(created_at__gte=starting_date_time)
            if ending_date_time:
                materials = materials.filter(created_at__lte=ending_date_time)
        materials = materials.order_by('-created_at')
        total_count = materials.count()
        if page:
            offset = limit * (page - 1)
        if offset is not None and limit is not None:
            materials = materials[offset:offset + limit]
        return MaterialNodeType(nodes=materials, total_count=total_count)

    def resolve_material(root, info, id):
        # We can easily optimize query count in the resolve method
        user = info.context.user
        company = user.the_current_company
        try:
            material = Material.objects.get(pk=id, company=company)
        except Material.DoesNotExist:
            material = None
        return material

    def resolve_material_assignments(
        root, info, material_assignment_filter=None, offset=None, limit=None, page=None
    ):
        # We can easily optimize query count in the resolve method
        user = info.context.user
        company = user.the_current_company
        total_count = 0
        material_assignments = MaterialAssignment.objects.filter(cash_register__company=company, is_deleted=False)
        if not user.can_manage_finance():
            if user.is_manager():
                material_assignments = material_assignments.filter(Q(cash_register__establishments__establishment__managers__employee=user.get_employee_in_company()) | Q(creator=user))
            else:
                material_assignments = material_assignments.filter(creator=user)
        if material_assignment_filter:
            keyword = material_assignment_filter.get("keyword", "")
            starting_date_time = material_assignment_filter.get("starting_date_time")
            ending_date_time = material_assignment_filter.get("ending_date_time")
            cash_registers = material_assignment_filter.get("cash_registers")
            if cash_registers:
                material_assignments = material_assignments.filter(cash_register__id__in=cash_registers)
            if keyword:
                material_assignments = material_assignments.filter(
                    Q(name__icontains=keyword)
                    | Q(description__icontains=keyword)
                )
            if starting_date_time:
                material_assignments = material_assignments.filter(created_at__gte=starting_date_time)
            if ending_date_time:
                material_assignments = material_assignments.filter(created_at__lte=ending_date_time)
        material_assignments = material_assignments.order_by("-created_at").distinct()
        total_count = material_assignments.count()
        if page:
            offset = limit * (page - 1)
        if offset is not None and limit is not None:
            material_assignments = material_assignments[offset : offset + limit]
        return MaterialAssignmentNodeType(nodes=material_assignments, total_count=total_count)

    def resolve_material_assignment(root, info, id):
        # We can easily optimize query count in the resolve method
        user = info.context.user
        company = user.the_current_company
        try:
            material_assignment = MaterialAssignment.objects.get(pk=id, cash_register__company=company)
        except MaterialAssignment.DoesNotExist:
            material_assignment = None
        return material_assignment 

#************************************************************************

class CreateMaterial(graphene.Mutation):
    class Arguments:
        material_data = MaterialInput(required=True)
        image = Upload(required=False)

    material = graphene.Field(MaterialType)

    def mutate(root, info, image=None, material_data=None):
        creator = info.context.user
        material = Material(**material_data)
        material.creator = creator
        material.company = creator.current_company if creator.current_company is not None else creator.company
        if info.context.FILES:
            # file1 = info.context.FILES['1']
            if image and isinstance(image, UploadedFile):
                image_file = material.image
                if not image_file:
                    image_file = File()
                    image_file.creator = creator
                image_file.image = image
                image_file.save()
                material.image = image_file
        material.save()
        folder = Folder.objects.create(name=str(material.id)+'_'+material.name,creator=creator)
        material.folder = folder
        material.save()
        return CreateMaterial(material=material)

class UpdateMaterial(graphene.Mutation):
    class Arguments:
        id = graphene.ID()
        material_data = MaterialInput(required=True)
        image = Upload(required=False)

    material = graphene.Field(MaterialType)

    def mutate(root, info, id, image=None, material_data=None):
        creator = info.context.user
        try:
            material = Material.objects.get(pk=id, company=creator.the_current_company)
        except Material.DoesNotExist:
            raise e
        Material.objects.filter(pk=id).update(**material_data)
        material.refresh_from_db()
        if not material.folder or material.folder is None:
            folder = Folder.objects.create(name=str(material.id)+'_'+material.name,creator=creator)
            Material.objects.filter(pk=id).update(folder=folder)
        if not image and material.image:
            image_file = material.image
            image_file.delete()
        if info.context.FILES:
            # file1 = info.context.FILES['1']
            if image and isinstance(image, UploadedFile):
                image_file = material.image
                if not image_file:
                    image_file = File()
                    image_file.creator = creator
                image_file.image = image
                image_file.save()
                material.image = image_file
            material.save()
        return UpdateMaterial(material=material)
        
class UpdateMaterialState(graphene.Mutation):
    class Arguments:
        id = graphene.ID()

    material = graphene.Field(MaterialType)
    done = graphene.Boolean()
    success = graphene.Boolean()
    message = graphene.String()

    def mutate(root, info, id, material_fields=None):
        creator = info.context.user
        try:
            material = Material.objects.get(pk=id, company=creator.the_current_company)
        except Material.DoesNotExist:
            raise e
        done = True
        success = True
        message = ''
        try:
            material = Material.objects.get(pk=id)
            Material.objects.filter(pk=id).update(is_active=not material.is_active)
            material.refresh_from_db()
        except Exception as e:
            done = False
            success = False
            material=None
            message = "Une erreur s'est produite."
        return UpdateMaterialState(done=done, success=success, message=message,material=material)


class DeleteMaterial(graphene.Mutation):
    class Arguments:
        id = graphene.ID()

    material = graphene.Field(MaterialType)
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
            material = Material.objects.get(pk=id, company=current_user.the_current_company)
        except Material.DoesNotExist:
            raise e
        if current_user.is_superuser:
            material = Material.objects.get(pk=id)
            material.delete()
            deleted = True
            success = True
        else:
            message = "Vous n'êtes pas un Superuser."
        return DeleteMaterial(deleted=deleted, success=success, message=message, id=id)


# *************************************************************************#
# ************************************************************************


class CreateMaterialAssignment(graphene.Mutation):
    class Arguments:
        material_assignment_data = MaterialAssignmentInput(required=True)
        document = Upload(required=False)

    material_assignment = graphene.Field(MaterialAssignmentType)

    def mutate(root, info, document=None, material_assignment_data=None):
        creator = info.context.user
        # Vérification si le cash_register existe
        try:
            cash_register = CashRegister.objects.get(pk=material_assignment_data.cash_register_id, company=creator.the_current_company)
        except CashRegister.DoesNotExist:
            raise ValueError("Le registre de caisse spécifié n'existe pas.")
        material_assignment = MaterialAssignment(**material_assignment_data)
        material_assignment.creator = creator
        material_assignment.company = creator.the_current_company
        if info.context.FILES:
            # file1 = info.context.FILES['1']
            if document and isinstance(document, UploadedFile):
                document_file = material_assignment.document
                if not document_file:
                    document_file = File()
                    document_file.creator = creator
                document_file.file = document
                document_file.save()
                material_assignment.document = document_file
        material_assignment.save()
        return CreateMaterialAssignment(material_assignment=material_assignment)


class UpdateMaterialAssignment(graphene.Mutation):
    class Arguments:
        id = graphene.ID()
        material_assignment_data = MaterialAssignmentInput(required=True)
        document = Upload(required=False)

    material_assignment = graphene.Field(MaterialAssignmentType)

    def mutate(root, info, id, document=None, material_assignment_data=None):
        creator = info.context.user
        # Vérification si le cash_register existe
        try:
            cash_register = CashRegister.objects.get(pk=material_assignment_data.cash_register_id, company=creator.the_current_company)
        except CashRegister.DoesNotExist:
            raise ValueError("Le registre de caisse spécifié n'existe pas.")
        MaterialAssignment.objects.filter(pk=id).update(**material_assignment_data)
        material_assignment = MaterialAssignment.objects.get(pk=id)
        if not document and material_assignment.document:
            document_file = material_assignment.document
            document_file.delete()
        if info.context.FILES:
            # file1 = info.context.FILES['1']
            if document and isinstance(document, UploadedFile):
                document_file = material_assignment.document
                if not document_file:
                    document_file = File()
                    document_file.creator = creator
                document_file.file = document
                document_file.save()
                material_assignment.document = document_file
            material_assignment.save()
        return UpdateMaterialAssignment(material_assignment=material_assignment)


class DeleteMaterialAssignment(graphene.Mutation):
    class Arguments:
        id = graphene.ID()

    material_assignment = graphene.Field(MaterialAssignmentType)
    id = graphene.ID()
    deleted = graphene.Boolean()
    success = graphene.Boolean()
    message = graphene.String()

    def mutate(root, info, id):
        deleted = False
        success = False
        message = ""
        current_user = info.context.user
        try:
            material_assignment = MaterialAssignment.objects.get(pk=id, cash_register__company=current_user.the_current_company)
        except MaterialAssignment.DoesNotExist:
            raise e
        if current_user.is_superuser:
            material_assignment = MaterialAssignment.objects.get(pk=id)
            material_assignment.delete()
            deleted = True
            success = True
        else:
            message = "Vous n'êtes pas un Superuser."
        return DeleteMaterialAssignment(deleted=deleted, success=success, message=message, id=id)


# *************************************************************************#
# ************************************************************************

#*************************************************************************#
class StocksMutation(graphene.ObjectType):
    create_material = CreateMaterial.Field()
    update_material = UpdateMaterial.Field()
    update_material_state = UpdateMaterialState.Field()
    delete_material = DeleteMaterial.Field()

    create_material_assignment = CreateMaterialAssignment.Field()
    update_material_assignment = UpdateMaterialAssignment.Field()
    delete_material_assignment = DeleteMaterialAssignment.Field()