import graphene
import channels_graphql_ws
from graphene_django import DjangoObjectType
from django.core.files.uploadedfile import InMemoryUploadedFile, UploadedFile
from graphql_jwt.decorators import login_required
from graphene_file_upload.scalars import Upload

from feedbacks.models import Comment, Signature, StatusChange, Feedback
from works.models import Task, TaskAction, TaskStep, Ticket
from purchases.models import Expense
from human_ressources.models import BeneficiaryAdmission
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
    def resolve_base64_encoded(self, info, **kwargs):
        if self.base64_encoded and not self.base64_encoded.startswith("data:image/"):
            return f"data:image/png;base64,{self.base64_encoded}"
        return self.base64_encoded
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

class FeedbackType(DjangoObjectType):
    class Meta:
        model = Feedback
        fields = "__all__"

    image = graphene.String()

    def resolve_image(instance, info, **kwargs):
        return instance.image and info.context.build_absolute_uri(
            instance.image.image.url
        )

class FeedbackNodeType(graphene.ObjectType):
    nodes = graphene.List(FeedbackType)
    total_count = graphene.Int()

class FeedbackFilterInput(graphene.InputObjectType):
    keyword = graphene.String(required=False)
    starting_date_time = graphene.DateTime(required=False)
    ending_date_time = graphene.DateTime(required=False)

class FeedbackInput(graphene.InputObjectType):
    id = graphene.ID(required=False)
    feedback_module = graphene.String(required=False)
    title = graphene.String(required=False)
    message = graphene.String(required=False)
    is_active = graphene.Boolean(required=False)

class CommentInput(graphene.InputObjectType):
    id = graphene.ID(required=False)
    text = graphene.String(required=False)
    parent_id = graphene.Int(name="parent", required=False)
    ticket_id = graphene.Int(name="ticket", required=False)
    task_id = graphene.Int(name="task", required=False)
    task_action_id = graphene.Int(name="taskAction", required=False)
    expense_id = graphene.Int(name="expense", required=False)
    beneficiary_admission_id = graphene.Int(name="beneficiaryAdmission", required=False)

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
    task_comments = graphene.Field(CommentNodeType, task_id = graphene.ID(), offset = graphene.Int(required=False), limit = graphene.Int(required=False), page = graphene.Int(required=False))
    task_action_comments = graphene.Field(CommentNodeType, task_action_id = graphene.ID(), offset = graphene.Int(required=False), limit = graphene.Int(required=False), page = graphene.Int(required=False))
    expense_comments = graphene.Field(CommentNodeType, expense_id = graphene.ID(), offset = graphene.Int(required=False), limit = graphene.Int(required=False), page = graphene.Int(required=False))
    beneficiary_admission_comments = graphene.Field(CommentNodeType, beneficiary_admission_id = graphene.ID(), offset = graphene.Int(required=False), limit = graphene.Int(required=False), page = graphene.Int(required=False))
    comment = graphene.Field(CommentType, id = graphene.ID())
    feedbacks = graphene.Field(
        FeedbackNodeType,
        feedback_filter=FeedbackFilterInput(required=False),
        offset=graphene.Int(required=False),
        limit=graphene.Int(required=False),
        page=graphene.Int(required=False),
    )
    feedback = graphene.Field(FeedbackType, id=graphene.ID())

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
            raise ValueError("Le ticket spécifiée n'existe pas.")
        total_count = ticket.comments.all().count()
        if page:
            offset = limit*(page-1)
        if offset is not None and limit is not None:
            ticket_comments = ticket.comments.all()[offset:offset+limit]
        else:
            ticket_comments = ticket.comments.all()
        return CommentNodeType(nodes=ticket_comments, total_count=total_count)

    def resolve_task_comments(root, info, task_id, offset=None, limit=None, page=None):
        # We can easily optimize query count in the resolve method
        total_count = 0
        try:
            task = Task.objects.get(pk=task_id)
        except Task.DoesNotExist:
            raise ValueError("L'intervention spécifiée n'existe pas.")
        total_count = task.comments.all().count()
        if page:
            offset = limit*(page-1)
        if offset is not None and limit is not None:
            task_comments = task.comments.all()[offset:offset+limit]
        else:
            task_comments = task.comments.all()
        return CommentNodeType(nodes=task_comments, total_count=total_count)

    def resolve_task_action_comments(root, info, task_action_id, offset=None, limit=None, page=None):
        # We can easily optimize query count in the resolve method
        total_count = 0
        try:
            task_action = TaskAction.objects.get(pk=task_action_id)
        except TaskAction.DoesNotExist:
            raise ValueError("L'action spécifiée n'existe pas.")
        total_count = task_action.comments.all().count()
        if page:
            offset = limit*(page-1)
        if offset is not None and limit is not None:
            task_action_comments = task_action.comments.all()[offset:offset+limit]
        else:
            task_action_comments = task_action.comments.all()
        return CommentNodeType(nodes=task_action_comments, total_count=total_count)

    def resolve_expense_comments(root, info, expense_id, offset=None, limit=None, page=None):
        # We can easily optimize query count in the resolve method
        total_count = 0
        try:
            expense = Expense.objects.get(pk=expense_id)
        except Expense.DoesNotExist:
            raise ValueError("La dépense spécifiée n'existe pas.")
        total_count = expense.comments.all().count()
        if page:
            offset = limit*(page-1)
        if offset is not None and limit is not None:
            expense_comments = expense.comments.all()[offset:offset+limit]
        else:
            expense_comments = expense.comments.all()
        return CommentNodeType(nodes=expense_comments, total_count=total_count)

    def resolve_beneficiary_admission_comments(root, info, beneficiary_admission_id, offset=None, limit=None, page=None):
        # We can easily optimize query count in the resolve method
        total_count = 0
        try:
            beneficiary_admission = BeneficiaryAdmission.objects.get(pk=beneficiary_admission_id)
        except BeneficiaryAdmission.DoesNotExist:
            raise ValueError("La dépense spécifiée n'existe pas.")
        total_count = beneficiary_admission.comments.all().count()
        if page:
            offset = limit*(page-1)
        if offset is not None and limit is not None:
            beneficiary_admission_comments = beneficiary_admission.comments.all()[offset:offset+limit]
        else:
            beneficiary_admission_comments = beneficiary_admission.comments.all()
        return CommentNodeType(nodes=beneficiary_admission_comments, total_count=total_count)

    def resolve_comment(root, info, id):
        # We can easily optimize query count in the resolve method
        try:
            comment = Comment.objects.get(pk=id)
        except Comment.DoesNotExist:
            comment = None
        return comment

    def resolve_feedbacks(
        root, info, feedback_filter=None, offset=None, limit=None, page=None
    ):
        # We can easily optimize query count in the resolve method
        user = info.context.user
        company = user.the_current_company
        total_count = 0
        feedbacks = Feedback.objects.all()
        if not user.is_superuser:
            feedbacks = feedbacks.filter(creator=user)
        if feedback_filter:
            keyword = feedback_filter.get("keyword", "")
            starting_date_time = feedback_filter.get("starting_date_time")
            ending_date_time = feedback_filter.get("ending_date_time")
            if keyword:
                feedbacks = feedbacks.filter(title__icontains=keyword)
            if starting_date_time:
                feedbacks = feedbacks.filter(created_at__gte=starting_date_time)
            if ending_date_time:
                feedbacks = feedbacks.filter(created_at__lte=ending_date_time)
        feedbacks = feedbacks.order_by("-created_at")
        total_count = feedbacks.count()
        if page:
            offset = limit * (page - 1)
        if offset is not None and limit is not None:
            feedbacks = feedbacks[offset : offset + limit]
        return FeedbackNodeType(nodes=feedbacks, total_count=total_count)

    def resolve_feedback(root, info, id):
        # We can easily optimize query count in the resolve method
        try:
            feedback = Feedback.objects.get(pk=id)
        except Feedback.DoesNotExist:
            feedback = None
        return feedback

