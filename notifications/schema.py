import graphene
import channels_graphql_ws
from graphene_django import DjangoObjectType
from graphql_jwt.decorators import login_required

from notifications.models import Notification
from notifications.notificator import broadcastNotificationsSeen

#************************************ObjectType************************************

class NotificationType(DjangoObjectType):
    class Meta:
        model = Notification
        fields = "__all__"

class NotificationNodeType(graphene.ObjectType):
    nodes = graphene.List(NotificationType)
    total_count = graphene.Int()
    not_seen_count = graphene.Int()

#************************************InputObjectType************************************

class NotificationInput(graphene.InputObjectType):
    id = graphene.ID(required=False)
    is_read = graphene.Boolean(required=False)
    is_seen = graphene.Boolean(required=False)

#************************************Mutation************************************

class NotificationsQuery(graphene.ObjectType):
    notifications = graphene.Field(NotificationNodeType, offset = graphene.Int(required=False), limit = graphene.Int(required=False), page = graphene.Int(required=False))
    notification = graphene.Field(NotificationType, id = graphene.ID())

    def resolve_notifications(root, info, offset=None, limit=None, page=None):
        # We can easily optimize query count in the resolve method
        total_count = 0
        not_seen_count = 0
        total_count = Notification.objects.all().count()
        not_seen_count = Notification.objects.filter(is_seen=False).count()
        if page:
            offset = limit*(page-1)
        if offset is not None and limit is not None:
            notifications = Notification.objects.all()[offset:offset+limit]
        else:
            notifications = Notification.objects.all()
        return NotificationNodeType(nodes=notifications, total_count=total_count, not_seen_count=not_seen_count)

    def resolve_notification(root, info, id):
        # We can easily optimize query count in the resolve method
        try:
            notification = Notification.objects.get(pk=id)
        except Notification.DoesNotExist:
            notification = None
        return notification

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
            Notification.objects.filter(id__in=ids).update(is_seen=True)
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

class NotificationsMutation(graphene.ObjectType):
    update_notification = UpdateNotification.Field()
    mark_notifications_as_seen = MarkNotificationsAsSeen.Field()
    delete_notification = DeleteNotification.Field()

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

class NotificationsSubscription(graphene.ObjectType):
    on_notification_added = OnNotificationAdded.Field()
    on_notifications_seen = OnNotificationsSeen.Field()
