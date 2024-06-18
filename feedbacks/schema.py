import graphene
import channels_graphql_ws
from graphene_django import DjangoObjectType
from django.core.files.uploadedfile import InMemoryUploadedFile, UploadedFile
from graphql_jwt.decorators import login_required
from graphene_file_upload.scalars import Upload

from feedbacks.models import Comment, Signature, StatusChange
from works.models import Task, TaskStep, Ticket
from medias.models import File
from feedbacks.broadcaster import broadcastCommentAdded, broadcastCommentDeleted

class CommentType(DjangoObjectType):
    class Meta:
        model = Comment
        fields = "__all__"
    image = graphene.String()
    def resolve_image( instance, info, **kwargs ):
        return instance.image and info.context.build_absolute_uri(instance.image.image.url)

class SignatureType(DjangoObjectType):
    class Meta:
        model = Signature
        fields = "__all__"
    image = graphene.String()
    satisfaction = graphene.String()
    def resolve_image( instance, info, **kwargs ):
        return instance.image and info.context.build_absolute_uri(instance.image.image.url)
    def resolve_satisfaction( instance, info, **kwargs ):
        return "MEDIUM" if instance.satisfaction == '' else instance.satisfaction

class StatusChangeType(DjangoObjectType):
    class Meta:
        model = StatusChange
        fields = "__all__"

class CommentNodeType(graphene.ObjectType):
    nodes = graphene.List(CommentType)
    total_count = graphene.Int()

class CommentInput(graphene.InputObjectType):
    id = graphene.ID(required=False)
    text = graphene.String(required=False)
    parent_id = graphene.Int(name="parent", required=False)

class SignatureInput(graphene.InputObjectType):
    id = graphene.ID(required=False)
    base64_encoded = graphene.String(required=False)
    author_name = graphene.String(required=False)
    author_number = graphene.String(required=False)
    author_email = graphene.String(required=False)
    satisfaction = graphene.String(required=False)
    comment = graphene.String(required=False)

class CommentsQuery(graphene.ObjectType):
    comments = graphene.List(CommentType, offset = graphene.Int(required=False), limit = graphene.Int(required=False), page = graphene.Int(required=False))
    task_step_comments = graphene.Field(CommentNodeType, task_step_id = graphene.ID(), offset = graphene.Int(required=False), limit = graphene.Int(required=False), page = graphene.Int(required=False))
    ticket_comments = graphene.Field(CommentNodeType, ticket_id = graphene.ID(), offset = graphene.Int(required=False), limit = graphene.Int(required=False), page = graphene.Int(required=False))
    comment = graphene.Field(CommentType, id = graphene.ID())

    def resolve_comments(root, info, offset=None, limit=None, page=None):
        comments = Comment.objects.all()
        return comments

    def resolve_task_step_comments(root, info, task_step_id, offset=None, limit=None, page=None):
        # We can easily optimize query count in the resolve method
        total_count = 0
        try:
        	task_step = TaskStep.objects.get(pk=task_step_id)
        except TaskStep.DoesNotExist:
        	raise ValueError("L'étape d'intervention spécifiée n'existe pas.")
        total_count = task_step.comments.all().count()
        if page:
            offset = limit*(page-1)
        if offset is not None and limit is not None:
            task_step_comments = task_step.comments.all()[offset:offset+limit]
        else:
            task_step_comments = task_step.comments.all()
        return CommentNodeType(nodes=task_step_comments, total_count=total_count)

    def resolve_ticket_comments(root, info, ticket_id, offset=None, limit=None, page=None):
        # We can easily optimize query count in the resolve method
        total_count = 0
        try:
            ticket = Ticket.objects.get(pk=ticket_id)
        except Ticket.DoesNotExist:
            raise ValueError("L'étape d'intervention spécifiée n'existe pas.")
        total_count = ticket.comments.all().count()
        if page:
            offset = limit*(page-1)
        if offset is not None and limit is not None:
            ticket_comments = ticket.comments.all()[offset:offset+limit]
        else:
            ticket_comments = ticket.comments.all()
        return CommentNodeType(nodes=ticket_comments, total_count=total_count)

    def resolve_comment(root, info, id):
        # We can easily optimize query count in the resolve method
        try:
            comment = Comment.objects.get(pk=id)
        except Comment.DoesNotExist:
            comment = None
        return comment

#************************************************************************

class CreateComment(graphene.Mutation):
    class Arguments:
        comment_data = CommentInput(required=True)
        image = Upload(required=False)
        task_step_id = graphene.ID(required=False)
        ticket_id = graphene.ID(required=False)

    comment = graphene.Field(CommentType)

    def mutate(root, info, task_step_id=None, ticket_id=None, image=None, comment_data=None):
        creator = info.context.user
        comment = Comment(**comment_data)
        comment.creator = creator
        if info.context.FILES:
            # file1 = info.context.FILES['1']
            if image and isinstance(image, UploadedFile):
                image_file = comment.image
                if not image_file:
                    image_file = File()
                    image_file.creator = creator
                image_file.image = image
                image_file.save()
                comment.image = image_file
        comment.save()
        broadcastCommentAdded(comment)
        if task_step_id and task_step_id is not None:
        	TaskStep.objects.get(pk=task_step_id).comments.add(comment)
        if ticket_id and ticket_id is not None:
            Ticket.objects.get(pk=ticket_id).comments.add(comment)
        return CreateComment(comment=comment)

