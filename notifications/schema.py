import graphene
import channels_graphql_ws
from graphene_django import DjangoObjectType
from django.core.files.uploadedfile import InMemoryUploadedFile, UploadedFile
from graphql_jwt.decorators import login_required
from graphene_file_upload.scalars import Upload

from notifications.models import Notification, MessageNotification, MessageNotificationEstablishment, MessageNotificationUserStatus
from notifications.notificator import broadcastNotificationsSeen, broadcastMessageNotificationsRead

from companies.models import Establishment
from medias.models import Folder, File

#************************************ObjectType************************************

class NotificationType(DjangoObjectType):
    class Meta:
        model = Notification
        fields = "__all__"

class NotificationNodeType(graphene.ObjectType):
    nodes = graphene.List(NotificationType)
    total_count = graphene.Int()
    not_seen_count = graphene.Int()


class MessageNotificationEstablishmentType(DjangoObjectType):
    class Meta:
        model = MessageNotificationEstablishment
        fields = "__all__"

class MessageNotificationType(DjangoObjectType):
    class Meta:
        model = MessageNotification
        fields = "__all__"

    image = graphene.String()
    is_read = graphene.Boolean()

    def resolve_image(instance, info, **kwargs):
        return instance.image and info.context.build_absolute_uri(
            instance.image.image.url
        )
    def resolve_is_read(instance, info, **kwargs):
        user = info.context.user
        return instance.message_notification_statuses.filter(user=user, is_read=True).exists() if not user.is_anonymous else False

class MessageNotificationNodeType(graphene.ObjectType):
    nodes = graphene.List(MessageNotificationType)
    total_count = graphene.Int()

class MessageNotificationFilterInput(graphene.InputObjectType):
    keyword = graphene.String(required=False)
    starting_date_time = graphene.DateTime(required=False)
    ending_date_time = graphene.DateTime(required=False)

#************************************InputObjectType************************************

class NotificationInput(graphene.InputObjectType):
    id = graphene.ID(required=False)
    is_read = graphene.Boolean(required=False)
    is_seen = graphene.Boolean(required=False)

class MessageNotificationInput(graphene.InputObjectType):
    id = graphene.ID(required=False)
    message_notification_type = graphene.String(required=False)
    title = graphene.String(required=False)
    message = graphene.String(required=False)
    is_active = graphene.Boolean(required=False)
    establishments = graphene.List(graphene.Int, required=False)

#************************************Mutation************************************

class NotificationsQuery(graphene.ObjectType):
    notifications = graphene.Field(NotificationNodeType, offset = graphene.Int(required=False), limit = graphene.Int(required=False), page = graphene.Int(required=False))
    notification = graphene.Field(NotificationType, id = graphene.ID())
    message_notifications = graphene.Field(
        MessageNotificationNodeType,
        message_notification_filter=MessageNotificationFilterInput(required=False),
        offset=graphene.Int(required=False),
        limit=graphene.Int(required=False),
        page=graphene.Int(required=False),
    )
    message_notification = graphene.Field(MessageNotificationType, id=graphene.ID())

    def resolve_notifications(root, info, offset=None, limit=None, page=None):
        # We can easily optimize query count in the resolve method
        user = info.context.user
        total_count = 0
        not_seen_count = 0
        notifications = Notification.objects.filter(recipient=user)
        total_count = notifications.count()
        not_seen_count = notifications.filter(is_seen=False).count()
        if page:
            offset = limit * (page - 1)
        if offset is not None and limit is not None:
            notifications = notifications[offset : offset + limit]
        return NotificationNodeType(nodes=notifications, total_count=total_count, not_seen_count=not_seen_count)

    def resolve_notification(root, info, id):
        # We can easily optimize query count in the resolve method
        try:
            notification = Notification.objects.get(pk=id)
        except Notification.DoesNotExist:
            notification = None
        return notification

    def resolve_message_notifications(
        root, info, message_notification_filter=None, offset=None, limit=None, page=None
    ):
        # We can easily optimize query count in the resolve method
        user = info.context.user
        company = (
            user.current_company if user.current_company is not None else user.company
        )
        total_count = 0
        message_notifications = MessageNotification.objects.filter(company=company)
        if message_notification_filter:
            keyword = message_notification_filter.get("keyword", "")
            starting_date_time = message_notification_filter.get("starting_date_time")
            ending_date_time = message_notification_filter.get("ending_date_time")
            if keyword:
                message_notifications = message_notifications.filter(
                    Q(name__icontains=keyword)
                    | Q(registration_number__icontains=keyword)
                    | Q(driver_name__icontains=keyword)
                )
            if starting_date_time:
                message_notifications = message_notifications.filter(created_at__gte=starting_date_time)
            if ending_date_time:
                message_notifications = message_notifications.filter(created_at__lte=ending_date_time)
        message_notifications = message_notifications.order_by("-created_at")
        total_count = message_notifications.count()
        if page:
            offset = limit * (page - 1)
        if offset is not None and limit is not None:
            message_notifications = message_notifications[offset : offset + limit]
        return MessageNotificationNodeType(nodes=message_notifications, total_count=total_count)

    def resolve_message_notification(root, info, id):
        # We can easily optimize query count in the resolve method
        try:
            message_notification = MessageNotification.objects.get(pk=id)
        except MessageNotification.DoesNotExist:
            message_notification = None
        return message_notification

