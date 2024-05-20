import graphene
from graphene_django import DjangoObjectType
from django.core.files.uploadedfile import InMemoryUploadedFile, UploadedFile
from graphql_jwt.decorators import login_required
from graphene_file_upload.scalars import Upload

from django.db.models import Q

from stocks.models import Material
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

class StocksQuery(graphene.ObjectType):
    materials = graphene.Field(MaterialNodeType, material_filter= MaterialFilterInput(required=False), offset = graphene.Int(required=False), limit = graphene.Int(required=False), page = graphene.Int(required=False))
    material = graphene.Field(MaterialType, id = graphene.ID())

    def resolve_materials(root, info, material_filter=None, offset=None, limit=None, page=None):
        # We can easily optimize query count in the resolve method
        total_count = 0
        materials = Material.objects.all()
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
        try:
            material = Material.objects.get(pk=id)
        except Material.DoesNotExist:
            material = None
        return material

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
        Material.objects.filter(pk=id).update(**material_data)
        material = Material.objects.get(pk=id)
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
        done = True
        success = True
        material = None
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
        if current_user.is_superuser:
            material = Material.objects.get(pk=id)
            material.delete()
            deleted = True
            success = True
        else:
            message = "Vous n'êtes pas un Superuser."
        return DeleteMaterial(deleted=deleted, success=success, message=message, id=id)

#*************************************************************************#
class StocksMutation(graphene.ObjectType):
    create_material = CreateMaterial.Field()
    update_material = UpdateMaterial.Field()
    update_material_state = UpdateMaterialState.Field()
    delete_material = DeleteMaterial.Field()