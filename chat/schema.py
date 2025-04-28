import graphene
import channels_graphql_ws
from graphene_django import DjangoObjectType
from django.core.files.uploadedfile import InMemoryUploadedFile, UploadedFile
from graphql_jwt.decorators import login_required
from graphene_file_upload.scalars import Upload

from django.db.models import Q

from chat.models import Conversation, ParticipantConversation, Message
from chat.broadcaster import broadcastMessageAdded
from notifications.notificator import push_notification_chat_participants

class MessageType(DjangoObjectType):
    class Meta:
        model = Message
        fields = "__all__"
    is_sent_by_me = graphene.Boolean()
    def resolve_is_sent_by_me( instance, info, **kwargs ):
        #print(f'info.context.user.id : {info.context.user}')
        return instance.sender.id == info.context.user.id

class MessageNodeType(graphene.ObjectType):
    nodes = graphene.List(MessageType)
    total_count = graphene.Int()

class ConversationType(DjangoObjectType):
    class Meta:
        model = Conversation
        fields = "__all__"
    last_message = graphene.Field(MessageType)
    not_seen_count = graphene.Int()
    def resolve_last_message( instance, info, **kwargs ):
        return instance.messages.all().first()
    def resolve_not_seen_count( instance, info, **kwargs ):
        return instance.messages.filter(is_seen=False).count()

class ConversationNodeType(graphene.ObjectType):
    nodes = graphene.List(ConversationType)
    total_count = graphene.Int()
    not_seen_count = graphene.Int()

class ParticipantConversationType(DjangoObjectType):
    class Meta:
        model = ParticipantConversation
        fields = "__all__"

class ParticipantConversationNodeType(graphene.ObjectType):
    nodes = graphene.List(ParticipantConversationType)
    total_count = graphene.Int()

class MessageInput(graphene.InputObjectType):
    id = graphene.ID(required=False)
    text = graphene.String(required=False)
    conversation_id = graphene.Int(name="conversation", required=False)
    recipient_id = graphene.Int(name="recipient", required=False)

class ConversationInput(graphene.InputObjectType):
    id = graphene.ID(required=False)
    name = graphene.String(required=False)

class ChatQuery(graphene.ObjectType):
    conversations = graphene.Field(ConversationNodeType, offset = graphene.Int(required=False), limit = graphene.Int(required=False), page = graphene.Int(required=False))
    conversation = graphene.Field(ConversationType, id = graphene.ID())
    messages = graphene.Field(MessageNodeType, conversation_id = graphene.ID(required=False), participant_id = graphene.ID(required=False), offset = graphene.Int(required=False), limit = graphene.Int(required=False), page = graphene.Int(required=False))
    message = graphene.Field(MessageType, id = graphene.ID())

    def resolve_messages(root, info, conversation_id=None, participant_id=None, offset=None, limit=None, page=None):
        # We can easily optimize query count in the resolve method
        user = info.context.user
        total_count = 0
        try:
            if not conversation_id or conversation_id is None:
                conversation = Conversation.objects.filter(
                    participants__user__id=user.id
                ).filter(
                    participants__user__id=participant_id
                ).first()
                if conversation:
                    conversation_id = conversation.id
                else:
                    return MessageNodeType(nodes=[], total_count=total_count)

            Message.objects.filter(~Q(sender__id=user.id), conversation__id=conversation_id).update(is_seen=True)        
            total_count = Message.objects.filter(conversation__id=conversation_id).count()
            if page:
                offset = limit*(page-1)
            if offset is not None and limit is not None:
                messages = Message.objects.filter(conversation__id=conversation_id)[offset:offset+limit]
            else:
                messages = Message.objects.filter(conversation__id=conversation_id)
        except Exception as e:
            print(f'Exception resolve_messages : {e}')
        return MessageNodeType(nodes=reversed(messages), total_count=total_count)

    def resolve_message(root, info, id):
        # We can easily optimize query count in the resolve method
        try:
            message = Message.objects.get(pk=id)
        except Message.DoesNotExist:
            message = None
        return message

    def resolve_conversations(root, info, offset=None, limit=None, page=None):
        # We can easily optimize query count in the resolve method
        user = info.context.user
        total_count = 0
        not_seen_count = 0
        total_count = Conversation.objects.filter(participants__user__id=user.id).count()
        not_seen_count = Message.objects.filter(~Q(sender__id=user.id), conversation__participants__user__id=user.id, is_seen=False).count()
        if page:
            offset = limit*(page-1)
        if offset is not None and limit is not None:
            conversations = Conversation.objects.filter(participants__user__id=user.id)[offset:offset+limit]
        else:
            conversations = Conversation.objects.filter(participants__user__id=user.id)
        return ConversationNodeType(nodes=conversations, total_count=total_count, not_seen_count=not_seen_count)

    def resolve_conversation(root, info, id):
        # We can easily optimize query count in the resolve method
        try:
            conversation = Conversation.objects.get(pk=id)
        except Conversation.DoesNotExist:
            conversation = None
        return conversation

