import graphene
from graphene_django import DjangoObjectType
from django.core.files.uploadedfile import InMemoryUploadedFile, UploadedFile
from graphql_jwt.decorators import login_required
from graphene_file_upload.scalars import Upload

from django.db.models import Q

from purchases.models import Supplier
from medias.models import Folder, File

class SupplierType(DjangoObjectType):
    class Meta:
        model = Supplier
        fields = "__all__"
    photo = graphene.String()
    cover_image = graphene.String()
    def resolve_photo( instance, info, **kwargs ):
        return instance.photo and info.context.build_absolute_uri(instance.photo.image.url)
    def resolve_cover_image( instance, info, **kwargs ):
        return instance.cover_image and info.context.build_absolute_uri(instance.cover_image.image.url)

class SupplierNodeType(graphene.ObjectType):
    nodes = graphene.List(SupplierType)
    total_count = graphene.Int()

class SupplierFilterInput(graphene.InputObjectType):
    keyword = graphene.String(required=False)
    starting_date_time = graphene.DateTime(required=False)
    ending_date_time = graphene.DateTime(required=False)

class SupplierInput(graphene.InputObjectType):
    id = graphene.ID(required=False)
    number = graphene.String(required=False)
    external_number = graphene.String(required=False)
    name = graphene.String(required=True)
    email = graphene.String(required=True)
    supplier_type = graphene.String(required=True)
    manager_name = graphene.String(required=True)
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

class PurchasesQuery(graphene.ObjectType):
    suppliers = graphene.Field(SupplierNodeType, supplier_filter= SupplierFilterInput(required=False), id_company = graphene.ID(required=False), offset = graphene.Int(required=False), limit = graphene.Int(required=False), page = graphene.Int(required=False))
    supplier = graphene.Field(SupplierType, id = graphene.ID())
    def resolve_suppliers(root, info, supplier_filter=None, id_company=None, offset=None, limit=None, page=None):
        # We can easily optimize query count in the resolve method
        total_count = 0
        suppliers = Supplier.objects.filter(company__id=id_company) if id_company else Supplier.objects.all()
        if supplier_filter:
            keyword = supplier_filter.get('keyword', '')
            starting_date_time = supplier_filter.get('starting_date_time')
            ending_date_time = supplier_filter.get('ending_date_time')
            if keyword:
                suppliers = suppliers.filter(Q(name__icontains=keyword) | Q(manager_name__icontains=keyword) | Q(email__icontains=keyword))
            if starting_date_time:
                suppliers = suppliers.filter(created_at__gte=starting_date_time)
            if ending_date_time:
                suppliers = suppliers.filter(created_at__lte=ending_date_time)
        suppliers = suppliers.order_by('-created_at')
        total_count = suppliers.count()
        if page:
            offset = limit * (page - 1)
        if offset is not None and limit is not None:
            suppliers = suppliers[offset:offset + limit]
        return SupplierNodeType(nodes=suppliers, total_count=total_count)

    def resolve_supplier(root, info, id):
        # We can easily optimize query count in the resolve method
        try:
            supplier = Supplier.objects.get(pk=id)
        except Supplier.DoesNotExist:
            supplier = None
        return supplier

class CreateSupplier(graphene.Mutation):
    class Arguments:
        supplier_data = SupplierInput(required=True)
        photo = Upload(required=False)
        cover_image = Upload(required=False)

    supplier = graphene.Field(SupplierType)

    def mutate(root, info, photo=None, cover_image=None,  supplier_data=None):
        creator = info.context.user
        supplier = Supplier(**supplier_data)
        supplier.creator = creator
        if info.context.FILES:
            # file1 = info.context.FILES['1']
            if photo and isinstance(photo, UploadedFile):
                photo_file = supplier.photo
                if not photo_file:
                    photo_file = File()
                    photo_file.creator = creator
                photo_file.image = photo
                photo_file.save()
                supplier.photo = photo_file
            # file2 = info.context.FILES['2']
            if cover_image and isinstance(cover_image, UploadedFile):
                cover_image_file = supplier.cover_image
                if not cover_image_file:
                    cover_image_file = File()
                    cover_image_file.creator = creator
                cover_image_file.image = cover_image
                cover_image_file.save()
                supplier.cover_image = cover_image_file
        supplier.save()
        folder = Folder.objects.create(name=str(supplier.id)+'_'+supplier.name,creator=creator)
        supplier.folder = folder
        supplier.save()
        return CreateSupplier(supplier=supplier)

class UpdateSupplier(graphene.Mutation):
    class Arguments:
        id = graphene.ID()
        supplier_data = SupplierInput(required=True)
        photo = Upload(required=False)
        cover_image = Upload(required=False)

    supplier = graphene.Field(SupplierType)

    def mutate(root, info, id, photo=None, cover_image=None,  supplier_data=None):
        creator = info.context.user
        Supplier.objects.filter(pk=id).update(**supplier_data)
        supplier = Supplier.objects.get(pk=id)
        if not supplier.folder or supplier.folder is None:
            folder = Folder.objects.create(name=str(supplier.id)+'_'+supplier.name,creator=creator)
            Supplier.objects.filter(pk=id).update(folder=folder)
        if not photo and supplier.photo:
            photo_file = supplier.photo
            photo_file.delete()
        if not cover_image and supplier.cover_image:
            cover_image_file = supplier.cover_image
            cover_image_file.delete()
        if info.context.FILES:
            # file1 = info.context.FILES['1']
            if photo and isinstance(photo, UploadedFile):
                photo_file = supplier.photo
                if not photo_file:
                    photo_file = File()
                    photo_file.creator = creator
                photo_file.image = photo
                photo_file.save()
                supplier.photo = photo_file
            # file2 = info.context.FILES['2']
            if cover_image and isinstance(cover_image, UploadedFile):
                cover_image_file = supplier.cover_image
                if not cover_image_file:
                    cover_image_file = File()
                    cover_image_file.creator = creator
                cover_image_file.image = cover_image
                cover_image_file.save()
                supplier.cover_image = cover_image_file
            supplier.save()
        supplier = Supplier.objects.get(pk=id)
        return UpdateSupplier(supplier=supplier)
        
class UpdateSupplierState(graphene.Mutation):
    class Arguments:
        id = graphene.ID()

    supplier = graphene.Field(SupplierType)
    done = graphene.Boolean()
    success = graphene.Boolean()
    message = graphene.String()

    def mutate(root, info, id, supplier_fields=None):
        creator = info.context.user
        done = True
        success = True
        supplier = None
        message = ''
        try:
            supplier = Supplier.objects.get(pk=id)
            Supplier.objects.filter(pk=id).update(is_active=not supplier.is_active)
            supplier.refresh_from_db()
        except Exception as e:
            done = False
            success = False
            supplier=None
            message = "Une erreur s'est produite."
        return UpdateSupplierState(done=done, success=success, message=message,supplier=supplier)

class DeleteSupplier(graphene.Mutation):
    class Arguments:
        id = graphene.ID()

    supplier = graphene.Field(SupplierType)
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
            supplier = Supplier.objects.get(pk=id)
            supplier.delete()
            deleted = True
            success = True
        else:
            message = "Vous n'êtes pas un Superuser."
        return DeleteSupplier(deleted=deleted, success=success, message=message, id=id)

class PurchasesMutation(graphene.ObjectType):
    create_supplier = CreateSupplier.Field()
    update_supplier = UpdateSupplier.Field()
    update_supplier_state = UpdateSupplierState.Field()
    delete_supplier = DeleteSupplier.Field()