#************************************************************************

class CreateComment(graphene.Mutation):
    class Arguments:
        comment_data = CommentInput(required=True)
        image = Upload(required=False)
        task_step_id = graphene.ID(required=False)
        ticket_id = graphene.ID(required=False)
        task_id = graphene.ID(required=False)
        task_action_id = graphene.ID(required=False)
        expense_id = graphene.ID(required=False)
        beneficiary_admission_id = graphene.ID(required=False)

    comment = graphene.Field(CommentType)

    def mutate(root, info, task_id=None, task_action_id=None, task_step_id=None, ticket_id=None, expense_id=None, beneficiary_admission_id=None, image=None, comment_data=None):
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
        if task_step_id and task_step_id is not None:
        	TaskStep.objects.get(pk=task_step_id).comments.add(comment)
        if ticket_id and ticket_id is not None:
            Ticket.objects.get(pk=ticket_id).comments.add(comment)
        if task_id and task_id is not None:
            Task.objects.get(pk=task_id).comments.add(comment)
        if task_action_id and task_action_id is not None:
            TaskAction.objects.get(pk=task_action_id).comments.add(comment)
        if expense_id and expense_id is not None:
            Expense.objects.get(pk=beneficiary_admission_id).comments.add(comment)
        if beneficiary_admission_id and beneficiary_admission_id is not None:
            BeneficiaryAdmission.objects.get(pk=beneficiary_admission_id).comments.add(comment)
        comment.refresh_from_db()
        broadcastCommentAdded(comment)
        return CreateComment(comment=comment)