#************************************************************************

class CreateConversation(graphene.Mutation):
    class Arguments:
        conversation_data = ConversationInput(required=True)
        conversation_id = graphene.ID(required=False)

    conversation = graphene.Field(ConversationType)
    done = graphene.Boolean()
    success = graphene.Boolean()
    conversation_response = graphene.String()

    def mutate(root, info, conversation_id=None, conversation_data=None):
        creator = info.context.user
        done = True
        success = True
        message = ''
        try:
            conversation = Conversation(**conversation_data)
            conversation.creator = creator
            conversation.save()
        except Exception as e:
            done = False
            success = False
            message = "Une erreur s'est produite."
        return CreateConversation(done=done, success=success, message=message, conversation=conversation)

class UpdateConversation(graphene.Mutation):
    class Arguments:
        id = graphene.ID()
        conversation_data = ConversationInput(required=True)

    conversation = graphene.Field(ConversationType)
    done = graphene.Boolean()
    success = graphene.Boolean()
    message = graphene.String()

    def mutate(root, info, id, image=None, conversation_data=None):
        creator = info.context.user
        done = True
        success = True
        message = ''
        try:
            Conversation.objects.filter(pk=id).update(**conversation_data)
        except Exception as e:
            done = False
            success = False
            message = "Une erreur s'est produite."
        return UpdateConversation(done=done, success=success, message=message, conversation=conversation)


class DeleteConversation(graphene.Mutation):
    class Arguments:
        id = graphene.ID()

    conversation = graphene.Field(ConversationType)
    id = graphene.ID()
    deleted = graphene.Boolean()
    success = graphene.Boolean()
    message = graphene.String()

    def mutate(root, info, id):
        deleted = False
        success = False
        message = ''
        current_user = info.context.user
        conversation = Conversation.objects.get(pk=id)
        if current_user.is_superuser or conversation.creator==current_user:
            conversation.delete()
            deleted = True
            success = True
        else:
            message = "Oups ! Vous n'avez pas les droits pour supprimer cet élément."
        return DeleteConversation(deleted=deleted, success=success, message=message, id=id)

#************************************************************************