class UpdateComment(graphene.Mutation):
    class Arguments:
        id = graphene.ID()
        comment_data = CommentInput(required=True)
        image = Upload(required=False)

    comment = graphene.Field(CommentType)

    def mutate(root, info, id, image=None, comment_data=None):
        creator = info.context.user
        Comment.objects.filter(pk=id).update(**comment_data)
        comment = Comment.objects.get(pk=id)
        if not image and comment.image:
            image_file = comment.image
            image_file.delete()
        if info.context.FILES:
            # file1 = info.context.FILES['1']
            if image and isinstance(image, UploadedFile):
                image_file = comment.image
                if not image_file:
                    image_file = File()
                    image_file.creator = creator
                image_file.image = image
                image_file.save()
                comment.image = image_file
            comment.save()
        return UpdateComment(comment=comment)


class DeleteComment(graphene.Mutation):
    class Arguments:
        id = graphene.ID()

    comment = graphene.Field(CommentType)
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
            comment = Comment.objects.get(pk=id)
            broadcastCommentDeleted(comment)
            comment.delete()
            deleted = True
            success = True
        else:
            message = "Vous n'êtes pas un Superuser."
        return DeleteComment(deleted=deleted, success=success, message=message, id=id)

#*************************************************************************#
class CommentsMutation(graphene.ObjectType):
    create_comment = CreateComment.Field()
    update_comment = UpdateComment.Field()
    delete_comment = DeleteComment.Field()


#**************************************Subscription**********************************


class OnCommentAdded(channels_graphql_ws.Subscription):
    """Simple GraphQL subscription."""

    # Leave only latest 64 messages in the server queue.
    notification_queue_limit = 64

    # Subscription payload.
    comment = graphene.Field(CommentType)

    class Arguments:
        """That is how subscription arguments are defined."""
        # arg1 = graphene.String()
        # arg2 = graphene.String()
        task_step_id = graphene.ID(required=False)
        ticket_id = graphene.ID(required=False)

    @staticmethod
    def subscribe(root, info, task_step_id=None, ticket_id=None):
        """Called when user subscribes."""

        # Return the list of subscription group names.
        return ["ON_COMMENT_ADDED"]

    @staticmethod
    def publish(payload, info, task_step_id=None, ticket_id=None):
        """Called to notify the client."""
        #print('send -*******************')
        #print(payload)
        # Here `payload` contains the `payload` from the `broadcast()`
        # invocation (see below). You can return `MySubscription.SKIP`
        # if you wish to suppress the notification to a particular
        # client. For example, this allows to avoid notifications for
        # the actions made by this particular client.
        if task_step_id and task_step_id is not None:
            if 'taskStep' in payload and 'comment' in payload and 'task_step' in payload['comment']:
                if str(task_step_id) != str(payload['comment']['task_step']['id']):
                    return OnCommentAdded.SKIP
        return OnCommentAdded(comment=payload['comment'])

class OnCommentDeleted(channels_graphql_ws.Subscription):
    """Simple GraphQL subscription."""

    # Leave only latest 64 messages in the server queue.
    notification_queue_limit = 64

    # Subscription payload.
    comment = graphene.Field(CommentType)

    class Arguments:
        """That is how subscription arguments are defined."""
        # arg1 = graphene.String()
        # arg2 = graphene.String()
        task_step_id = graphene.ID(required=False)
        ticket_id = graphene.ID(required=False)

    @staticmethod
    def subscribe(root, info, task_step_id=None, ticket_id=None):
        """Called when user subscribes."""

        # Return the list of subscription group names.
        return ["ON_COMMENT_DELETED"]

    @staticmethod
    def publish(payload, info, task_step_id=None, ticket_id=None):
        """Called to notify the client."""
        #print('send -*******************')
        #print(payload)
        # Here `payload` contains the `payload` from the `broadcast()`
        # invocation (see below). You can return `MySubscription.SKIP`
        # if you wish to suppress the notification to a particular
        # client. For example, this allows to avoid notifications for
        # the actions made by this particular client.
        if task_step_id and task_step_id is not None:
            if 'taskStep' in payload and 'comment' in payload and 'task_step' in payload['comment']:
                if str(task_step_id) != str(payload['comment']['task_step']['id']):
                    return OnCommentAdded.SKIP
        return OnCommentDeleted(comment=payload['comment'])

class CommentsSubscription(graphene.ObjectType):
    on_comment_added = OnCommentAdded.Field()
    on_comment_deleted = OnCommentDeleted.Field()