#************************************Mutation************************************

class UpdateNotification(graphene.Mutation):
    class Arguments:
        id = graphene.ID()
        notification_data = NotificationInput(required=True)

    notification = graphene.Field(NotificationType)

    def mutate(root, info, id, notification_data=None):
        Notification.objects.filter(pk=id).update(**notification_data)
        notification = Notification.objects.get(pk=id)
        return UpdateNotification(notification=notification)

class MarkNotificationsAsSeen(graphene.Mutation):
    class Arguments:
        ids = graphene.List(graphene.ID)
        is_seen = graphene.Boolean(required=False)
    
    done = graphene.Boolean()
    success = graphene.Boolean()
    message = graphene.String()

    def mutate(root, info, ids, is_seen=None):
        done = True
        success = True
        message = ''
        try:
            Notification.objects.filter(is_seen=False).update(is_seen=True)
            not_seen_count = Notification.objects.filter(is_seen=False).count()
            broadcastNotificationsSeen(not_seen_count=not_seen_count)
        except Exception as e:
            done = False
            success = False
            message = "Une erreur s'est produite."
        return MarkNotificationsAsSeen(done=done, success=success, message=message)

class DeleteNotification(graphene.Mutation):
    class Arguments:
        id = graphene.ID()

    notification = graphene.Field(NotificationType)
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
            notification = Notification.objects.get(pk=id)
            notification.delete()
            deleted = True
            success = True
        else:
            message = "Vous n'êtes pas un Superuser."
        return DeleteNotification(deleted=deleted, success=success, message=message, id=id)

# ************************************************************************


class CreateMessageNotification(graphene.Mutation):
    class Arguments:
        message_notification_data = MessageNotificationInput(required=True)
        image = Upload(required=False)

    message_notification = graphene.Field(MessageNotificationType)

    def mutate(root, info, image=None, message_notification_data=None):
        creator = info.context.user
        establishment_ids = message_notification_data.pop("establishments")
        message_notification = MessageNotification(**message_notification_data)
        message_notification.creator = creator
        message_notification.company = (
            creator.current_company
            if creator.current_company is not None
            else creator.company
        )
        if info.context.FILES:
            # file1 = info.context.FILES['1']
            if image and isinstance(image, UploadedFile):
                image_file = message_notification.image
                if not image_file:
                    image_file = File()
                    image_file.creator = creator
                image_file.image = image
                image_file.save()
                message_notification.image = image_file
        message_notification.save()

        establishments = Establishment.objects.filter(id__in=establishment_ids)
        for establishment in establishments:
            try:
                message_notification_establishment = MessageNotificationEstablishment.objects.get(establishment__id=establishment.id, message_notification__id=message_notification.id)
            except MessageNotificationEstablishment.DoesNotExist:
                MessageNotificationEstablishment.objects.create(
                        message_notification=message_notification,
                        establishment=establishment,
                        creator=creator
                    )
        return CreateMessageNotification(message_notification=message_notification)