class CreateMessage(graphene.Mutation):
    class Arguments:
        message_data = MessageInput(required=True)
        conversation_id = graphene.ID(required=False)

    message = graphene.Field(MessageType)
    done = graphene.Boolean()
    success = graphene.Boolean()
    message_response = graphene.String()

    def mutate(root, info, conversation_id=None, message_data=None):
        user = info.context.user
        done = True
        success = True
        conversation = None
        message = None
        message_response = ''
        if not conversation_id or conversation_id is None:
            if 'conversation_id' in message_data:
                conversation_id = message_data.pop("conversation_id")
                try:
                    conversation = Conversation.objects.get(pk=conversation_id)
                except Exception as e:
                    conversation = None
            if not conversation or conversation is None and 'recipient_id' in message_data:
                recipient_id = message_data.pop("recipient_id")
                try:
                    # Vérifier si la conversation existe déjà
                    conversation = Conversation.objects.filter(
                        participants__user__id=user.id
                    ).filter(
                        participants__user__id=recipient_id
                    ).first()

                    # Si la conversation n'existe pas, la créer
                    if not conversation or conversation is None:
                        conversation = Conversation.objects.create(creator=user)

                        # Ajouter les participants à la conversation
                        ParticipantConversation.objects.create(conversation=conversation, user=user)
                        ParticipantConversation.objects.create(conversation=conversation, user_id=recipient_id)

                except Exception as e:
                    conversation = None
                    print(f'Exception***** : {e}')
                    done = False
                    success = False
                    message_response = "Une exception s'est produite lors de la création de la conversation."
        try:
            if conversation:
                message = Message.objects.create(
                    conversation=conversation,
                    sender=user, text=message_data.text
                )
                if message:
                    broadcastMessageAdded(message=message)
                    push_notification_chat_participants(message=message)
            else:
                done = False
                success = False
                message_response = "Une erreur s'est produite lors de la création de la conversation."
        except Exception as e:
            done = False
            success = False
            message_response = "Une erreur s'est produite."
        return CreateMessage(done=done, success=success, message_response=message_response, message=message)

class UpdateMessage(graphene.Mutation):
    class Arguments:
        id = graphene.ID()
        message_data = MessageInput(required=True)

    message = graphene.Field(MessageType)
    done = graphene.Boolean()
    success = graphene.Boolean()
    message_response = graphene.String()

    def mutate(root, info, id, image=None, message_data=None):
        creator = info.context.user
        done = True
        success = True
        message_response = ''
        try:
            Message.objects.filter(pk=id).update(**message_data)
        except Exception as e:
            done = False
            success = False
            message_response = "Une erreur s'est produite."
        return UpdateMessage(done=done, success=success, message_response=message_response, message=message)


class DeleteMessage(graphene.Mutation):
    class Arguments:
        id = graphene.ID()

    message = graphene.Field(MessageType)
    id = graphene.ID()
    deleted = graphene.Boolean()
    success = graphene.Boolean()
    message_response = graphene.String()

    def mutate(root, info, id):
        deleted = False
        success = False
        message_response = ''
        current_user = info.context.user
        message = Message.objects.get(pk=id)
        if current_user.is_superuser or message.creator==current_user:
            message.delete()
            deleted = True
            success = True
        else:
            message_response = "Vous n'êtes pas un Superuser."
        return DeleteMessage(deleted=deleted, success=success, message_response=message_response, id=id)

#*************************************************************************#
class ChatMutation(graphene.ObjectType):
    create_conversation = CreateConversation.Field()
    update_conversation = UpdateConversation.Field()
    delete_conversation = DeleteConversation.Field()

    create_message = CreateMessage.Field()
    update_message = UpdateMessage.Field()
    delete_message = DeleteMessage.Field()

#**************************************Subscription**********************************

class OnMessageAdded(channels_graphql_ws.Subscription):
    """Simple GraphQL subscription."""

    # Leave only latest 64 messages in the server queue.
    notification_queue_limit = 64

    # Subscription payload.
    message = graphene.Field(MessageType)

    class Arguments:
        """That is how subscription arguments are defined."""
        conversation_id = graphene.ID(required=True)
        # arg1 = graphene.String()
        # arg2 = graphene.String()

    @staticmethod
    def subscribe(root, info,conversation_id):
        """Called when user subscribes."""

        # Return the list of subscription group names.
        return ["ON_MESSAGE_ADDED"]

    @staticmethod
    def publish(payload, info, conversation_id):
        """Called to notify the client."""
        #print(payload)
        # Here `payload` contains the `payload` from the `broadcast()`
        # invocation (see below). You can return `MySubscription.SKIP`
        # if you wish to suppress the notification to a particular
        # client. For example, this allows to avoid notifications for
        # the actions made by this particular client.
        if str(conversation_id) != str(payload['message'].conversation.id):
            return OnMessageAdded.SKIP
        return OnMessageAdded(message=payload['message'])



class ChatSubscription(graphene.ObjectType):
    on_message_added = OnMessageAdded.Field()