class UpdateComment(graphene.Mutation):
    class Arguments:
        id = graphene.ID()
        comment_data = CommentInput(required=True)
        image = Upload(required=False)

    comment = graphene.Field(CommentType)

    def mutate(root, info, id, image=None, comment_data=None):
        creator = info.context.user
        try:
            comment = Comment.objects.get(pk=id, creator=creator)
        except Comment.DoesNotExist:
            raise e
        Comment.objects.filter(pk=id).update(**comment_data)
        comment.refresh_from_db()
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
        comment = Comment.objects.get(pk=id)
        if current_user.is_superuser or comment.creator==current_user:
            broadcastCommentDeleted(comment)
            comment.delete()
            deleted = True
            success = True
        else:
            message = "Vous n'êtes pas un Superuser."
        return DeleteComment(deleted=deleted, success=success, message=message, id=id)

# **********************************************************************************************

class CreateFeedback(graphene.Mutation):
    class Arguments:
        feedback_data = FeedbackInput(required=True)
        image = Upload(required=False)

    feedback = graphene.Field(FeedbackType)

    def mutate(root, info, image=None, feedback_data=None):
        creator = info.context.user
        feedback = Feedback(**feedback_data)
        feedback.creator = creator
        feedback.company = creator.the_current_company
        if info.context.FILES:
            # file1 = info.context.FILES['1']
            if image and isinstance(image, UploadedFile):
                image_file = feedback.image
                if not image_file:
                    image_file = File()
                    image_file.creator = creator
                image_file.image = image
                image_file.save()
                feedback.image = image_file
        feedback.save()
        return CreateFeedback(feedback=feedback)


class UpdateFeedback(graphene.Mutation):
    class Arguments:
        id = graphene.ID()
        feedback_data = FeedbackInput(required=True)
        image = Upload(required=False)

    feedback = graphene.Field(FeedbackType)

    def mutate(root, info, id, image=None, feedback_data=None):
        creator = info.context.user
        try:
            feedback = Feedback.objects.get(pk=id, creator=creator)
        except Feedback.DoesNotExist:
            raise e
        Feedback.objects.filter(pk=id).update(**feedback_data)
        feedback.refresh_from_db()
        if not image and feedback.image:
            image_file = feedback.image
            image_file.delete()
        if info.context.FILES:
            # file1 = info.context.FILES['1']
            if image and isinstance(image, UploadedFile):
                image_file = feedback.image
                if not image_file:
                    image_file = File()
                    image_file.creator = creator
                image_file.image = image
                image_file.save()
                feedback.image = image_file
            feedback.save()
        return UpdateFeedback(feedback=feedback)


class UpdateFeedbackState(graphene.Mutation):
    class Arguments:
        id = graphene.ID()

    feedback = graphene.Field(FeedbackType)
    done = graphene.Boolean()
    success = graphene.Boolean()
    message = graphene.String()

    def mutate(root, info, id, feedback_fields=None):
        creator = info.context.user
        try:
            feedback = Feedback.objects.get(pk=id, creator=creator)
        except Feedback.DoesNotExist:
            raise e
        done = True
        success = True
        message = ""
        try:
            Feedback.objects.filter(pk=id).update(
                is_active=not feedback.is_active
            )
            feedback.refresh_from_db()
        except Exception as e:
            done = False
            success = False
            feedback = None
            message = "Une erreur s'est produite."
        return UpdateFeedbackState(
            done=done, success=success, message=message, feedback=feedback
        )


class DeleteFeedback(graphene.Mutation):
    class Arguments:
        id = graphene.ID()

    feedback = graphene.Field(FeedbackType)
    id = graphene.ID()
    deleted = graphene.Boolean()
    success = graphene.Boolean()
    message = graphene.String()

    def mutate(root, info, id):
        deleted = False
        success = False
        message = ""
        current_user = info.context.user
        feedback = Feedback.objects.get(pk=id)
        if current_user.is_superuser or feedback.creator==current_user:
            feedback.delete()
            deleted = True
            success = True
        else:
            message = "Vous n'êtes pas un Superuser."
        return DeleteFeedback(
            deleted=deleted, success=success, message=message, id=id
        )


# *************************************************************************#