class UpdateMessageNotification(graphene.Mutation):
    class Arguments:
        id = graphene.ID()
        message_notification_data = MessageNotificationInput(required=True)
        image = Upload(required=False)

    message_notification = graphene.Field(MessageNotificationType)

    def mutate(root, info, id, image=None, message_notification_data=None):
        creator = info.context.user
        establishment_ids = message_notification_data.pop("establishments")
        MessageNotification.objects.filter(pk=id).update(**message_notification_data)
        MessageNotificationUserStatus.objects.filter(message_notification__id=id).update(is_read=False)
        message_notification = MessageNotification.objects.get(pk=id)
        if not image and message_notification.image:
            image_file = message_notification.image
            image_file.delete()
        if info.context.FILES:
            # file1 = info.context.FILES['1']
            if image and isinstance(image, UploadedFile):
                image_file = message_notification.image
                if not image_file:
                    image_file = File()
                    image_file.creator = creator
                image_file.image = image
                image_file.save()
                message_notification.image = image_file
            message_notification.save()

        MessageNotificationEstablishment.objects.filter(message_notification=message_notification).exclude(establishment__id__in=establishment_ids).delete()
        establishments = Establishment.objects.filter(id__in=establishment_ids)
        for establishment in establishments:
            try:
                message_notification_establishment = MessageNotificationEstablishment.objects.get(establishment__id=establishment.id, message_notification__id=message_notification.id)
            except MessageNotificationEstablishment.DoesNotExist:
                MessageNotificationEstablishment.objects.create(
                        message_notification=message_notification,
                        establishment=establishment,
                        creator=creator
                    )
        return UpdateMessageNotification(message_notification=message_notification)


class UpdateMessageNotificationState(graphene.Mutation):
    class Arguments:
        id = graphene.ID()

    message_notification = graphene.Field(MessageNotificationType)
    done = graphene.Boolean()
    success = graphene.Boolean()
    message = graphene.String()

    def mutate(root, info, id, message_notification_fields=None):
        creator = info.context.user
        done = True
        success = True
        message_notification = None
        message = ""
        try:
            message_notification = MessageNotification.objects.get(pk=id)
            MessageNotification.objects.filter(pk=id).update(
                is_active=not message_notification.is_active
            )
            message_notification.refresh_from_db()
        except Exception as e:
            done = False
            success = False
            message_notification = None
            message = "Une erreur s'est produite."
        return UpdateMessageNotificationState(
            done=done, success=success, message=message, message_notification=message_notification
        )

class MarkMessageNotificationsAsRead(graphene.Mutation):
    class Arguments:
        ids = graphene.List(graphene.ID)
        is_read = graphene.Boolean(required=False)
    
    done = graphene.Boolean()
    success = graphene.Boolean()
    message = graphene.String()

    def mutate(root, info, ids, is_read=None):
        user = info.context.user
        done = True
        success = True
        message = ''
        try:
            message_notifications = MessageNotification.objects.filter(id__in=ids)
            for message_notification in message_notifications:
                notification_status, created = MessageNotificationUserStatus.objects.get_or_create(
                    user=user,
                    message_notification=message_notification
                    )
                notification_status.is_read = True
                notification_status.save()
            not_read_count = MessageNotification.objects.filter(is_read=False).count()
            # broadcastMessageNotificationsRead(not_read_count=not_read_count)
        except Exception as e:
            done = False
            success = False
            message = "Une erreur s'est produite."
        return MarkMessageNotificationsAsRead(done=done, success=success, message=message)


class DeleteMessageNotification(graphene.Mutation):
    class Arguments:
        id = graphene.ID()

    message_notification = graphene.Field(MessageNotificationType)
    id = graphene.ID()
    deleted = graphene.Boolean()
    success = graphene.Boolean()
    message = graphene.String()

    def mutate(root, info, id):
        deleted = False
        success = False
        message = ""
        current_user = info.context.user
        if current_user.is_superuser:
            message_notification = MessageNotification.objects.get(pk=id)
            message_notification.delete()
            deleted = True
            success = True
        else:
            message = "Vous n'êtes pas un Superuser."
        return DeleteMessageNotification(
            deleted=deleted, success=success, message=message, id=id
        )


# *************************************************************************#

class NotificationsMutation(graphene.ObjectType):
    update_notification = UpdateNotification.Field()
    mark_notifications_as_seen = MarkNotificationsAsSeen.Field()
    delete_notification = DeleteNotification.Field()

    create_message_notification = CreateMessageNotification.Field()
    update_message_notification = UpdateMessageNotification.Field()
    update_message_notification_state = UpdateMessageNotificationState.Field()
    mark_message_notifications_as_read = MarkMessageNotificationsAsRead.Field()
    delete_message_notification = DeleteMessageNotification.Field()

#**************************************Subscription**********************************

