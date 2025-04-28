import graphene
from graphene_django import DjangoObjectType
from django.core.files.uploadedfile import InMemoryUploadedFile, UploadedFile
from graphql_jwt.decorators import login_required
from graphene_file_upload.scalars import Upload

from loan_management.models import TheObject, ObjectRecovery
from medias.models import File

class TheObjectType(DjangoObjectType):
    class Meta:
        model = TheObject
        fields = "__all__"
    image = graphene.String()
    def resolve_image( instance, info, **kwargs ):
        return instance.image and info.context.build_absolute_uri(instance.image.image.url)

class TheObjectNodeType(graphene.ObjectType):
    nodes = graphene.List(TheObjectType)
    total_count = graphene.Int()

class ObjectRecoveryType(DjangoObjectType):
    class Meta:
        model = ObjectRecovery
        fields = "__all__"

class TheObjectInput(graphene.InputObjectType):
    id = graphene.ID(required=False)
    number = graphene.String(required=False)
    name = graphene.String(required=True)
    description = graphene.String(required=False)
    observation = graphene.String(required=False)
    is_active = graphene.Boolean(required=False)
    client_id = graphene.Int(name="client", required=False)
    partner_id = graphene.Int(name="partner", required=False)

class TheObjectFilterInput(graphene.InputObjectType):
    keyword = graphene.String(required=False)
    recovery_date = graphene.DateTime(required=False)
    return_date = graphene.DateTime(required=False)

class ObjectRecoveryMediaInput(graphene.InputObjectType):
    id = graphene.ID(required=False)
    image = Upload(required=False)
    video = Upload(required=False)
    media = Upload(required=False)
    caption = graphene.String(required=False)

class ObjectRecoveryInput(graphene.InputObjectType):
    id = graphene.ID(required=False)
    number = graphene.String(required=False)
    name = graphene.String(required=False)
    description = graphene.String(required=False)
    observation = graphene.String(required=False)
    recovery_date = graphene.DateTime(required=False)
    return_date = graphene.DateTime(required=False)
    the_object_id = graphene.Int(name="the_object", required=False)

class LoansQuery(graphene.ObjectType):
    the_objects = graphene.Field(TheObjectNodeType, the_object_filter= TheObjectFilterInput(required=False), offset = graphene.Int(required=False), limit = graphene.Int(required=False), page = graphene.Int(required=False))
    the_object = graphene.Field(TheObjectType, id = graphene.ID())
    object_recovery = graphene.Field(ObjectRecoveryType, id = graphene.ID())

    def resolve_the_objects(root, info, the_object_filter=None, offset=None, limit=None, page=None):
        # We can easily optimize query count in the resolve method
        user = info.context.user
        company = user.current_company if user.current_company is not None else user.company
        total_count = 0
        the_objects = TheObject.objects.filter(company=company)
        if the_object_filter:
            keyword = the_object_filter.get('keyword', '')
            recovery_date = the_object_filter.get('recovery_date')
            return_date = the_object_filter.get('return_date')
            if keyword:
                the_objects = the_objects.filter(name__icontains=keyword)
            if recovery_date:
                the_objects = the_objects.filter(the_object_recoveries__recovery_date__gte=recovery_date)
            if return_date:
                the_objects = the_objects.filter(the_object_recoveries__return_date__lte=return_date)
        the_objects = the_objects.order_by('-created_at')        
        total_count = the_objects.count()
        if page:
            offset = limit * (page - 1)
        if offset is not None and limit is not None:
            the_objects = the_objects[offset:offset + limit]
        return TheObjectNodeType(nodes=the_objects, total_count=total_count)

    def resolve_the_object(root, info, id):
        # We can easily optimize query count in the resolve method
        try:
            the_object = TheObject.objects.get(pk=id)
        except TheObject.DoesNotExist:
            the_object = None
        return the_object

    def resolve_object_recovery(root, info, id):
        # We can easily optimize query count in the resolve method
        try:
            object_recovery = ObjectRecovery.objects.get(pk=id)
        except ObjectRecovery.DoesNotExist:
            object_recovery = None
        return object_recovery

#************************************************************************

class CreateTheObject(graphene.Mutation):
    class Arguments:
        the_object_data = TheObjectInput(required=True)
        image = Upload(required=False)

    the_object = graphene.Field(TheObjectType)

    def mutate(root, info, image=None, the_object_data=None):
        creator = info.context.user
        the_object = TheObject(**the_object_data)
        the_object.creator = creator
        the_object.company = creator.current_company if creator.current_company is not None else creator.company
        if info.context.FILES:
            # file1 = info.context.FILES['1']
            if image and isinstance(image, UploadedFile):
                image_file = the_object.image
                if not image_file:
                    image_file = File()
                    image_file.creator = creator
                image_file.image = image
                image_file.save()
                the_object.image = image_file
        the_object.save()
        return CreateTheObject(the_object=the_object)

class UpdateTheObject(graphene.Mutation):
    class Arguments:
        id = graphene.ID()
        the_object_data = TheObjectInput(required=True)
        image = Upload(required=False)

    the_object = graphene.Field(TheObjectType)

    def mutate(root, info, id, image=None, the_object_data=None):
        creator = info.context.user
        TheObject.objects.filter(pk=id).update(**the_object_data)
        the_object = TheObject.objects.get(pk=id)
        if not image and the_object.image:
            image_file = the_object.image
            image_file.delete()
        if info.context.FILES:
            # file1 = info.context.FILES['1']
            if image and isinstance(image, UploadedFile):
                image_file = the_object.image
                if not image_file:
                    image_file = File()
                    image_file.creator = creator
                image_file.image = image
                image_file.save()
                the_object.image = image_file
            the_object.save()
        return UpdateTheObject(the_object=the_object)

