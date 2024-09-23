import graphene
from graphene_django import DjangoObjectType
from django.core.files.uploadedfile import InMemoryUploadedFile, UploadedFile
from graphql_jwt.decorators import login_required
from graphene_file_upload.scalars import Upload

from django.db.models import Q

from blog.models import Post
from medias.models import Folder, File

class PostType(DjangoObjectType):
    class Meta:
        model = Post
        fields = "__all__"

    image = graphene.String()

    def resolve_image(instance, info, **kwargs):
        return instance.image and info.context.build_absolute_uri(
            instance.image.image.url
        )

class PostNodeType(graphene.ObjectType):
    nodes = graphene.List(PostType)
    total_count = graphene.Int()

class PostFilterInput(graphene.InputObjectType):
    keyword = graphene.String(required=False)
    starting_date_time = graphene.DateTime(required=False)
    ending_date_time = graphene.DateTime(required=False)


class PostInput(graphene.InputObjectType):
    id = graphene.ID(required=False)
    number = graphene.String(required=False)
    title = graphene.String(required=False)
    content = graphene.String(required=False)
    is_active = graphene.Boolean(required=False)
    description = graphene.String(required=False)
    observation = graphene.String(required=False)

class BlogQuery(graphene.ObjectType):
    posts = graphene.Field(PostNodeType, post_filter= PostFilterInput(required=False), id_company = graphene.ID(required=False), offset = graphene.Int(required=False), limit = graphene.Int(required=False), page = graphene.Int(required=False))
    post = graphene.Field(PostType, id = graphene.ID())
    def resolve_posts(root, info, post_filter=None, id_company=None, offset=None, limit=None, page=None):
        # We can easily optimize query count in the resolve method
        user = info.context.user
        company = user.current_company if user.current_company is not None else user.company
        total_count = 0
        posts = Post.objects.filter(company__id=id_company) if id_company else Post.objects.filter(company=company)
        if post_filter:
            keyword = post_filter.get('keyword', '')
            starting_date_time = post_filter.get('starting_date_time')
            ending_date_time = post_filter.get('ending_date_time')
            if keyword:
                posts = posts.filter(Q(title__icontains=keyword))
            if starting_date_time:
                posts = posts.filter(created_at__gte=starting_date_time)
            if ending_date_time:
                posts = posts.filter(created_at__lte=ending_date_time)
        posts = posts.order_by('-created_at')
        total_count = posts.count()
        if page:
            offset = limit * (page - 1)
        if offset is not None and limit is not None:
            posts = posts[offset:offset + limit]
        return PostNodeType(nodes=posts, total_count=total_count)

    def resolve_post(root, info, id):
        # We can easily optimize query count in the resolve method
        try:
            post = Post.objects.get(pk=id)
        except Post.DoesNotExist:
            post = None
        return post

#***************************************************************************

class CreatePost(graphene.Mutation):
    class Arguments:
        post_data = PostInput(required=True)
        image = Upload(required=False)

    post = graphene.Field(PostType)

    def mutate(root, info, image=None, post_data=None):
        creator = info.context.user
        post = Post(**post_data)
        post.creator = creator
        post.company = creator.current_company if creator.current_company is not None else creator.company
        if info.context.FILES:
            # file1 = info.context.FILES['1']
            if image and isinstance(image, UploadedFile):
                image_file = post.image
                if not image_file:
                    image_file = File()
                    image_file.creator = creator
                image_file.image = image
                image_file.save()
                post.image = image_file
        post.save()
        return CreatePost(post=post)

class UpdatePost(graphene.Mutation):
    class Arguments:
        id = graphene.ID()
        post_data = PostInput(required=True)
        image = Upload(required=False)

    post = graphene.Field(PostType)

    def mutate(root, info, id, image=None, post_data=None):
        creator = info.context.user
        Post.objects.filter(pk=id).update(**post_data)
        post = Post.objects.get(pk=id)
        if not image and post.image:
            image_file = post.image
            image_file.delete()
        if info.context.FILES:
            # file1 = info.context.FILES['1']
            if image and isinstance(image, UploadedFile):
                image_file = post.image
                if not image_file:
                    image_file = File()
                    image_file.creator = creator
                image_file.image = image
                image_file.save()
                post.image = image_file
            post.save()
        return UpdatePost(post=post)

class UpdatePostState(graphene.Mutation):
    class Arguments:
        id = graphene.ID()

    post = graphene.Field(PostType)
    done = graphene.Boolean()
    success = graphene.Boolean()
    message = graphene.String()

    def mutate(root, info, id, post_fields=None):
        creator = info.context.user
        done = True
        success = True
        post = None
        message = ''
        try:
            post = Post.objects.get(pk=id)
            Post.objects.filter(pk=id).update(is_active=not post.is_active)
            post.refresh_from_db()
        except Exception as e:
            done = False
            success = False
            post=None
            message = "Une erreur s'est produite."
        return UpdatePostState(done=done, success=success, message=message,post=post)

class DeletePost(graphene.Mutation):
    class Arguments:
        id = graphene.ID()

    post = graphene.Field(PostType)
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
            post = Post.objects.get(pk=id)
            post.delete()
            deleted = True
            success = True
        else:
            message = "Vous n'êtes pas un Superuser."
        return DeletePost(deleted=deleted, success=success, message=message, id=id)

#************************************************************************

#*******************************************************************************************************************************

class BlogMutation(graphene.ObjectType):
    create_post = CreatePost.Field()
    update_post = UpdatePost.Field()
    update_post_state = UpdatePostState.Field()
    delete_post = DeletePost.Field()
    