#*************************************************************************#
class CommentsMutation(graphene.ObjectType):
    create_comment = CreateComment.Field()
    update_comment = UpdateComment.Field()
    delete_comment = DeleteComment.Field()

    create_feedback = CreateFeedback.Field()
    update_feedback = UpdateFeedback.Field()
    update_feedback_state = UpdateFeedbackState.Field()
    delete_feedback = DeleteFeedback.Field()


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
        task_id = graphene.ID(required=False)
        task_step_id = graphene.ID(required=False)
        ticket_id = graphene.ID(required=False)
        task_action_id = graphene.ID(required=False)
        expense_id = graphene.ID(required=False)
        beneficiary_admission_id = graphene.ID(required=False)

    @staticmethod
    def subscribe(root, info, task_id=None, task_action_id=None, task_step_id=None, ticket_id=None, expense_id=None, beneficiary_admission_id=None):
        """Called when user subscribes."""
        
        # Return the list of subscription group names.
        return ["ON_COMMENT_ADDED"]

    @staticmethod
    def publish(payload, info, task_id=None, task_action_id=None, task_step_id=None, ticket_id=None, expense_id=None, beneficiary_admission_id=None):
        """Called to notify the client."""
        #print('send -*******************')
        #print(payload)
        # Here `payload` contains the `payload` from the `broadcast()`
        # invocation (see below). You can return `MySubscription.SKIP`
        # if you wish to suppress the notification to a particular
        # client. For example, this allows to avoid notifications for
        # the actions made by this particular client.
        if task_id and task_id is not None:
            if 'comment' in payload and payload['comment'].task:
                if str(task_id) != str(payload['comment'].task.id):
                    return OnCommentAdded.SKIP
        if task_action_id and task_action_id is not None:
            if 'comment' in payload and payload['comment'].task_action:
                if str(task_action_id) != str(payload['comment'].task_action.id):
                    return OnCommentAdded.SKIP
        if task_step_id and task_step_id is not None:
            if 'taskStep' in payload and 'comment' in payload and 'task_step' in payload['comment']:
                if str(task_step_id) != str(payload['comment']['task_step']['id']):
                    return OnCommentAdded.SKIP
        if ticket_id and ticket_id is not None:
            if 'comment' in payload and payload['comment'].ticket:
                if str(ticket_id) != str(payload['comment'].ticket.id):
                    return OnCommentAdded.SKIP
        if expense_id and expense_id is not None:
            if 'comment' in payload and payload['comment'].expense:
                if str(expense_id) != str(payload['comment'].expense.id):
                    return OnCommentAdded.SKIP
        if beneficiary_admission_id and beneficiary_admission_id is not None:
            if 'comment' in payload and payload['comment'].beneficiary_admission:
                if str(beneficiary_admission_id) != str(payload['comment'].beneficiary_admission.id):
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
        task_id = graphene.ID(required=False)
        task_step_id = graphene.ID(required=False)
        ticket_id = graphene.ID(required=False)
        task_action_id = graphene.ID(required=False)
        expense_id = graphene.ID(required=False)
        beneficiary_admission_id = graphene.ID(required=False)

    @staticmethod
    def subscribe(root, info, task_id=None, task_action_id=None, task_step_id=None, ticket_id=None, expense_id=None, beneficiary_admission_id=None):
        """Called when user subscribes."""

        # Return the list of subscription group names.
        return ["ON_COMMENT_DELETED"]

    @staticmethod
    def publish(payload, info, task_id=None, task_action_id=None, task_step_id=None, ticket_id=None, expense_id=None, beneficiary_admission_id=None):
        """Called to notify the client."""
        #print('send -*******************')
        #print(payload)
        # Here `payload` contains the `payload` from the `broadcast()`
        # invocation (see below). You can return `MySubscription.SKIP`
        # if you wish to suppress the notification to a particular
        # client. For example, this allows to avoid notifications for
        # the actions made by this particular client.
        if task_id and task_id is not None:
            if 'comment' in payload and payload['comment'].task:
                if str(task_id) != str(payload['comment'].task.id):
                    return OnCommentDeleted.SKIP
        if task_action_id and task_action_id is not None:
            if 'comment' in payload and payload['comment'].task_action:
                if str(task_action_id) != str(payload['comment'].task_action.id):
                    return OnCommentDeleted.SKIP
        if task_step_id and task_step_id is not None:
            if 'taskStep' in payload and 'comment' in payload and 'task_step' in payload['comment']:
                if str(task_step_id) != str(payload['comment']['task_step']['id']):
                    return OnCommentDeleted.SKIP
        if ticket_id and ticket_id is not None:
            if 'comment' in payload and payload['comment'].ticket:
                if str(ticket_id) != str(payload['comment'].ticket.id):
                    return OnCommentDeleted.SKIP
        if expense_id and expense_id is not None:
            if 'comment' in payload and payload['comment'].expense:
                if str(expense_id) != str(payload['comment'].expense.id):
                    return OnCommentDeleted.SKIP
        if beneficiary_admission_id and beneficiary_admission_id is not None:
            if 'comment' in payload and payload['comment'].beneficiary_admission:
                if str(beneficiary_admission_id) != str(payload['comment'].beneficiary_admission.id):
                    return OnCommentDeleted.SKIP
        return OnCommentDeleted(comment=payload['comment'])

class CommentsSubscription(graphene.ObjectType):
    on_comment_added = OnCommentAdded.Field()
    on_comment_deleted = OnCommentDeleted.Field()