class UpdateTheObjectState(graphene.Mutation):
    class Arguments:
        id = graphene.ID()

    the_object = graphene.Field(TheObjectType)
    done = graphene.Boolean()
    success = graphene.Boolean()
    message = graphene.String()

    def mutate(root, info, id, the_object_fields=None):
        creator = info.context.user
        done = True
        success = True
        the_object = None
        message = ''
        try:
            the_object = TheObject.objects.get(pk=id)
            TheObject.objects.filter(pk=id).update(is_active=not the_object.is_active)
            the_object.refresh_from_db()
        except Exception as e:
            done = False
            success = False
            the_object=None
            message = "Une erreur s'est produite."
        return UpdateTheObjectState(done=done, success=success, message=message,the_object=the_object)

class DeleteTheObject(graphene.Mutation):
    class Arguments:
        id = graphene.ID()

    the_object = graphene.Field(TheObjectType)
    id = graphene.ID()
    deleted = graphene.Boolean()
    success = graphene.Boolean()
    message = graphene.String()

    def mutate(root, info, id):
        deleted = False
        success = False
        message = ''
        current_user = info.context.user
        the_object = TheObject.objects.get(pk=id)
        if current_user.is_superuser or the_object.creator==current_user:
            the_object.delete()
            deleted = True
            success = True
        else:
            message = "Oups ! Vous n'avez pas les droits pour supprimer cet élément."
        return DeleteTheObject(deleted=deleted, success=success, message=message, id=id)

#***********************************************************************************************************

class CreateObjectRecovery(graphene.Mutation):
    class Arguments:
        the_object_id = graphene.ID(required=True)
        object_recovery_data = ObjectRecoveryInput(required=False)
        images = graphene.List(ObjectRecoveryMediaInput, required=False)
        videos = graphene.List(ObjectRecoveryMediaInput, required=False)

    object_recovery = graphene.Field(ObjectRecoveryType)

    def mutate(root, info, the_object_id, images=None, videos=None, object_recovery_data=None):
        creator = info.context.user
        try:
            the_object = TheObject.objects.get(pk=the_object_id)
        except TheObject.DoesNotExist:
            raise ValueError("Une erreur s'est produite.")
        try:
            object_recovery = ObjectRecovery.objects.create(creator=creator, the_object=the_object)
            if object_recovery_data and object_recovery_data is not None:
                ObjectRecovery.objects.filter(pk=object_recovery.id).update(**object_recovery_data)
        except ObjectRecovery.DoesNotExist:
            raise ValueError("Une erreur s'est produite.")
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
            object_recovery.images.add(image_file)
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
            object_recovery.videos.add(video_file)
        object_recovery.save()
        return CreateObjectRecovery(object_recovery=object_recovery)

class UpdateObjectRecovery(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)
        object_recovery_data = ObjectRecoveryInput(required=False)
        images = graphene.List(ObjectRecoveryMediaInput, required=False)
        videos = graphene.List(ObjectRecoveryMediaInput, required=False)

    object_recovery = graphene.Field(ObjectRecoveryType)

    def mutate(root, info, id, images=None, videos=None, object_recovery_data=None):
        creator = info.context.user
        if object_recovery_data and object_recovery_data is not None:
            ObjectRecovery.objects.filter(pk=id).update(**object_recovery_data)
        try:
            object_recovery = ObjectRecovery.objects.get(pk=id)
        except ObjectRecovery.DoesNotExist:
            raise ValueError("La récupération de l'objet spécifié n'existe pas.")
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
            object_recovery.images.add(image_file)
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
            object_recovery.videos.add(video_file)
        object_recovery.save()
        return UpdateObjectRecovery(object_recovery=object_recovery)

class DeleteObjectRecovery(graphene.Mutation):
    class Arguments:
        id = graphene.ID()

    object_recovery = graphene.Field(TheObjectType)
    id = graphene.ID()
    deleted = graphene.Boolean()
    success = graphene.Boolean()
    message = graphene.String()

    def mutate(root, info, id):
        deleted = False
        success = False
        message = ''
        current_user = info.context.user
        object_recovery = ObjectRecovery.objects.get(pk=id)
        if current_user.is_superuser or object_recovery.creator==current_user:
            object_recovery.delete()
            deleted = True
            success = True
        else:
            message = "Oups ! Vous n'avez pas les droits pour supprimer cet élément."
        return DeleteObjectRecovery(deleted=deleted, success=success, message=message, id=id)

#*************************************************************************#
class LoansMutation(graphene.ObjectType):
    create_the_object = CreateTheObject.Field()
    update_the_object = UpdateTheObject.Field()
    update_the_object_state = UpdateTheObjectState.Field()
    delete_the_object = DeleteTheObject.Field()

    create_object_recovery = CreateObjectRecovery.Field()
    update_object_recovery = UpdateObjectRecovery.Field()
    delete_object_recovery = DeleteObjectRecovery.Field()