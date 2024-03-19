import os
import graphene
from graphene_django import DjangoObjectType
from graphql_jwt.decorators import login_required
from graphene_file_upload.scalars import Upload

from medias.models import Folder, File

class ChildrenFolderType(DjangoObjectType):
    class Meta:
        model = Folder
        fields = "__all__"
        
def getFileTypeFromFileInstance(file_instance=None):
    # Extraire l'extension du fichier depuis l'URL
    _, file_extension = os.path.splitext(file_instance.file.url)

    # Mapper l'extension à une catégorie (video, image, autre)
    if file_extension.lower() in ['.mp4', '.avi', '.mkv', '.mov']:
        return 'VIDEO'
    elif file_extension.lower() in ['.jpg', '.jpeg', '.png', '.gif']:
        return 'IMAGE'
    else:
        return file_instance.file_type

class ChildrenFileType(DjangoObjectType):
    class Meta:
        model = File
        fields = "__all__"
    def resolve_file ( instance, info, **kwargs ):
        return instance.file and info.context.build_absolute_uri(instance.file.url)
    def resolve_file_type ( instance, info, **kwargs ):
        return getFileTypeFromFileInstance(file_instance=instance)

class FolderType(DjangoObjectType):
    class Meta:
        model = Folder
        fields = "__all__"
    folders = graphene.List(ChildrenFolderType)
    files = graphene.List(ChildrenFileType)
    def resolve_folders ( instance, info, **kwargs ):
        return instance.children_folders.all()
    def resolve_files ( instance, info, **kwargs ):
        return instance.file_set.all()

class FolderInput(graphene.InputObjectType):
    id = graphene.ID(required=False)
    number = graphene.String(required=False)
    name = graphene.String(required=True)
    folder_type = graphene.String(required=False)
    description = graphene.String(required=False)
    observation = graphene.String(required=False)
    is_active = graphene.Boolean(required=False)
    folder_id = graphene.Int(name="folder", required=False)

class FileType(DjangoObjectType):
    class Meta:
        model = File
        fields = "__all__"
    def resolve_file( instance, info, **kwargs ):
        return instance.file and info.context.build_absolute_uri(instance.file.url)
    def resolve_video( instance, info, **kwargs ):
        return instance.video and info.context.build_absolute_uri(instance.video.url)
    def resolve_thumbnail( instance, info, **kwargs ):
        return instance.thumbnail and info.context.build_absolute_uri(instance.thumbnail.url)
    def resolve_image( instance, info, **kwargs ):
        return instance.image and info.context.build_absolute_uri(instance.image.url)

class FileInput(graphene.InputObjectType):
    id = graphene.ID(required=False)
    number = graphene.String(required=False)
    name = graphene.String(required=True)
    file_type = graphene.String(required=False)
    description = graphene.String(required=False)
    observation = graphene.String(required=False)
    is_active = graphene.Boolean(required=False)
    folder_id = graphene.Int(name="folder", required=False)

class MediasQuery(graphene.ObjectType):
    folders = graphene.List(FolderType)
    folder = graphene.Field(FolderType, id = graphene.ID())
    files = graphene.List(FileType)
    file = graphene.Field(FileType, id = graphene.ID())

    def resolve_folders(root, info):
        # We can easily optimize query count in the resolve method
        folders = Folder.objects.all()
        return folders

    def resolve_folder(root, info, id):
        # We can easily optimize query count in the resolve method
        folder = Folder.objects.get(pk=id)
        return folder

    def resolve_files(root, info):
        # We can easily optimize query count in the resolve method
        files = File.objects.all()
        return files

    def resolve_file(root, info, id):
        # We can easily optimize query count in the resolve method
        file = File.objects.get(pk=id)
        return file

#*******************************************************************#

class CreateFolder(graphene.Mutation):
    class Arguments:
        folder_data = FolderInput(required=True)

    folder = graphene.Field(FolderType)

    def mutate(root, info, folder_data=None):
        creator = info.context.user
        folder = Folder(**folder_data)
        folder.creator = creator
        folder.save()
        return CreateFolder(folder=folder)

class UpdateFolder(graphene.Mutation):
    class Arguments:
        id = graphene.ID()
        folder_data = FolderInput(required=True)

    folder = graphene.Field(FolderType)

    def mutate(root, info, id, folder_data=None):
        Folder.objects.filter(pk=id).update(**folder_data)
        folder = Folder.objects.get(pk=id)
        return UpdateFolder(folder=folder)


class DeleteFolder(graphene.Mutation):
    class Arguments:
        id = graphene.ID()

    folder = graphene.Field(FolderType)
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
            folder = Folder.objects.get(pk=id)
            if current_user.is_superuser or folder.creator.id == current_user.id:
                folder.delete()
                deleted = True
                success = True
            else:
                message = "Vous n'êtes pas un Superuser."
        except Folder.DoesNotExist:
            message = "Ce fichier n'exite pas pour le supprimer."
        return DeleteFolder(deleted=deleted, success=success, message=message, id=id)

#*******************************************************************#

class CreateFile(graphene.Mutation):
    class Arguments:
        file_data = FileInput(required=True)
        file_upload = Upload(required=True)

    file = graphene.Field(FileType)

    def mutate(root, info, file_upload, file_data=None):
        creator = info.context.user
        file = File(**file_data)
        file.creator = creator
        if info.context.FILES:
            # file_upload = info.context.FILES['1']
            file.file = file_upload
        file.save()
        return CreateFile(file=file)

class UpdateFile(graphene.Mutation):
    class Arguments:
        id = graphene.ID()
        file_data = FileInput(required=True)
        file_upload = Upload(required=False)

    file = graphene.Field(FileType)

    def mutate(root, info, id, file_upload, file_data=None):
        File.objects.filter(pk=id).update(**file_data)
        file = File.objects.get(pk=id)
        if info.context.FILES:
            # file_upload = info.context.FILES['1']
            file.file = file_upload
            file.save()
        return UpdateFile(file=file)


class DeleteFile(graphene.Mutation):
    class Arguments:
        id = graphene.ID()

    file = graphene.Field(FileType)
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
            file = File.objects.get(pk=id)
            if current_user.is_superuser or file.creator.id == current_user.id:
                file.delete()
                deleted = True
                success = True
            else:
                message = "Vous n'êtes pas un Superuser."
        except File.DoesNotExist:
            message = "Ce fichier n'exite pas pour le supprimer."
        return DeleteFile(deleted=deleted, success=success, message=message, id=id)

class MediasMutation(graphene.ObjectType):
    create_folder = CreateFolder.Field()
    update_folder = UpdateFolder.Field()
    delete_folder = DeleteFolder.Field()

    create_file = CreateFile.Field()
    update_file = UpdateFile.Field()
    delete_file = DeleteFile.Field()