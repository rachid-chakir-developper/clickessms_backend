import graphene
from graphene_django import DjangoObjectType
from django.core.files.uploadedfile import InMemoryUploadedFile, UploadedFile
from graphql_jwt.decorators import login_required
from graphene_file_upload.scalars import Upload

from django.db.models import Q

from building_estate.models import SpaceRoom
from medias.models import Folder, File
from medias.schema import MediaInput

class SpaceRoomType(DjangoObjectType):
    class Meta:
        model = SpaceRoom
        fields = "__all__"

    image = graphene.String()

    def resolve_image(instance, info, **kwargs):
        return instance.image and info.context.build_absolute_uri(
            instance.image.image.url
        )

class SpaceRoomNodeType(graphene.ObjectType):
    nodes = graphene.List(SpaceRoomType)
    total_count = graphene.Int()

class SpaceRoomFilterInput(graphene.InputObjectType):
    keyword = graphene.String(required=False)
    starting_date_time = graphene.DateTime(required=False)
    ending_date_time = graphene.DateTime(required=False)
    establishments = graphene.List(graphene.Int, required=False)
    order_by = graphene.String(required=False)

class SpaceRoomInput(graphene.InputObjectType):
    id = graphene.ID(required=False)
    number = graphene.String(required=False)
    name = graphene.String(required=False)
    room_type = graphene.String(required=False)
    capacity = graphene.Int(required=False)
    is_active = graphene.Boolean(required=False)
    description = graphene.String(required=False)
    observation = graphene.String(required=False)
    establishment_id = graphene.Int(name="establishment", required=False)

class BuildingEstateQuery(graphene.ObjectType):
    space_rooms = graphene.Field(SpaceRoomNodeType, space_room_filter= SpaceRoomFilterInput(required=False), id_company = graphene.ID(required=False), offset = graphene.Int(required=False), limit = graphene.Int(required=False), page = graphene.Int(required=False))
    space_room = graphene.Field(SpaceRoomType, id = graphene.ID())
    def resolve_space_rooms(root, info, space_room_filter=None, id_company=None, offset=None, limit=None, page=None):
        # We can easily optimize query count in the resolve method
        user = info.context.user
        company = user.the_current_company
        total_count = 0
        space_rooms = SpaceRoom.objects.filter(company__id=id_company) if id_company else SpaceRoom.objects.filter(company=company)
        the_order_by = '-created_at'
        if space_room_filter:
            keyword = space_room_filter.get('keyword', '')
            starting_date_time = space_room_filter.get('starting_date_time')
            ending_date_time = space_room_filter.get('ending_date_time')
            establishments = space_room_filter.get('establishments')
            order_by = space_room_filter.get('order_by')
            if establishments:
                space_rooms = space_rooms.filter(establishment__id__in=establishments)
            if keyword:
                space_rooms = space_rooms.filter(Q(title__icontains=keyword))
            if starting_date_time:
                space_rooms = space_rooms.filter(created_at__gte=starting_date_time)
            if ending_date_time:
                space_rooms = space_rooms.filter(created_at__lte=ending_date_time)
            if order_by:
                the_order_by = order_by
        space_rooms = space_rooms.order_by(the_order_by).distinct()
        total_count = space_rooms.count()
        if page:
            offset = limit * (page - 1)
        if offset is not None and limit is not None:
            space_rooms = space_rooms[offset:offset + limit]
        return SpaceRoomNodeType(nodes=space_rooms, total_count=total_count)

    def resolve_space_room(root, info, id):
        # We can easily optimize query count in the resolve method
        try:
            space_room = SpaceRoom.objects.get(pk=id)
        except SpaceRoom.DoesNotExist:
            space_room = None
        return space_room

#*****************************************************************************************************************

class CreateSpaceRoom(graphene.Mutation):
    class Arguments:
        space_room_data = SpaceRoomInput(required=True)
        image = Upload(required=False)

    space_room = graphene.Field(SpaceRoomType)

    def mutate(root, info, image=None, space_room_data=None):
        creator = info.context.user
        space_room = SpaceRoom(**space_room_data)
        space_room.creator = creator
        space_room.company = creator.the_current_company
        if info.context.FILES:
            # file1 = info.context.FILES['1']
            if image and isinstance(image, UploadedFile):
                image_file = space_room.image
                if not image_file:
                    image_file = File()
                    image_file.creator = creator
                image_file.image = image
                image_file.save()
                space_room.image = image_file
        space_room.save()
        folder = Folder.objects.create(
            name=str(space_room.id) + "_" + space_room.name,
            creator=creator,
        )
        space_room.folder = folder
        space_room.save()
        return CreateSpaceRoom(space_room=space_room)

class UpdateSpaceRoom(graphene.Mutation):
    class Arguments:
        id = graphene.ID()
        space_room_data = SpaceRoomInput(required=True)
        image = Upload(required=False)

    space_room = graphene.Field(SpaceRoomType)

    def mutate(root, info, id, image=None, space_room_data=None):
        creator = info.context.user
        SpaceRoom.objects.filter(pk=id).update(**space_room_data)
        space_room = SpaceRoom.objects.get(pk=id)
        if not space_room.folder or space_room.folder is None:
            folder = Folder.objects.create(
                name=str(space_room.id) + "_" + space_room.name,
                creator=creator,
            )
            SpaceRoom.objects.filter(pk=id).update(folder=folder)
        if not image and space_room.image:
            image_file = space_room.image
            image_file.delete()
        if info.context.FILES:
            # file1 = info.context.FILES['1']
            if image and isinstance(image, UploadedFile):
                image_file = space_room.image
                if not image_file:
                    image_file = File()
                    image_file.creator = creator
                image_file.image = image
                image_file.save()
                space_room.image = image_file
        space_room.save()
        return UpdateSpaceRoom(space_room=space_room)

class UpdateSpaceRoomState(graphene.Mutation):
    class Arguments:
        id = graphene.ID()

    space_room = graphene.Field(SpaceRoomType)
    done = graphene.Boolean()
    success = graphene.Boolean()
    message = graphene.String()

    def mutate(root, info, id, space_room_fields=None):
        creator = info.context.user
        done = True
        success = True
        space_room = None
        message = ''
        try:
            space_room = SpaceRoom.objects.get(pk=id)
            SpaceRoom.objects.filter(pk=id).update(is_active=not space_room.is_active)
            space_room.refresh_from_db()
        except Exception as e:
            done = False
            success = False
            space_room=None
            message = "Une erreur s'est produite."
        return UpdateSpaceRoomState(done=done, success=success, message=message,space_room=space_room)

class DeleteSpaceRoom(graphene.Mutation):
    class Arguments:
        id = graphene.ID()

    space_room = graphene.Field(SpaceRoomType)
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
            space_room = SpaceRoom.objects.get(pk=id)
            space_room.delete()
            deleted = True
            success = True
        else:
            message = "Vous n'êtes pas un Superuser."
        return DeleteSpaceRoom(deleted=deleted, success=success, message=message, id=id)

#************************************************************************

#*******************************************************************************************************************************

class BuildingEstateMutation(graphene.ObjectType):
    create_space_room = CreateSpaceRoom.Field()
    update_space_room = UpdateSpaceRoom.Field()
    update_space_room_state = UpdateSpaceRoomState.Field()
    delete_space_room = DeleteSpaceRoom.Field()
    