class OnNotificationAdded(channels_graphql_ws.Subscription):
    """Simple GraphQL subscription."""

    # Leave only latest 64 messages in the server queue.
    notification_queue_limit = 64

    # Subscription payload.
    notification = graphene.Field(NotificationType)

    class Arguments:
        """That is how subscription arguments are defined."""
        # arg1 = graphene.String()
        # arg2 = graphene.String()

    @staticmethod
    def subscribe(root, info):
        """Called when user subscribes."""

        # Return the list of subscription group names.
        return ["ON_NOTIF_ADDED"]

    @staticmethod
    def publish(payload, info):
        """Called to notify the client."""
        #print('send -*******************')
        #print(payload)
        # Here `payload` contains the `payload` from the `broadcast()`
        # invocation (see below). You can return `MySubscription.SKIP`
        # if you wish to suppress the notification to a particular
        # client. For example, this allows to avoid notifications for
        # the actions made by this particular client.
        user = info.context.user
        if str(user.id) != str(payload.recipient.id):
            return OnNotificationAdded.SKIP
        return OnNotificationAdded(notification=payload)


class OnNotificationsSeen(channels_graphql_ws.Subscription):
    """Simple GraphQL subscription."""

    # Leave only latest 64 messages in the server queue.
    notification_queue_limit = 64

    # Subscription payload.
    total_count = graphene.Int()
    not_seen_count = graphene.Int()

    class Arguments:
        """That is how subscription arguments are defined."""
        # arg1 = graphene.String()
        # arg2 = graphene.String()

    @staticmethod
    def subscribe(root, info):
        """Called when user subscribes."""

        # Return the list of subscription group names.
        return ["ON_NOTIFS_SEEN"]

    @staticmethod
    def publish(payload, info):
        """Called to notify the client."""
        #print('send -*******************')
        #print(payload)
        # Here `payload` contains the `payload` from the `broadcast()`
        # invocation (see below). You can return `MySubscription.SKIP`
        # if you wish to suppress the notification to a particular
        # client. For example, this allows to avoid notifications for
        # the actions made by this particular client.
        return OnNotificationsSeen(not_seen_count=payload['not_seen_count'])

#**************************************Subscription**********************************

class OnMessageNotificationAdded(channels_graphql_ws.Subscription):
    """Simple GraphQL subscription."""

    # Leave only latest 64 messages in the server queue.
    message_notification_queue_limit = 64

    # Subscription payload.
    message_notification = graphene.Field(MessageNotificationType)

    class Arguments:
        """That is how subscription arguments are defined."""
        # arg1 = graphene.String()
        # arg2 = graphene.String()

    @staticmethod
    def subscribe(root, info):
        """Called when user subscribes."""

        # Return the list of subscription group names.
        return ["ON_MSG_NOTIF_ADDED"]

    @staticmethod
    def publish(payload, info):
        """Called to notify the client."""
        #print('send -*******************')
        #print(payload)
        # Here `payload` contains the `payload` from the `broadcast()`
        # invocation (see below). You can return `MySubscription.SKIP`
        # if you wish to suppress the message_notification to a particular
        # client. For example, this allows to avoid message_notifications for
        # the actions made by this particular client.
        return OnMessageNotificationAdded(message_notification=payload)


class OnMessageNotificationsRead(channels_graphql_ws.Subscription):
    """Simple GraphQL subscription."""

    # Leave only latest 64 messages in the server queue.
    message_notification_queue_limit = 64

    # Subscription payload.
    total_count = graphene.Int()
    not_read_count = graphene.Int()

    class Arguments:
        """That is how subscription arguments are defined."""
        # arg1 = graphene.String()
        # arg2 = graphene.String()

    @staticmethod
    def subscribe(root, info):
        """Called when user subscribes."""

        # Return the list of subscription group names.
        return ["ON_MSG_NOTIFS_READ"]

    @staticmethod
    def publish(payload, info):
        """Called to notify the client."""
        #print('send -*******************')
        #print(payload)
        # Here `payload` contains the `payload` from the `broadcast()`
        # invocation (see below). You can return `MySubscription.SKIP`
        # if you wish to suppress the message_notification to a particular
        # client. For example, this allows to avoid message_notifications for
        # the actions made by this particular client.
        return OnMessageNotificationsRead(not_read_count=payload['not_read_count'])

#***********************************************************************************

class NotificationsSubscription(graphene.ObjectType):
    on_notification_added = OnNotificationAdded.Field()
    on_notifications_seen = OnNotificationsSeen.Field()

    on_message_notification_added = OnMessageNotificationAdded.Field()
    on_message_notifications_read = OnMessageNotificationsRead.Field()
