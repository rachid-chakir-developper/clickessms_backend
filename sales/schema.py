import graphene
from graphene_django import DjangoObjectType
from django.core.files.uploadedfile import InMemoryUploadedFile, UploadedFile
from graphql_jwt.decorators import login_required
from graphene_file_upload.scalars import Upload

from django.db.models import Q

from sales.models import Client
from medias.models import Folder, File

class ClientType(DjangoObjectType):
    class Meta:
        model = Client
        fields = "__all__"
    photo = graphene.String()
    cover_image = graphene.String()
    def resolve_photo( instance, info, **kwargs ):
        return instance.photo and info.context.build_absolute_uri(instance.photo.image.url)
    def resolve_cover_image( instance, info, **kwargs ):
        return instance.cover_image and info.context.build_absolute_uri(instance.cover_image.image.url)

class ClientNodeType(graphene.ObjectType):
    nodes = graphene.List(ClientType)
    total_count = graphene.Int()

class ClientFilterInput(graphene.InputObjectType):
    keyword = graphene.String(required=False)
    starting_date_time = graphene.DateTime(required=False)
    ending_date_time = graphene.DateTime(required=False)

class ClientInput(graphene.InputObjectType):
    id = graphene.ID(required=False)
    number = graphene.String(required=False)
    external_number = graphene.String(required=False)
    name = graphene.String(required=True)
    email = graphene.String(required=True)
    client_type = graphene.String(required=True)
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
    
class SalesQuery(graphene.ObjectType):
    clients = graphene.Field(ClientNodeType, client_filter= ClientFilterInput(required=False), id_company = graphene.ID(required=False), offset = graphene.Int(required=False), limit = graphene.Int(required=False), page = graphene.Int(required=False))
    client = graphene.Field(ClientType, id = graphene.ID())
    def resolve_clients(root, info, client_filter=None, id_company=None, offset=None, limit=None, page=None):
        # We can easily optimize query count in the resolve method
        total_count = 0
        clients = Client.objects.filter(company__id=id_company) if id_company else Client.objects.all()
        if client_filter:
            keyword = client_filter.get('keyword', '')
            starting_date_time = client_filter.get('starting_date_time')
            ending_date_time = client_filter.get('ending_date_time')
            if keyword:
                clients = clients.filter(Q(name__icontains=keyword) | Q(manager_name__icontains=keyword) | Q(email__icontains=keyword))
            if starting_date_time:
                clients = clients.filter(created_at__gte=starting_date_time)
            if ending_date_time:
                clients = clients.filter(created_at__lte=ending_date_time)
        clients = clients.order_by('-created_at')
        total_count = clients.count()
        if page:
            offset = limit * (page - 1)
        if offset is not None and limit is not None:
            clients = clients[offset:offset + limit]
        return ClientNodeType(nodes=clients, total_count=total_count)

    def resolve_client(root, info, id):
        # We can easily optimize query count in the resolve method
        try:
            client = Client.objects.get(pk=id)
        except Client.DoesNotExist:
            client = None
        return client

class CreateClient(graphene.Mutation):
    class Arguments:
        client_data = ClientInput(required=True)
        photo = Upload(required=False)
        cover_image = Upload(required=False)

    client = graphene.Field(ClientType)

    def mutate(root, info, photo=None, cover_image=None,  client_data=None):
        creator = info.context.user
        client = Client(**client_data)
        client.creator = creator
        client.company = creator.current_company if creator.current_company is not None else creator.company
        if info.context.FILES:
            # file1 = info.context.FILES['1']
            if photo and isinstance(photo, UploadedFile):
                photo_file = client.photo
                if not photo_file:
                    photo_file = File()
                    photo_file.creator = creator
                photo_file.image = photo
                photo_file.save()
                client.photo = photo_file
            # file2 = info.context.FILES['2']
            if cover_image and isinstance(cover_image, UploadedFile):
                cover_image_file = client.cover_image
                if not cover_image_file:
                    cover_image_file = File()
                    cover_image_file.creator = creator
                cover_image_file.image = cover_image
                cover_image_file.save()
                client.cover_image = cover_image_file
        client.save()
        folder = Folder.objects.create(name=str(client.id)+'_'+client.name,creator=creator)
        client.folder = folder
        client.save()
        return CreateClient(client=client)

class UpdateClient(graphene.Mutation):
    class Arguments:
        id = graphene.ID()
        client_data = ClientInput(required=True)
        photo = Upload(required=False)
        cover_image = Upload(required=False)

    client = graphene.Field(ClientType)

    def mutate(root, info, id, photo=None, cover_image=None,  client_data=None):
        creator = info.context.user
        Client.objects.filter(pk=id).update(**client_data)
        client = Client.objects.get(pk=id)
        if not client.folder or client.folder is None:
            folder = Folder.objects.create(name=str(client.id)+'_'+client.name,creator=creator)
            Client.objects.filter(pk=id).update(folder=folder)
        if not photo and client.photo:
            photo_file = client.photo
            photo_file.delete()
        if not cover_image and client.cover_image:
            cover_image_file = client.cover_image
            cover_image_file.delete()
        if info.context.FILES:
            # file1 = info.context.FILES['1']
            if photo and isinstance(photo, UploadedFile):
                photo_file = client.photo
                if not photo_file:
                    photo_file = File()
                    photo_file.creator = creator
                photo_file.image = photo
                photo_file.save()
                client.photo = photo_file
            # file2 = info.context.FILES['2']
            if cover_image and isinstance(cover_image, UploadedFile):
                cover_image_file = client.cover_image
                if not cover_image_file:
                    cover_image_file = File()
                    cover_image_file.creator = creator
                cover_image_file.image = cover_image
                cover_image_file.save()
                client.cover_image = cover_image_file
            client.save()
        client = Client.objects.get(pk=id)
        return UpdateClient(client=client)

class UpdateClientState(graphene.Mutation):
    class Arguments:
        id = graphene.ID()

    client = graphene.Field(ClientType)
    done = graphene.Boolean()
    success = graphene.Boolean()
    message = graphene.String()

    def mutate(root, info, id, client_fields=None):
        creator = info.context.user
        done = True
        success = True
        client = None
        message = ''
        try:
            client = Client.objects.get(pk=id)
            Client.objects.filter(pk=id).update(is_active=not client.is_active)
            client.refresh_from_db()
        except Exception as e:
            done = False
            success = False
            client=None
            message = "Une erreur s'est produite."
        return UpdateClientState(done=done, success=success, message=message,client=client)

class DeleteClient(graphene.Mutation):
    class Arguments:
        id = graphene.ID()

    client = graphene.Field(ClientType)
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
            client = Client.objects.get(pk=id)
            client.delete()
            deleted = True
            success = True
        else:
            message = "Vous n'êtes pas un Superuser."
        return DeleteClient(deleted=deleted, success=success, message=message, id=id)


#*************************************************************************#

class SalesMutation(graphene.ObjectType):
    create_client = CreateClient.Field()
    update_client = UpdateClient.Field()
    update_client_state = UpdateClientState.Field()
    delete_client = DeleteClient.Field()